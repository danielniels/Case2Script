"""
Session, SessionManager, ReportStore, ScriptStore + script generation.
Depends on: helpers.py (for _js — used by the disabled JS generator, kept for reference).
Playwright script output is Python-only via generate_playwright_py_from_json.
"""

import asyncio
import base64
import json
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from playwright.async_api import Browser, BrowserContext, Page

from helpers import _js


# ==================== Session TTL config ====================

_SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))
_SESSION_REAPER_INTERVAL = int(os.getenv("SESSION_REAPER_INTERVAL", "60"))


# ==================== Session ====================

class Session:
    def __init__(self, browser: Browser, context: BrowserContext, page: Page):
        self.browser = browser
        self.context = context
        self.page = page
        self.lock = asyncio.Lock()
        self.command_history: list = []
        self.last_used: float = asyncio.get_event_loop().time()

    def touch(self):
        self.last_used = asyncio.get_event_loop().time()


# ==================== Session Manager ====================

class SessionManager:
    """Thread-safe registry of browser sessions. One browser per sessionId."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()
        self._reaper_task: Optional[asyncio.Task] = None

    def start_reaper(self):
        self._reaper_task = asyncio.create_task(self._reaper_loop())

    async def stop_reaper(self):
        if self._reaper_task:
            self._reaper_task.cancel()
            try:
                await self._reaper_task
            except asyncio.CancelledError:
                pass

    async def _reaper_loop(self):
        while True:
            await asyncio.sleep(_SESSION_REAPER_INTERVAL)
            await self._evict_idle()

    async def _evict_idle(self):
        now = asyncio.get_event_loop().time()
        async with self._lock:
            expired = [
                sid for sid, sess in self._sessions.items()
                if (now - sess.last_used) > _SESSION_TTL_SECONDS
            ]
        for sid in expired:
            print(f"[Session] TTL expired, closing idle session: {sid}")
            await self.close(sid)

    async def get_or_create(self, session_id: str, pw) -> Session:
        async with self._lock:
            if session_id in self._sessions:
                sess = self._sessions[session_id]
                sess.touch()
                return sess

        _headless = os.getenv("HEADLESS", "false").lower() not in ("false", "0", "no")
        browser = await pw.chromium.launch(headless=_headless)
        context = await browser.new_context(
            bypass_csp=True,
            ignore_https_errors=True,
        )
        page = await context.new_page()
        new_sess = Session(browser, context, page)

        async with self._lock:
            if session_id in self._sessions:
                await context.close()
                await browser.close()
                sess = self._sessions[session_id]
            else:
                self._sessions[session_id] = new_sess
                sess = new_sess
                print(f"[Session] Created: {session_id} (headless={_headless})")

        sess.touch()
        return sess

    async def close(self, session_id: str):
        async with self._lock:
            if session_id in self._sessions:
                sess = self._sessions.pop(session_id)
                try:
                    await sess.context.close()
                except Exception:
                    pass
                try:
                    await sess.browser.close()
                except Exception:
                    pass
                print(f"[Session] Closed: {session_id}")

    def active_sessions(self) -> int:
        return len(self._sessions)

    def get(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)


# ==================== Report Store ====================

class ReportStore:
    """Per-test-case report state with an asyncio.Lock."""

    def __init__(self):
        self._reports: Dict[str, dict] = {}
        self._commands: Dict[str, list] = {}
        self._run_counter: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def init_report(self, test_case_id: str, test_case_name: str = None,
                           test_suite_id: str = None):
        async with self._lock:
            self._run_counter[test_case_id] = self._run_counter.get(test_case_id, 0) + 1
            run_number = self._run_counter[test_case_id]
            ts = datetime.now().strftime("%d%m%Y_%H%M%S")
            self._reports[test_case_id] = {
                "test_case_id": test_case_id,
                "test_case_name": test_case_name or test_case_id,
                "test_suite_id": test_suite_id or "",
                "run_timestamp": ts,
                "run_number": run_number,
                "test_step": [],
            }
            self._commands[test_case_id] = []

    async def add_step(self, test_case_id: str, step_data: dict):
        async with self._lock:
            if test_case_id in self._reports:
                self._reports[test_case_id]["test_step"].append(step_data)

    async def get_report(self, test_case_id: str) -> Optional[dict]:
        async with self._lock:
            return self._reports.get(test_case_id)

    async def get_run_timestamp(self, test_case_id: str) -> str:
        async with self._lock:
            return (self._reports.get(test_case_id) or {}).get("run_timestamp", "")

    async def pop_report(self, test_case_id: str) -> Optional[dict]:
        async with self._lock:
            return self._reports.pop(test_case_id, None)

    async def append_command(self, test_case_id: str, cmd: dict):
        async with self._lock:
            if test_case_id not in self._commands:
                self._commands[test_case_id] = []
            self._commands[test_case_id].append(cmd)

    async def get_commands(self, test_case_id: str) -> list:
        async with self._lock:
            return list(self._commands.get(test_case_id, []))


# # ==================== Script Store JS Templates ====================

# _JS_TEMPLATES = {
#     "navigate": lambda p: (
#         f"await page.goto({_js(p.get('url',''))}, {{ waitUntil: 'domcontentloaded' }});\n"
#         f"    await page.waitForLoadState('load').catch(() => {{}});\n"
#         f"    await page.waitForLoadState('networkidle').catch(() => {{}});"
#     ),

#     "click": lambda p: (
#         f"await page.evaluate((sel) => {{\n"
#         f"      let el;\n"
#         f"      const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;\n"
#         f"      if (xsel.startsWith('//')) {{\n"
#         f"          const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);\n"
#         f"          el = r.singleNodeValue;\n"
#         f"      }} else {{\n"
#         f"          el = document.querySelector(xsel);\n"
#         f"      }}\n"
#         f"      if (el) el.click();\n"
#         f"  }}, {_js(p.get('selector',''))}).catch(() => {{}});\n"
#         f"    await page.waitForLoadState('load').catch(() => {{}});\n"
#         f"    await page.waitForLoadState('networkidle').catch(() => {{}});\n"
#         f"    await page.waitForTimeout(800);"
#     ),

#     "click_at_position": lambda p: "\n    ".join([
#         f"await page.locator({_js(p.get('selector', '.mapwrap svg'))}).first().click({{ position: {{ x: {c['x']}, y: {c['y']} }} }});\n    await page.waitForTimeout(300);"
#         for c in (p.get('clicks') or [{"x": p.get('x', 0), "y": p.get('y', 0)}])
#     ]),

#     "fill": lambda p:
#         f"await page.locator({_js(p.get('selector',''))}).first().fill({_js(p.get('text',''))});",

#     "select_option": lambda p: (
#         f"await page.evaluate(({{sel, val}}) => {{\n"
#         f"  let el;\n"
#         f"  if (sel.startsWith('//') || sel.startsWith('xpath=')) {{\n"
#         f"    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;\n"
#         f"  }} else {{\n"
#         f"    el = document.querySelector(sel);\n"
#         f"  }}\n"
#         f"  if (!el) return false;\n"
#         f"  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);\n"
#         f"  if (!opt) return false;\n"
#         f"  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');\n"
#         f"  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);\n"
#         f"  else el.value = opt.value;\n"
#         f"  el.dispatchEvent(new Event('change', {{ bubbles: true }}));\n"
#         f"  el.dispatchEvent(new Event('input', {{ bubbles: true }}));\n"
#         f"  return true;\n"
#         f"}}, {{ sel: {_js(p.get('selector',''))}, val: {_js(p.get('value',''))} }});"
#     ),

#     "press_key": lambda p: (
#         f"await page.keyboard.press({_js(p.get('key','Escape'))});"
#         f"await page.waitForTimeout(1000);"
#     ),

#     "screenshot": lambda p:
#         f"await page.screenshot({{ path: {_js(p.get('path','screenshot.png'))} }});",

#     "wait_for_load": lambda p:
#         f"await page.waitForLoadState({_js(p.get('state','load'))});",

#     "wait_for_selector": lambda p:
#         f"await page.waitForSelector({_js(p.get('selector',''))}, {{ state: {_js(p.get('state','visible'))} }});",

#     "hover": lambda p:
#         f"await page.locator({_js(p.get('selector',''))}).first().hover();",

#     "double_click": lambda p:
#         f"await page.dblclick({_js(p.get('selector',''))});",

#     "scroll_to_element": lambda p:
#         f"await page.locator({_js(p.get('selector',''))}).scrollIntoViewIfNeeded();",

#     "clear_input": lambda p:
#         f"await page.fill({_js(p.get('selector',''))}, '');",

#     "upload_file": lambda p:
#         f"await page.setInputFiles({_js(p.get('selector',''))}, {__import__('json').dumps(p.get('files',[]) if isinstance(p.get('files'), list) else [p.get('files','')])});",

#     "assert_text": lambda p: (
#         '{ const t = (await page.locator(' + _js(p["selector"]) + ').first().innerText()).trim(); '
#         'if (!t.includes(' + _js(p["expected"]) + ')) '
#         'throw new Error("assert_text failed — expected " + ' + _js(p["expected"]) + ' + ", got: " + t); }'
#     ),
#     "assert_visible": lambda p: (
#         'if (!await page.locator(' + _js(p["selector"]) + ').first().isVisible()) '
#         'throw new Error("assert_visible failed: " + ' + _js(p["selector"]) + ');'
#     ),
#     "assert_not_visible": lambda p: (
#         '{ const c = await page.locator(' + _js(p["selector"]) + ').count(); '
#         'if (c > 0 && await page.locator(' + _js(p["selector"]) + ').first().isVisible()) '
#         'throw new Error("assert_not_visible failed, element visible: " + ' + _js(p["selector"]) + '); }'
#     ),
#     "assert_disabled": lambda p: (
#         'if (!await page.locator(' + _js(p["selector"]) + ').first().isDisabled()) '
#         'throw new Error("assert_disabled failed, element enabled: " + ' + _js(p["selector"]) + ');'
#     ),
    # "assert_url": lambda p: (
    #     'try { await page.waitForURL("**/*' + p["expected"] + '*", { timeout: ' + str(p.get("timeout", 8000)) + ' }); } catch (e) {}\n'
    #     '    if (!page.url().includes(' + _js(p["expected"]) + ')) '
    #     'throw new Error("assert_url failed — got: " + page.url());'
    # ),
#     "assert_toast": lambda p: (
#         '{ const _exp = ' + _js(p.get("expected_text", "")) + '; '
#         'const _to = ' + str(int(p.get("timeout", 6000))) + '; '
#         'const _all = [...document.querySelectorAll('
#         '"[role=alert],[role=status],[class*=toast],[class*=swal2],[class*=alert],[class*=snackbar],[class*=notyf]"'
#         ')].filter(e => { const s = window.getComputedStyle(e); return s.display !== "none" && s.visibility !== "hidden" && e.offsetParent !== null; }); '
#         'const _t = _all.map(e => (e.innerText || e.textContent || "").trim()).join(" "); '
#         'if (_exp && !_t.toLowerCase().includes(_exp.toLowerCase())) '
#         'throw new Error("assert_toast failed — expected: " + _exp + ", got: " + _t); '
#         'if (!_exp && !_all.length) throw new Error("assert_toast failed — no notification visible"); }'
#     ),
#     "execute_js": lambda p:
#         f"await page.evaluate({_js(p.get('script', ''))});",
# }

# _JS_SKIP = {
#     "get_interactable_elements", "get_page_content", "get_page_info",
#     "get_page_content_and_save_csv", "get_page_content_and_save_txt",
#     "get_credentials", "close_session",
# }


# def _method_to_js(method: str, params: dict) -> Optional[str]:
#     """Convert one MCP step → Playwright JS statement."""
#     handler = _JS_TEMPLATES.get(method)
#     if not handler:
#         return None
#     try:
#         return handler(params)
#     except Exception:
#         return None


# # ==================== Playwright Script Generator (JS) — DISABLED ====================
# # Full Node.js/Playwright generator. Disabled in favor of the Python generator
# # below (generate_playwright_py_from_json). Kept here, commented, in case the
# # JS output path needs to come back.

# def generate_playwright_from_json(json_path: str) -> Optional[str]:
#     """
#     Read a saved MCP script JSON and generate a standalone Node.js Playwright script.
#     Source of truth = the .json file. Output: data/saved_playwright_scripts/<stem>.js
#     """
#     try:
#         with open(json_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#     except Exception as e:
#         print(f"[Playwright Generator] Cannot read {json_path}: {e}")
#         return None

#     steps = data.get("steps", []) if isinstance(data, dict) else data
#     if not steps:
#         print(f"[Playwright Generator] No steps in {json_path}")
#         return None

#     stem = Path(json_path).stem
#     pw_dir = Path("data/saved_playwright_scripts")
#     pw_dir.mkdir(parents=True, exist_ok=True)
#     js_path = str(pw_dir / f"{stem}.js")

#     lines = [
#         f"// Auto-generated Playwright script — {stem}",
#         f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
#         f"// Source: {Path(json_path).name}",
#         f"// Run: node {stem}.js",
#         "// Requires: npm install playwright && npx playwright install chromium",
#         "",
#         "const { chromium } = require('playwright');",
#         "const { mkdirSync } = require('fs');",
#         "",
#         f"mkdirSync('data/saved_playwright_scripts/screenshots/{stem}', {{ recursive: true }});",
#         "",
#         "async function runTest() {",
#         "  const browser = await chromium.launch({ headless: false });",
#         "  const context = await browser.newContext({ ignoreHTTPSErrors: true });",
#         "  const page = await context.newPage();",
#         "",
#         "  try {",
#     ]

#     for step in steps:
#         method  = step.get("method", "")
#         params  = {k: v for k, v in step.get("params", {}).items() if k != "sessionId"}
#         desc    = step.get("step", "")
#         status  = step.get("status", "passed")
#         step_id = step.get("id", "?")

#         params = dict(params)
#         resolved = params.get("resolved_selector", "")
#         if resolved and ("[" in resolved or "@" in resolved or "#" in resolved):
#             params["selector"] = resolved
#         elif params.get("selector"):
#             params["selector"] = re.sub(r'\s+\d+(")\]$', r'\1]', params["selector"])

#         lines.append("")

#         if method in _JS_SKIP:
#             lines.append(f"    // [Step {step_id}] {desc} [{method}] — MCP-only, skipped")
#             continue

#         if status == "failed":
#             lines.append(f"    // STEP {step_id} FAILED [{method}] — fix manually before running")
#             lines.append(f"    // {desc}")
#             js_line = _method_to_js(method, params)
#             if js_line:
#                 lines.append(f"    // {js_line}")
#             continue

#         lines.append(f"    // Step {step_id}: {desc}")
#         lines.append(f"    console.log('▶ STEP {step_id}');")

#         if method == "screenshot":
#             ss_path = f"data/saved_playwright_scripts/screenshots/{stem}/step_{step_id}.png"
#             lines.append(f"    await page.screenshot({{ path: {_js(ss_path)} }});")
#             continue

#         js_line = _method_to_js(method, params)
#         if js_line:
#             lines.append(f"    {js_line}")
#             ss_auto = f"data/saved_playwright_scripts/screenshots/{stem}/step_{step_id}.png"
#             lines.append(f"    await page.screenshot({{ path: {_js(ss_auto)} }});")

#     lines += [
#         "",
#         "    console.log('Test completed');",
#         "  } catch (err) {",
#         "    console.error('Test failed:', err.message);",
#         "    process.exit(1);",
#         "  } finally {",
#         "    await browser.close();",
#         "  }",
#         "}",
#         "",
#         "runTest();",
#     ]

#     with open(js_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(lines))

#     print(f"[Playwright Generator] Script generated: {js_path}")
#     return js_path


# ==================== Script Store PY Templates ====================
# NOTE: anything passed INTO page.evaluate(...) is still JavaScript — it runs
# in the browser context and uses _js() (above) to build those snippets.
# _py() below is only for the OUTER python-side Playwright driver calls.
# Every lambda here returns a flat, zero-indent multi-line Python block;
# the generator re-indents it with textwrap.indent() — do not hand-indent
# continuation lines inside these lambdas.

def _py(s) -> str:
    """Safely wrap a value as a Python string literal (outer/driver-side code)."""
    return repr(str(s))


_PY_TEMPLATES = {
    "navigate": lambda p: (
        f"await page.goto({_py(p.get('url',''))}, wait_until='domcontentloaded')\n"
        f"try:\n"
        f"    await page.wait_for_load_state('load')\n"
        f"except Exception:\n"
        f"    pass\n"
        f"try:\n"
        f"    await page.wait_for_load_state('networkidle')\n"
        f"except Exception:\n"
        f"    pass"
    ),

    "click": lambda p: (
        f"try:\n"
        f"    await page.evaluate(\"\"\"(sel) => {{\n"
        f"  function isVisible(node) {{\n"
        f"    const s = window.getComputedStyle(node);\n"
        f"    return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;\n"
        f"  }}\n"
        f"  let el;\n"
        f"  const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;\n"
        f"  if (xsel.startsWith('//')) {{\n"
        f"      const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);\n"
        f"      for (let i = 0; i < r.snapshotLength; i++) {{\n"
        f"          const node = r.snapshotItem(i);\n"
        f"          if (isVisible(node)) {{ el = node; break; }}\n"
        f"      }}\n"
        f"  }} else {{\n"
        f"      const nodes = document.querySelectorAll(xsel);\n"
        f"      for (const node of nodes) {{\n"
        f"          if (isVisible(node)) {{ el = node; break; }}\n"
        f"      }}\n"
        f"  }}\n"
        f"  if (el) el.click();\n"
        f"}}\"\"\", {_py(p.get('selector',''))})\n"
        f"except Exception:\n"
        f"    pass\n"
        f"try:\n"
        f"    await page.wait_for_load_state('load')\n"
        f"except Exception:\n"
        f"    pass\n"
        f"try:\n"
        f"    await page.wait_for_load_state('networkidle')\n"
        f"except Exception:\n"
        f"    pass\n"
        f"await page.wait_for_timeout(800)"
    ),

    "click_at_position": lambda p: "\n".join([
        f"await page.locator({_py(p.get('selector', '.mapwrap svg'))}).first.click(position={{'x': {c['x']}, 'y': {c['y']}}})\n"
        f"await page.wait_for_timeout(300)"
        for c in (p.get('clicks') or [{"x": p.get('x', 0), "y": p.get('y', 0)}])
    ]),

    "fill": lambda p:
        f"await page.locator({_py(p.get('selector',''))}).first.fill({_py(p.get('text',''))})",

    "select_option": lambda p: (
        f"await page.evaluate(\"\"\"({{sel, val}}) => {{\n"
        f"  function isVisible(node) {{\n"
        f"    const s = window.getComputedStyle(node);\n"
        f"    return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;\n"
        f"  }}\n"
        f"  let el;\n"
        f"  if (sel.startsWith('//') || sel.startsWith('xpath=')) {{\n"
        f"    const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;\n"
        f"    const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);\n"
        f"    for (let i = 0; i < r.snapshotLength; i++) {{\n"
        f"        const node = r.snapshotItem(i);\n"
        f"        if (isVisible(node)) {{ el = node; break; }}\n"
        f"    }}\n"
        f"  }} else {{\n"
        f"    const nodes = document.querySelectorAll(sel);\n"
        f"    for (const node of nodes) {{\n"
        f"        if (isVisible(node)) {{ el = node; break; }}\n"
        f"    }}\n"
        f"  }}\n"
        f"  if (!el) return false;\n"
        f"  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);\n"
        f"  if (!opt) return false;\n"
        f"  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');\n"
        f"  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);\n"
        f"  else el.value = opt.value;\n"
        f"  el.dispatchEvent(new Event('change', {{ bubbles: true }}));\n"
        f"  el.dispatchEvent(new Event('input', {{ bubbles: true }}));\n"
        f"  return true;\n"
        f"}}\"\"\", {{'sel': {_py(p.get('selector',''))}, 'val': {_py(p.get('value',''))}}})"
    ),

    "press_key": lambda p: (
        f"await page.keyboard.press({_py(p.get('key','Escape'))})\n"
        f"await page.wait_for_timeout(1000)"
    ),

    "screenshot": lambda p:
        f"await page.screenshot(path={_py(p.get('path','screenshot.png'))})",

    "wait_for_load": lambda p:
        f"await page.wait_for_load_state({_py(p.get('state','load'))})",

    "wait_for_selector": lambda p:
        f"await page.wait_for_selector({_py(p.get('selector',''))}, state={_py(p.get('state','visible'))})",

    "hover": lambda p:
        f"await page.locator({_py(p.get('selector',''))}).first.hover()",

    "double_click": lambda p:
        f"await page.dblclick({_py(p.get('selector',''))})",

    "scroll_to_element": lambda p:
        f"await page.locator({_py(p.get('selector',''))}).scroll_into_view_if_needed()",

    "clear_input": lambda p:
        f"await page.fill({_py(p.get('selector',''))}, '')",

    "upload_file": lambda p: (
        f"await page.set_input_files({_py(p.get('selector',''))}, "
        f"{p.get('files', []) if isinstance(p.get('files'), list) else [p.get('files','')]!r})"
    ),

    "assert_text": lambda p: (
        f"t = (await page.locator({_py(p['selector'])}).first.inner_text()).strip()\n"
        f"if {_py(p['expected'])} not in t:\n"
        f"    raise AssertionError(f\"assert_text failed — expected {p['expected']!r}, got: {{t}}\")"
    ),
    "assert_visible": lambda p: (
        f"if not await page.locator({_py(p['selector'])}).first.is_visible():\n"
        f"    raise AssertionError(f\"assert_visible failed: {{{_py(p['selector'])}}}\")"
    ),
    "assert_not_visible": lambda p: (
        f"_c = await page.locator({_py(p['selector'])}).count()\n"
        f"if _c > 0 and await page.locator({_py(p['selector'])}).first.is_visible():\n"
        f"    raise AssertionError(f\"assert_not_visible failed, element visible: {p['selector']!r}\")"
    ),
    "assert_disabled": lambda p: (
        f"if not await page.locator({_py(p['selector'])}).first.is_disabled():\n"
        f"    raise AssertionError(f\"assert_disabled failed, element enabled: {p['selector']!r}\")"
    ),
    "assert_url": lambda p: (
        f"try:\n"
        f"    await page.wait_for_url('**/*{p['expected']}*', timeout={p.get('timeout', 8000)})\n"
        f"except Exception:\n"
        f"    pass\n"
        f"if {_py(p['expected'])} not in page.url:\n"
        f"    raise AssertionError(f\"assert_url failed — got: {{page.url}}\")"
    ),
    "assert_toast": lambda p: (
        f"_result = await page.evaluate(\"\"\"() => {{\n"
        f"  const _all = [...document.querySelectorAll(\n"
        f"    \"[role=alert],[role=status],[class*=toast],[class*=swal2],[class*=alert],[class*=snackbar],[class*=notyf]\"\n"
        f"  )].filter(e => {{ const s = window.getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden' && e.offsetParent !== null; }});\n"
        f"  return _all.map(e => (e.innerText || e.textContent || '').trim()).join(' ');\n"
        f"}}\"\"\")\n"
        f"_exp = {_py(p.get('expected_text', ''))}\n"
        f"if _exp and _exp.lower() not in _result.lower():\n"
        f"    raise AssertionError(f\"assert_toast failed — expected: {{_exp}}, got: {{_result}}\")\n"
        f"if not _exp and not _result:\n"
        f"    raise AssertionError(\"assert_toast failed — no notification visible\")"
    ),
    "execute_js": lambda p:
        f"await page.evaluate({_py(p.get('script', ''))})",
}

_PY_SKIP = {
    "get_interactable_elements", "get_page_content", "get_page_info",
    "get_page_content_and_save_csv", "get_page_content_and_save_txt",
    "get_credentials", "close_session",
}


def _method_to_py(method: str, params: dict) -> Optional[str]:
    """Convert one MCP step → Playwright Python statement (flat, zero-indent)."""
    handler = _PY_TEMPLATES.get(method)
    if not handler:
        return None
    try:
        return handler(params)
    except Exception:
        return None


# ==================== Playwright PYTHON Script Generator ====================

def generate_playwright_py_from_json(json_path: str) -> Optional[str]:
    """
    Read a saved MCP script JSON and generate a standalone async Python
    Playwright script (mirrors the live MCP server, which runs async_playwright).
    Source of truth = the .json file. Output: data/saved_playwright_scripts_py/<stem>.py
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Playwright Generator] Cannot read {json_path}: {e}")
        return None

    steps = data.get("steps", []) if isinstance(data, dict) else data
    if not steps:
        print(f"[Playwright Generator] No steps in {json_path}")
        return None

    stem = Path(json_path).stem
    pw_dir = Path("data/saved_playwright_scripts_py")
    pw_dir.mkdir(parents=True, exist_ok=True)
    py_path = str(pw_dir / f"{stem}.py")
    screenshots_dir = f"data/saved_playwright_scripts_py/screenshots/{stem}"

    lines = [
        f"# Auto-generated Playwright script — {stem}",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Source: {Path(json_path).name}",
        f"# Run: python {stem}.py",
        "# Requires: pip install playwright && playwright install chromium",
        "",
        "import asyncio",
        "import os",
        "from playwright.async_api import async_playwright",
        "",
        f"SCREENSHOT_DIR = {_py(screenshots_dir)}",
        "os.makedirs(SCREENSHOT_DIR, exist_ok=True)",
        "",
        "",
        "async def run_test():",
        "    async with async_playwright() as pw:",
        "        browser = await pw.chromium.launch(headless=False)",
        "        context = await browser.new_context(ignore_https_errors=True)",
        "        page = await context.new_page()",
        "",
        "        try:",
    ]

    for step in steps:
        method  = step.get("method", "")
        params  = {k: v for k, v in step.get("params", {}).items() if k != "sessionId"}
        desc    = step.get("step", "")
        status  = step.get("status", "passed")
        step_id = step.get("id", "?")

        params = dict(params)
        original = params.get("selector", "")
        resolved = params.get("resolved_selector", "")
        # Prefer original selector; fall back to resolved_selector only when
        # original is empty. resolved_selector can contain broken XPath when
        # the button text itself contains double quotes (double-quote inside a
        # double-quoted XPath string literal → invalid XPath).
        if original:
            params["selector"] = re.sub(r'\s+\d+(")\]$', r'\1]', original)
        elif resolved and ("[" in resolved or "@" in resolved or "#" in resolved):
            params["selector"] = resolved

        lines.append("")

        if method in _PY_SKIP:
            lines.append(f"            # [Step {step_id}] {desc} [{method}] — MCP-only, skipped")
            continue

        if status == "failed":
            lines.append(f"            # STEP {step_id} FAILED [{method}] — fix manually before running")
            lines.append(f"            # {desc}")
            py_line = _method_to_py(method, params)
            if py_line:
                commented = "\n".join(f"# {sub}" for sub in py_line.split("\n"))
                lines.append(textwrap.indent(commented, "            ").rstrip())
            continue

        lines.append(f"            # Step {step_id}: {desc}")
        lines.append(f"            print('>> STEP {step_id}')")

        if method == "screenshot":
            ss_path = f"{screenshots_dir}/step_{step_id}.png"
            lines.append(f"            await page.screenshot(path={_py(ss_path)})")
            continue

        py_line = _method_to_py(method, params)
        if py_line:
            lines.append(textwrap.indent(py_line, "            ").rstrip())
            ss_auto = f"{screenshots_dir}/step_{step_id}.png"
            lines.append(f"            await page.screenshot(path={_py(ss_auto)})")

    lines += [
        "",
        "            print('Test completed')",
        "        except Exception as err:",
        "            print(f'Test failed: {err}')",
        "            raise",
        "        finally:",
        "            await browser.close()",
        "",
        "",
        'if __name__ == "__main__":',
        "    asyncio.run(run_test())",
        "",
    ]

    with open(py_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[Playwright Generator] Python script generated: {py_path}")
    return py_path


# ==================== Script Store ====================

class ScriptStore:
    """
    Records every executed command as a replayable JSON-RPC script.
    Flushes to disk after EVERY step so the file is always up-to-date.
    Saved to: data/saved_scripts/<clean_tc_id>_<run_timestamp>.json
    """

    def __init__(self):
        self._steps: Dict[str, list] = {}
        self._paths: Dict[str, str] = {}
        self._py_paths: Dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def init_script(self, test_case_id: str, run_timestamp: str, session_id: str):
        async with self._lock:
            self._steps[test_case_id] = []

            clean = test_case_id.replace(" ", "_").replace("=", "")
            script_dir = Path("data/saved_scripts")
            script_dir.mkdir(parents=True, exist_ok=True)
            path = str(script_dir / f"{clean}_{run_timestamp}.json")
            self._paths[test_case_id] = path

            self._flush(test_case_id)
            print(f"[ScriptStore] Script file created: {path}")

    async def append_step(self, test_case_id: str, method: str, params: dict,
                           step_description: str, step_id: int, status: str = "passed"):
        async with self._lock:
            if test_case_id not in self._steps:
                return

            entry = {
                "jsonrpc": "2.0",
                "method": method,
                "step": step_description,
                "status": status,
                "params": params,
                "id": step_id
            }
            self._steps[test_case_id].append(entry)
            self._flush(test_case_id)
            print(f"[ScriptStore] Step {step_id} ({status}) appended → {self._paths[test_case_id]}")

    async def get_failed_steps(self, test_case_id: str) -> list:
        async with self._lock:
            return [
                s for s in self._steps.get(test_case_id, [])
                if s.get("status") == "failed"
            ]

    async def finalize_script(self, test_case_id: str):
        async with self._lock:
            steps = self._steps.get(test_case_id, [])
            path  = self._paths.get(test_case_id)
            if not path:
                return

            failed = [s for s in steps if s.get("status") == "failed"]
            passed = [s for s in steps if s.get("status") != "failed"]

            summary = {
                "total_steps": len(steps),
                "passed": len(passed),
                "failed": len(failed),
                "failed_steps": [
                    f"Step {s['id']} failed - {s['step']} [{s['method']}]"
                    for s in failed
                ]
            }

            final = {
                "summary": summary,
                "steps": steps,
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(final, f, indent=2, ensure_ascii=False)

            py_path = generate_playwright_py_from_json(path)
            if py_path:
                self._py_paths[test_case_id] = py_path
                print(f"[ScriptStore] Playwright script (PY): {py_path}")

            print(f"[ScriptStore] Script finalized: {path}")
            if failed:
                print(f"[ScriptStore] {len(failed)} step(s) FAILED:")
                for s in failed:
                    print(f"   ✘ Step {s['id']} - {s['step']} [{s['method']}]")
            else:
                print(f"[ScriptStore] All {len(steps)} step(s) passed.")

    def _flush(self, test_case_id: str):
        path = self._paths.get(test_case_id)
        steps = self._steps.get(test_case_id)
        if path is not None and steps is not None:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(steps, f, indent=2, ensure_ascii=False)

    async def get_script_path(self, test_case_id: str) -> Optional[str]:
        async with self._lock:
            return self._paths.get(test_case_id)

    async def get_py_script_path(self, test_case_id: str) -> Optional[str]:
        async with self._lock:
            return self._py_paths.get(test_case_id)

    async def clear(self, test_case_id: str):
        async with self._lock:
            self._steps.pop(test_case_id, None)
            self._paths.pop(test_case_id, None)


# ==================== Report Save/Finalize ====================

def save_test_report(report: dict) -> str:
    test_case_id = report.get("test_case_id", "unknown")
    report["timer"] = 1
    report_dir = Path("data/test_reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%d%m%Y_%H%M%S")
    clean_name = test_case_id.replace(" ", "_").replace("=", "")
    report_file = report_dir / f"report_{clean_name}_{ts}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Test report saved: {report_file}")
    return str(report_file)


def _normalize_timestamp(ts: str) -> str:
    """Convert DDMMYYYY_HHMMSS to ISO 8601 format YYYY-MM-DDTHH:MM:SS."""
    try:
        dt = datetime.strptime(ts, "%d%m%Y_%H%M%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return ts


async def finalize_test_report(test_case_id: str, reports: ReportStore) -> dict:
    """Save the completed report to disk."""
    report = await reports.pop_report(test_case_id)
    if not report:
        return {"report_path": None, "error": "No in-memory report found"}
    report_path = save_test_report(report)
    return {"report_path": report_path, "test_case_id": test_case_id}


def _find_latest_report_file(test_case_id: str) -> Optional[Path]:
    """Find the most recently saved report JSON for the given test_case_id."""
    report_dir = Path("data/test_reports")
    if not report_dir.exists():
        return None
    clean = test_case_id.replace(" ", "_").replace("=", "")
    matches = sorted(
        report_dir.glob(f"report_{clean}_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


# ==================== Report Submit ====================

async def submit_report_to_submit_agent(report: dict, token: str = "",
                                        submit_url: str = "") -> Dict[str, Any]:
    """Submit a report to the backend API. Token must come from the caller."""
    if not token:
        return {"skipped": True, "reason": "No token provided."}

    url = submit_url or (os.getenv("SUBMIT_AGENT_URL") or
                         "http://172.16.12.136:3000/api/running/submit-agent").strip()
    if not url:
        return {"skipped": True, "reason": "SUBMIT_AGENT_URL is empty"}

    timeout_seconds = float(os.getenv("SUBMIT_AGENT_TIMEOUT_SECONDS") or "20")
    retries = int(os.getenv("SUBMIT_AGENT_RETRIES") or "2")
    payload_mode = (os.getenv("SUBMIT_AGENT_PAYLOAD_MODE") or "multipart").strip().lower()

    test_suite_id = str(report.get("test_suite_id") or "")
    test_case_id = str(report.get("test_case_id") or "")
    timer = max(1, int(report.get("timer") or 1))
    test_steps = report.get("test_step") or []

    def _step_file_bytes(step: dict):
        b64 = (step.get("file") or step.get("screenshot") or "").strip()
        if not b64:
            return None
        try:
            data_bytes = base64.b64decode(b64, validate=True)
        except Exception:
            try:
                data_bytes = base64.b64decode(b64)
            except Exception:
                return None
        if data_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            try:
                from io import BytesIO
                from PIL import Image
                im = Image.open(BytesIO(data_bytes))
                if im.mode != "RGB":
                    im = im.convert("RGB")
                buf = BytesIO()
                im.save(buf, format="JPEG", quality=85, optimize=True)
                return buf.getvalue(), ".jpg", "image/jpeg"
            except Exception:
                return data_bytes, ".png", "image/png"
        if data_bytes.startswith(b"\xff\xd8"):
            return data_bytes, ".jpg", "image/jpeg"
        return data_bytes, ".bin", "application/octet-stream"

    test_steps_json = json.dumps(
        [{k: v for k, v in (s or {}).items() if k not in ("file", "screenshot")}
         for s in test_steps],
        ensure_ascii=False,
    )
    data = {
        "test_suite_id": test_suite_id,
        "test_case_id": test_case_id,
        "timer": str(timer),
        "test_steps": test_steps_json,
        "testSteps": test_steps_json,
        "run_timestamp": _normalize_timestamp(str(report.get("run_timestamp") or "")),
        "run_number": str(report.get("run_number") or ""),
    }
    headers = {}
    headers["Authorization"] = (token if token.lower().startswith("bearer ")
                                 else f"Bearer {token}")

    print(f"[submit-agent] POST {url}")
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        for attempt in range(retries + 1):
            try:
                if payload_mode == "multipart":
                    multipart_fields: Dict[str, Any] = {k: (None, v) for k, v in data.items()}
                    if os.getenv("SUBMIT_AGENT_INCLUDE_SCREENSHOTS", "true").lower() != "false":
                        for s in test_steps:
                            step_num = s.get("test_step_number")
                            if step_num is None:
                                continue
                            file_info = _step_file_bytes(s)
                            if not file_info:
                                continue
                            file_bytes, ext, ct = file_info
                            multipart_fields[f"file_step_{step_num}"] = (
                                f"step_{step_num}{ext}", file_bytes, ct)
                    resp = await client.post(url, files=multipart_fields, headers=headers)
                elif payload_mode == "json":
                    resp = await client.post(url, json=data, headers=headers)
                else:
                    resp = await client.post(url, data=data, headers=headers)
                ok = 200 <= resp.status_code < 300
                result = {
                    "ok": ok,
                    "status_code": resp.status_code,
                    "response_preview": (resp.text or "")[:800],
                }
                print(f"[submit-agent] status={resp.status_code} ok={ok}")
                if not ok and resp.status_code >= 500 and attempt < retries:
                    await asyncio.sleep(0.8 * (attempt + 1))
                    continue
                return result
            except Exception as e:
                if attempt < retries:
                    await asyncio.sleep(0.8 * (attempt + 1))
                    continue
                return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "Unknown error"}