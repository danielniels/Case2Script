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
        # Tracks the aria-controls id of the last combobox/listbox trigger that
        # was clicked open, so a following click_by_index step ("pick option X
        # from the list") can be scoped to options belonging to THAT specific
        # popup. Without this, a page with multiple Select/dropdown instances
        # (e.g. a component-library docs page with several demo widgets) can
        # have a candidate option's text coincidentally collide with a value
        # already shown by a DIFFERENT, unrelated widget elsewhere on the page —
        # see [[project_click_by_index_icon_resolution]] "Banana" case, 2026-07-09.
        self.last_combobox_controls: Optional[str] = None

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


_QUOTED_LABEL_RE = re.compile(r"['\"]([^'\"]{1,80})['\"]")


def _extract_quoted_label(desc: str) -> Optional[str]:
    """Pull a quoted label out of a step description, e.g. "Check the checkbox
    for test case 'Delete Cycle'" -> "Delete Cycle".

    Used as a portability fallback for two live-session-only recording styles
    that don't survive being replayed in a fresh browser session:
      - click_by_index: clicks the Nth element of a live-refetched
        "interactable elements" snapshot. That index has no meaning outside
        the exact session it was captured in (it shifts with list length,
        DOM state, timing, etc).
      - a `click` selector containing a Radix/shadcn auto-generated id
        (id="radix-_r_X_"). Radix assigns these via an internal mount-order
        counter that resets and renumbers on every fresh page load, so an id
        captured in one session is not guaranteed to exist — or to mean the
        same thing — in another.
    Where we can recover the option's visible text (from `expected_text` or a
    quoted phrase in the description), we rebuild a text-based selector
    instead, which IS stable across sessions since it doesn't depend on
    DOM/mount ordering.
    """
    if not desc:
        return None
    matches = _QUOTED_LABEL_RE.findall(desc)
    return matches[-1] if matches else None


def _text_option_selector_py(label: str) -> str:
    """Build a Playwright XPath that finds a listbox option / checkbox row by
    its visible text, instead of a Radix auto-generated id or a live element
    index. Known limitation: if `label` itself contains a `"` character, the
    XPath attribute-value quoting below will break — rare in practice for UI
    labels, not handled here."""
    return (
        f'//*[@role="option"][normalize-space(.) = "{label}"]'
        f' | //*[@role="option"][.//text()[normalize-space(.) = "{label}"]]'
        f' | //*[@cmdk-item][.//text()[normalize-space(.) = "{label}"]]'
    )


def _icon_button_selector_py(tag: str, identity_attr: str, identity_value: str,
                              row_label: Optional[str] = None) -> str:
    """Build a Playwright XPath for an icon-only button (no visible text —
    identified by title or aria-label instead, e.g. a lucide <Eye> icon with
    title="View"). This is a DIFFERENT shape than _text_option_selector_py:
    that one is for combobox/listbox *options*; this one is for a plain
    action button that happens to have no text content.

    If row_label is given (from a quoted phrase in the step description, e.g.
    "row where Name is 'X'"), the selector is scoped to the row/list-item
    containing that text first — otherwise, with N rows each carrying an
    identical title="View" button, .first would always click row 1 regardless
    of which row the step actually meant. Checks tr / [role="row"] / li, same
    as the live click_by_index row_context lookup (tools.py), so replayed
    scripts and live runs resolve the same element the same way.

    Known limitation: same as _text_option_selector_py — a `"` inside
    identity_value or row_label breaks the XPath string literal; not handled.
    """
    tag = (tag or "button").lower()
    base = f'//{tag}[@{identity_attr}="{identity_value}"]'
    if not row_label:
        return base
    return (
        f'//tr[contains(normalize-space(.), "{row_label}")]{base}'
        f' | //*[@role="row"][contains(normalize-space(.), "{row_label}")]{base}'
        f' | //li[contains(normalize-space(.), "{row_label}")]{base}'
    )


def _button_text_selector_py(tag: str, text: str, row_label: Optional[str] = None) -> str:
    """Build a Playwright XPath for a click_by_index target identified by its
    own visible text — the common case, e.g. a plain `<button>Log In</button>`.
    This is the THIRD shape click_by_index needs alongside
    _icon_button_selector_py (title/aria-label, no text) and
    _text_option_selector_py (role="option"/cmdk-item, combobox picks).

    Found missing 2026-07-09: a recorded step "Click the login button" had no
    element_title/element_aria_label (a plain text button has neither), so
    normalization fell through to _text_option_selector_py — which builds a
    role="option"/cmdk-item selector. That's structurally wrong for a normal
    button and always times out. element_text (already returned by
    cmd_click_by_index, tools.py) is the correct identity source here and is
    checked FIRST in the normalization chain below, before title/aria-label,
    since icon buttons naturally have empty text and fall through unaffected.

    Same row-scoping support as _icon_button_selector_py for consistency,
    though most text-identified buttons (login, tab labels, etc.) won't have
    a row_label since they're not per-row.

    Known limitation: same as sibling functions — a `"` inside text/row_label
    breaks the XPath string literal; not handled.
    """
    tag = (tag or "button").lower()
    base = f'//{tag}[.//text()[normalize-space(.) = "{text}"]]'
    if not row_label:
        return base
    return (
        f'//tr[contains(normalize-space(.), "{row_label}")]{base}'
        f' | //*[@role="row"][contains(normalize-space(.), "{row_label}")]{base}'
        f' | //li[contains(normalize-space(.), "{row_label}")]{base}'
    )


def _js_click_click_py(selector: str) -> str:
    """One click block — same isVisible+xpath/css lookup JS used by the 'click'
    template, parameterized on selector. Used to replay ARIA-combobox
    select_option as two sequential real clicks (open trigger, click option)
    instead of the native <select> Array.from(el.options) trick, which does
    nothing on a Radix/shadcn-style combobox."""
    return (
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
        f"}}\"\"\", {_py(selector)})\n"
        f"except Exception:\n"
        f"    pass\n"
        f"await page.wait_for_timeout(800)"
    )


def _select_option_py(p: dict) -> str:
    if p.get("resolved_via") == "aria_combobox":
        trigger = p.get("trigger_selector") or p.get("selector", "")
        # Rebuild the option selector from `value` (the visible label, e.g.
        # "TCM Testing" / "Medium") rather than trusting the recorded
        # `option_selector`, which is usually scoped to a Radix auto-generated
        # container id (id="radix-_r_X_"). That id is only valid within the
        # exact browser session it was captured in — Radix renumbers its
        # internal mount-order counter on every fresh page load, so a script
        # exported from one session and replayed in another can silently
        # resolve to the wrong (or a disabled) element. A text-based selector
        # has no such dependency.
        label = p.get("value", "")
        option_sel = _text_option_selector_py(label) if label else p.get("option_selector")
        if not option_sel:
            return (
                f"# select_option (ARIA combobox) — matched option text could not be\n"
                f"# safely converted to an XPath selector (likely contains a `\"` character).\n"
                f"# MANUAL FIX NEEDED: open {_py(trigger)} and click the option for "
                f"value={_py(p.get('value', ''))} by hand."
            )
        return (
            _js_click_click_py(trigger)
            + "\n"
            + _js_click_click_py(option_sel)
        )

    # Select2 / native <select> path — unchanged.
    return (
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
    )


# Injected once into any generated script that has an upload_file step, so the
# standalone .py file never depends on Case2Script's data/fixtures/ folder or
# its FastAPI backend. Resolution order, fully automated (zero clicks) for the
# first four, dialog only as a last resort:
#   1) env var override               — for CI/unattended runs
#   2) absolute path (the hint itself, if it's already a full path)
#   3) home-folder shortcut           — "downloads/x.pdf" -> ~/Downloads/x.pdf
#      (mirrors tools.py::_resolve_fixtures on the live MCP session, so a case
#      description written once behaves the same during recording AND replay)
#   4) relative to the script's own working directory
#   5) native OS file picker          — only reached if 1-4 all miss; this is
#      the one path that needs a human at the keyboard.
_UPLOAD_HELPER_PY = (
    'def _resolve_upload_file(hint: str, env_var: str) -> str:\n'
    '    """Resolve a file to upload without needing Case2Script\'s fixtures folder\n'
    '    or its backend. See _UPLOAD_HELPER_PY comment in stores.py for the full\n'
    '    resolution order — env var / absolute path / ~/Downloads-style shortcut /\n'
    '    cwd-relative all resolve with ZERO manual interaction; only the final\n'
    '    native-dialog fallback needs a human click."""\n'
    '    override = os.environ.get(env_var)\n'
    '    candidate = override or hint\n'
    '    if os.path.isabs(candidate) and os.path.isfile(candidate):\n'
    '        return candidate\n'
    '    _shortcuts = {"downloads": "Downloads", "download": "Downloads",\n'
    '                  "desktop": "Desktop", "documents": "Documents", "document": "Documents"}\n'
    '    _norm = candidate.replace("\\\\", "/")\n'
    '    _head, _sep, _rest = _norm.partition("/")\n'
    '    if _sep and _rest:\n'
    '        _head_s = _head.strip()\n'
    '        _alias = _shortcuts.get(_head_s.lower())\n'
    '        if _alias:\n'
    '            _guess = os.path.join(os.path.expanduser("~"), _alias, _rest)\n'
    '            if os.path.isfile(_guess):\n'
    '                return _guess\n'
    '        else:\n'
    '            _home = os.path.expanduser("~")\n'
    '            try:\n'
    '                for _entry in os.listdir(_home):\n'
    '                    if _entry.lower() == _head_s.lower() and os.path.isdir(os.path.join(_home, _entry)):\n'
    '                        _guess2 = os.path.join(_home, _entry, _rest)\n'
    '                        if os.path.isfile(_guess2):\n'
    '                            return _guess2\n'
    '            except OSError:\n'
    '                pass\n'
    '    else:\n'
    '        # Bare filename, no folder prefix at all — scan common OS folders\n'
    '        # in priority order (Documents first) before giving up. Mirrors\n'
    '        # tools.py::_scan_common_folders on the live MCP session, so a\n'
    '        # case description behaves the same during recording AND replay.\n'
    '        _home3 = os.path.expanduser("~")\n'
    '        for _folder in ("Documents", "Downloads", "Desktop"):\n'
    '            _guess3 = os.path.join(_home3, _folder, candidate)\n'
    '            if os.path.isfile(_guess3):\n'
    '                print(f"[upload] bare filename {candidate!r} matched in ~/{_folder}/ -> {_guess3}")\n'
    '                return _guess3\n'
    '    if os.path.isfile(candidate):\n'
    '        return os.path.abspath(candidate)\n'
    '    if override:\n'
    '        raise FileNotFoundError(f"{env_var} is set to {override!r} but that file does not exist")\n'
    '    if os.environ.get("C2S_NO_DIALOG"):\n'
    '        raise FileNotFoundError(\n'
    '            f"Could not auto-resolve upload file for {hint!r} (tried absolute path, "\n'
    '            f"~/Downloads or ~/Desktop or ~/Documents style shortcut, and cwd-relative), "\n'
    '            f"and C2S_NO_DIALOG is set so the file picker is disabled. "\n'
    '            f"Set env var {env_var}=<absolute path> instead."\n'
    '        )\n'
    '    print(\n'
    '        f"[upload] Could not auto-resolve {hint!r} (checked absolute path, "\n'
    '        f"~/Downloads-style shortcut, and cwd-relative). Opening a file picker so "\n'
    '        f"you can select it manually — you have 120s. To skip this in unattended "\n'
    '        f"runs, set env var {env_var}=<absolute path>, or C2S_NO_DIALOG=1 to fail fast instead."\n'
    '    )\n'
    '    import threading\n'
    '    _dialog_result = {}\n'
    '    def _show_dialog():\n'
    '        try:\n'
    '            import tkinter as tk\n'
    '            from tkinter import filedialog\n'
    '            root = tk.Tk()\n'
    '            root.withdraw()\n'
    '            root.attributes("-topmost", True)\n'
    '            _dialog_result["path"] = filedialog.askopenfilename(title=f"Select file to upload: {hint}")\n'
    '            root.destroy()\n'
    '        except Exception as e:\n'
    '            _dialog_result["error"] = e\n'
    '    _t = threading.Thread(target=_show_dialog, daemon=True)\n'
    '    _t.start()\n'
    '    _t.join(timeout=120)\n'
    '    if _t.is_alive():\n'
    '        raise TimeoutError(\n'
    '            f"No file selected within 120s for upload step: {hint!r}. If this ran "\n'
    '            f"unattended by mistake, set env var {env_var}=<absolute path> instead."\n'
    '        )\n'
    '    _dialog_err = _dialog_result.get("error")\n'
    '    if _dialog_err is not None:\n'
    '        raise RuntimeError(\n'
    '            f"Could not open file picker for {hint!r}: {_dialog_err}. "\n'
    '            f"Fix the path, or set env var {env_var}=<absolute path>."\n'
    '        ) from _dialog_err\n'
    '    _path = _dialog_result.get("path")\n'
    '    if not _path:\n'
    '        raise RuntimeError(f"No file selected for upload step: {hint!r}")\n'
    '    return _path'
)


def _upload_file_py(p: dict) -> str:
    """Emits one _resolve_upload_file() call per file, then a single
    set_input_files() with the resolved paths. env var name is derived from
    the step id so multiple upload steps in one script don't collide."""
    files = p.get("files", [])
    if not isinstance(files, list):
        files = [files]
    if not files:
        return "# upload_file step had no files recorded — nothing to generate"

    safe_step_id = re.sub(r"[^A-Za-z0-9_]", "_", str(p.get("_step_id", "X"))).upper()
    out_lines = []
    var_names = []
    for i, f in enumerate(files):
        env_var = f"C2S_UPLOAD_{safe_step_id}_{i}"
        var_name = f"_upload_{safe_step_id}_{i}"
        out_lines.append(f"{var_name} = _resolve_upload_file({_py(f)}, {_py(env_var)})")
        var_names.append(var_name)
    out_lines.append(
        f"await page.set_input_files({_py(p.get('selector',''))}, [{', '.join(var_names)}])"
    )
    return "\n".join(out_lines)


# ==================== Selector classification (XPath -> semantic locator) ====================
# Playwright's own docs recommend role/text/label/placeholder locators over
# raw XPath/CSS — they mirror how a real user or screen reader perceives the
# page and tolerate DOM restructuring that breaks brittle XPath text-node
# matching. Every selector recorded into saved_scripts/*.json is already a
# single, already-decided XPath/CSS string (see the click/fill MCP tool
# schemas in tools.py — there's no separate role/text/placeholder field to
# prefer instead), so this can only be a POST-hoc conversion: recognize the
# small set of structural shapes this codebase's own recorder actually
# produces, and rewrite those to Playwright's native locator API. Verified
# against 182 real recorded selectors across every saved test case: 91%
# (166/182) match one of the shapes below. Anything unrecognized returns
# None — the caller keeps the raw XPath/CSS as the ONLY locator in that
# case, identical to pre-existing behavior, so an unmatched shape is zero
# regression, never a failure.

_SEL_ID = re.compile(r'^(?:xpath=)?//\w+\[@id\s*=\s*["\']([^"\']+)["\']\]$', re.I)
_SEL_NAME = re.compile(r'^(?:xpath=)?//\w+\[@name\s*=\s*["\']([^"\']+)["\']\]$', re.I)
_SEL_PLACEHOLDER = re.compile(r'^(?:xpath=)?//\w+\[@placeholder\s*=\s*["\']([^"\']+)["\']\]$', re.I)
_SEL_ARIA_LABEL = re.compile(r'^(?:xpath=)?//\w+\[@aria-label\s*=\s*["\']([^"\']+)["\']\]$', re.I)
# Icon-only elements identified by their title tooltip (see prompts.py:
# "Icon-only buttons ... carry their identity in title="). Unlike id/name/
# aria-label, title is frequently NOT unique across a page — responsive
# sites commonly render a desktop nav AND a mobile nav simultaneously in the
# DOM, each with its own icon carrying the identical title (e.g. two
# <a title="USER"> nodes, one hidden via CSS media query at the current
# viewport). Before this pattern existed, _classify_selector_py returned
# None for title-based xpaths, which skipped click_with_fallback entirely
# and fell straight to the unprotected `page.locator(xpath).first.click()`
# path (see _click_py) — `.first` picks DOM order, not visibility, so it
# can silently resolve to the hidden twin and time out waiting for it to
# become visible. Found 2026-07-23 via advantageonlineshopping.com's navbar
# (title="USER" duplicated across desktop/mobile nav blocks). Appending
# `:visible` (a native Playwright CSS extension, not a JS-evaluate hack —
# consistent with the no-JS-evaluate locator standard) filters the match
# down to whichever twin is actually rendered right now.
_SEL_TITLE = re.compile(r'^(?:xpath=)?//(\w+)\[@title\s*=\s*["\']([^"\']+)["\']\]$', re.I)
_SEL_TEXT = re.compile(
    r'^(?:xpath=)?//(\w+)\[(?:\.//text\(\)|text\(\))\[normalize-space\(\.\)\s*=\s*'
    r'(?:"([^"]*)"|\'([^\']*)\')\]\]$'
)
_TAG_TO_ROLE = {"button": "button", "a": "link"}


def _classify_selector_py(selector: str) -> Optional[str]:
    """Return a Playwright locator expression as source code (e.g.
    'page.get_by_placeholder("Requirement name")') if `selector` matches a
    known recorder shape, else None. `label/following::` (relative form-field
    matching, e.g. //label[...]/following::input[1]) is deliberately NOT
    converted to get_by_label() — that XPath shape exists specifically for
    forms with no real <label for>/aria-labelledby association, which is
    exactly what get_by_label() requires to find anything. Left as XPath —
    safe, matches current behavior."""
    if not selector:
        return None
    s = selector.strip()

    m = _SEL_ID.match(s)
    if m:
        css = "#%s" % m.group(1)
        return f"page.locator({_py(css)})"

    m = _SEL_NAME.match(s)
    if m:
        css = '[name="%s"]' % m.group(1).replace('"', '\\"')
        return f"page.locator({_py(css)})"

    m = _SEL_PLACEHOLDER.match(s)
    if m:
        return f"page.get_by_placeholder({_py(m.group(1))}, exact=True)"

    m = _SEL_ARIA_LABEL.match(s)
    if m:
        return f"page.get_by_label({_py(m.group(1))}, exact=True)"

    m = _SEL_TITLE.match(s)
    if m:
        tag = m.group(1).lower()
        title = m.group(2).replace('\\', '\\\\').replace('"', '\\"')
        css = f'{tag}[title="{title}"]:visible'
        return f"page.locator({_py(css)})"

    m = _SEL_TEXT.match(s)
    if m:
        tag = m.group(1).lower()
        label = m.group(2) if m.group(2) is not None else m.group(3)
        role = _TAG_TO_ROLE.get(tag)
        if role:
            return f"page.get_by_role({_py(role)}, name={_py(label)}, exact=True)"
        return f"page.get_by_text({_py(label)}, exact=True)"

    return None


# Injected into any generated script that has a click or fill step (i.e.
# virtually all of them). Tries the semantic locator built by
# _classify_selector_py() first; only falls back to the raw XPath/CSS
# recorded at capture time if that times out. Both paths go through
# Playwright's native click()/fill(), so actionability checks
# (visible/stable/enabled/receives-events) always apply — unlike the old
# page.evaluate() force-click this replaces, which bypassed them entirely
# and could "succeed" against an element a real user couldn't reach.
_LOCATOR_HELPER_PY = (
    'async def click_with_fallback(page, primary, xpath_fallback, desc, timeout=15000):\n'
    '    try:\n'
    '        await primary.click(timeout=timeout)\n'
    '    except Exception:\n'
    '        print(f"[fallback] semantic locator failed for {desc}, trying recorded selector")\n'
    '        await page.locator(xpath_fallback).first.click(timeout=timeout)\n'
    '\n'
    '\n'
    'async def fill_with_fallback(page, primary, value, xpath_fallback, desc, timeout=15000):\n'
    '    try:\n'
    '        await primary.fill(value, timeout=timeout)\n'
    '    except Exception:\n'
    '        print(f"[fallback] semantic locator failed for {desc}, trying recorded selector")\n'
    '        await page.locator(xpath_fallback).first.fill(value, timeout=timeout)'
)


def _click_py(p: dict) -> str:
    selector = p.get('selector', '')
    primary = _classify_selector_py(selector)
    desc = _py(selector[:80])
    # timeout=15000, not the old 6000: Playwright's own actionability polling
    # (attached/visible/stable/enabled) already retries the WHOLE window, so a
    # longer budget costs nothing when the element shows up quickly — it only
    # matters on the slow-render case this was raised for. Found 2026-07-09:
    # a click_by_index step immediately following a client-side SPA route
    # change (sidebar nav click, no full page reload) needs the destination
    # view's data (e.g. a table fetched async) to render before the next
    # step's target exists. Verified the row-scoped XPath itself was 100%
    # correct via a standalone lxml XPath test against the real page HTML —
    # the failure was purely a timing race, not a selector bug. 6000ms +
    # the ~2.4s of settle time after the PRIOR click (load/networkidle/400ms)
    # wasn't consistently enough. This is universal (any click that follows
    # a client-side navigation can hit the same race), not specific to
    # click_by_index/icon buttons — hence the bump applies to every click.
    if primary:
        body = f"await click_with_fallback(page, {primary}, {_py(selector)}, {desc}, timeout=15000)\n"
    else:
        # No known semantic shape recognized (see _classify_selector_py) —
        # use the recorded XPath/CSS directly via native click(), same
        # selector as before. No JS-evaluate force-click anymore anywhere:
        # Playwright's own actionability wait replaces it.
        body = f"await page.locator({_py(selector)}).first.click(timeout=15000)\n"
    return (
        body +
        f"try:\n"
        f"    await page.wait_for_load_state('load')\n"
        f"except Exception:\n"
        f"    pass\n"
        f"try:\n"
        # Bounded to 2s — see identical comment on the "navigate" template.
        f"    await page.wait_for_load_state('networkidle', timeout=2000)\n"
        f"except Exception:\n"
        f"    pass\n"
        f"await page.wait_for_timeout(400)"
    )


def _fill_py(p: dict) -> str:
    selector = p.get('selector', '')
    text = p.get('text', '')
    primary = _classify_selector_py(selector)
    desc = _py(selector[:80])
    if primary:
        action = f"await fill_with_fallback(page, {primary}, {_py(text)}, {_py(selector)}, {desc}, timeout=15000)"
    else:
        action = f"await page.locator({_py(selector)}).first.fill({_py(text)})"
    return (
        f"try:\n"
        f"    {action}\n"
        f"except Exception:\n"
        f"    await page.screenshot(path=f'{{SCREENSHOT_DIR}}/FAILED.png')\n"
        f"    raise"
    )


def _assert_text_py(p: dict) -> str:
    """assert_text template. input_value() is the correct Playwright API for
    <input>/<textarea>, but on a native <select> it returns the selected
    OPTION'S VALUE ATTRIBUTE (e.g. "2"), not its visible label ("Option 2")
    — and since input_value() doesn't throw for a <select>, the old
    text_content() fallback (only reached on exception) never fired. Test
    descriptions almost always mean the visible label. Found 2026-07-09 via
    a real replay failure (TC001): expected 'Option 2', got '2'. Fixed by
    detecting <select> and also capturing the selected option's own text as
    a second candidate — match succeeds against EITHER the raw
    input_value()/text_content() OR the select's label, so scripts that
    intentionally assert against a raw value (e.g. "2") still work too.
    Same defect existed in the live engine's cmd_assert_text (tools.py),
    fixed there in the same way — this is not select-specific to one test
    case, applies to every assert_text step targeting a <select>."""
    selector = p.get('selector', '')
    expected = p.get('expected', '')
    return (
        f"_loc = page.locator({_py(selector)}).first\n"
        f"_select_label = ''\n"
        f"try:\n"
        f"    if ((await _loc.evaluate('el => el.tagName')) or '').upper() == 'SELECT':\n"
        f"        _select_label = ((await _loc.evaluate(\"el => el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : ''\")) or '').strip()\n"
        f"except Exception:\n"
        f"    pass\n"
        f"try:\n"
        f"    t = (await _loc.input_value()).strip()\n"
        f"except Exception:\n"
        f"    t = (await _loc.text_content() or '').strip()\n"
        f"if not t:\n"
        f"    try:\n"
        f"        t = (await _loc.text_content() or '').strip()\n"
        f"    except Exception:\n"
        f"        pass\n"
        f"_expected = {_py(expected)}\n"
        f"_match = (_expected in t) or bool(_select_label and _expected in _select_label)\n"
        f"if _match and _select_label and _expected in _select_label and _expected not in t:\n"
        f"    t = _select_label\n"
        f"if not _match:\n"
        f"    _detail = f\", select_label={{_select_label!r}}\" if _select_label else ''\n"
        f"    raise AssertionError(f\"assert_text failed — expected {{_expected!r}}, got: {{t}}{{_detail}}\")"
    )


_PY_TEMPLATES = {
    "navigate": lambda p: (
        f"await page.goto({_py(p.get('url',''))}, wait_until='domcontentloaded')\n"
        f"try:\n"
        f"    await page.wait_for_load_state('load')\n"
        f"except Exception:\n"
        f"    pass\n"
        f"try:\n"
        # Bounded to 2s, not Playwright's 30s default. Its result is never
        # branched on (bare except below) — on apps with any persistent
        # background traffic (polling, websockets, live-session pings), the
        # page can go the *entire* run without a 500ms-quiet window, so this
        # otherwise burns the full default timeout for zero benefit every
        # single time. Measured on this app: 6+ steps hit exactly ~30.0s each
        # before this fix (~180s of dead waiting out of a 191s run).
        f"    await page.wait_for_load_state('networkidle', timeout=2000)\n"
        f"except Exception:\n"
        f"    pass"
    ),

    "click": _click_py,

    "click_at_position": lambda p: "\n".join([
        f"await page.locator({_py(p.get('selector', '.mapwrap svg'))}).first.click(position={{'x': {c['x']}, 'y': {c['y']}}})\n"
        f"await page.wait_for_timeout(300)"
        for c in (p.get('clicks') or [{"x": p.get('x', 0), "y": p.get('y', 0)}])
    ]),

    "fill": _fill_py,

    "select_option": _select_option_py,

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

    "upload_file": _upload_file_py,

    "assert_text": _assert_text_py,
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

    # Deduplicate by step id — when a run fails and retries, the JSON contains
    # steps from both runs with the same ids. Keep only the last occurrence
    # (the retry run), which has the most up-to-date selectors and status.
    seen: dict = {}
    for s in steps:
        seen[s.get("id", id(s))] = s
    steps = list(seen.values())

    stem = Path(json_path).stem
    pw_dir = Path("data/saved_playwright_scripts_py")
    pw_dir.mkdir(parents=True, exist_ok=True)
    py_path = str(pw_dir / f"{stem}.py")
    # NOTE: screenshot/result paths are no longer built here as strings — the
    # generated script computes them at runtime via SCREENSHOT_DIR, which is
    # anchored to the script's own file location (os.path.dirname(__file__)),
    # so they resolve correctly regardless of the caller's cwd (project root
    # for the live backend, or the script's own folder for script-runner's
    # batch runner).

    has_upload = any(s.get("method") == "upload_file" for s in steps)
    has_click_or_fill = any(s.get("method") in ("click", "fill") for s in steps)

    lines = [
        f"# Auto-generated Playwright script — {stem}",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Source: {Path(json_path).name}",
        f"# Run (from project root): python {py_path}",
        "# Requires: pip install playwright && playwright install chromium",
        "",
        "import asyncio",
        "import os",
        "import json",
        "from playwright.async_api import async_playwright",
        "",
        "# Anchored to this file's own location, NOT the caller's cwd — so this",
        "# script writes screenshots/results to the same place whether it's run",
        "# from the project root (old behavior) or via script-runner/run_scripts.py",
        "# (which sets cwd to this script's own folder, e.g. for batch runs).",
        "_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))",
        f"SCREENSHOT_DIR = os.path.join(_SCRIPT_DIR, 'screenshots', {_py(stem)})",
        "os.makedirs(SCREENSHOT_DIR, exist_ok=True)",
        f"RESULT_PATH = os.path.join(_SCRIPT_DIR, {_py(f'{stem}.result.json')})",
        "",
    ]
    if has_upload:
        lines += [
            "",
            _UPLOAD_HELPER_PY,
            "",
        ]
    if has_click_or_fill:
        lines += [
            "",
            _LOCATOR_HELPER_PY,
            "",
        ]
    lines += [
        "",
        "async def run_test():",
        "    async with async_playwright() as pw:",
        "        browser = await pw.chromium.launch(headless=False)",
        "        context = await browser.new_context(ignore_https_errors=True)",
        "        page = await context.new_page()",
        "",
        "        _step_results = []   # structured per-step outcomes, dumped to RESULT_PATH in finally",
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
        params["_step_id"] = step_id
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

        # --- Portability normalization -----------------------------------------
        # Two recording styles only make sense inside the exact live browser
        # session they were captured in, and silently produce broken/no-op code
        # when replayed standalone later:
        #   - click_by_index: clicks the Nth element of a live-refetched
        #     "interactable elements" snapshot. There's no selector at all to
        #     translate — the index shifts with list length/DOM state — so the
        #     current per-method templates have nothing to emit for it.
        #   - click with a Radix/shadcn auto-generated id (id="radix-_r_X_"):
        #     valid Playwright code, but the id is only valid in the session it
        #     was captured in (Radix's internal mount-order counter renumbers on
        #     every fresh page load).
        # Where we have a visible-text label to fall back to (expected_text, or
        # a quoted phrase in the step description), rewrite to a text-based
        # selector instead — stable across sessions since it doesn't depend on
        # DOM/mount ordering.
        _fallback_label = params.get("expected_text") or _extract_quoted_label(desc)
        if method == "click_by_index":
            # Three possible identity sources for a click_by_index target, all
            # captured by cmd_click_by_index/engine.py at recording time, tried
            # in priority order:
            #  1. element_text — plain buttons/links identified by their own
            #     visible text (e.g. "Log In"). This is the MOST common case for
            #     click_by_index and is checked first; icon buttons naturally
            #     have empty text so they fall through to case 2 unaffected.
            #  2. element_title / element_aria_label — icon-only action button
            #     (View/Edit/Delete), no visible text.
            #  3. Neither present (older recording made before this metadata was
            #     captured, added 2026-07-08/09) — fall back to the
            #     option-selector guess, which is only correct for genuine
            #     combobox/listbox option picks. Kept only for backward
            #     compatibility with old recordings.
            _row_label = _extract_quoted_label(desc)
            _element_text = (params.get("element_text") or "").strip()
            _identity_attr = "title" if params.get("element_title") else (
                "aria-label" if params.get("element_aria_label") else None)
            _identity_value = params.get("element_title") or params.get("element_aria_label")
            # A quoted phrase in the description is only a genuine row_label
            # when it names something OTHER than the target itself — e.g.
            # "row where Name is 'X'" or "click 'X'" on a per-row Edit icon.
            # Plain steps like `Click the "REGISTER" button.` also contain a
            # quoted phrase, but it's just the button's own label restated in
            # quotes — not a row identifier. Without this check, _row_label ==
            # _element_text (both "REGISTER") and _button_text_selector_py
            # wraps the selector in //tr[contains(...,"REGISTER")]/[role=row]/
            # //li[...], which is structurally wrong for a plain submit button
            # that isn't inside any row/list at all, and always times out.
            # Found 2026-07-23 on advantageonlineshopping.com's register form.
            if _row_label and _row_label.strip().casefold() in (
                _element_text.casefold(), (_identity_value or "").strip().casefold()
            ):
                _row_label = None
            if _element_text:
                method = "click"
                params["selector"] = _button_text_selector_py(
                    params.get("element_tag", "button"), _element_text, _row_label
                )
            elif _identity_attr and _identity_value:
                method = "click"
                params["selector"] = _icon_button_selector_py(
                    params.get("element_tag", "button"), _identity_attr, _identity_value, _row_label
                )
            elif _fallback_label:
                method = "click"
                params["selector"] = _text_option_selector_py(_fallback_label)
            else:
                method = "__unsupported__"
        elif method == "click" and "radix-" in str(params.get("selector", "")) and _fallback_label:
            params["selector"] = _text_option_selector_py(_fallback_label)
        # --- end normalization ---------------------------------------------------

        lines.append("")

        if method == "__unsupported__":
            lines.append(
                f"            # STEP {step_id} [{step.get('method')}] — recorded as click_by_index with no "
                f"expected_text/label to fall back to."
            )
            lines.append(
                "            # This method only works inside a live, DOM-refetching MCP session "
                "(clicks the Nth element of a snapshot taken at that moment) and has no stable "
                "Playwright equivalent."
            )
            lines.append(f"            # MANUAL FIX NEEDED: {desc}")
            continue

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
        # Each step gets its own try/except so a failure is recorded with the
        # exact step_id/description/error BEFORE re-raising up to the outer
        # handler (which still stops the whole script — batch-level continue
        # logic lives in script-runner/run_scripts.py, not here).
        lines.append("            try:")

        safe_step_id = re.sub(r"[^A-Za-z0-9_]", "_", str(step_id))

        if method == "screenshot":
            shot_var = f"_shot_{safe_step_id}"
            lines.append(f"                {shot_var} = os.path.join(SCREENSHOT_DIR, {_py(f'step_{step_id}.png')})")
            lines.append(f"                await page.screenshot(path={shot_var})")
            lines.append(
                f"                _step_results.append({{'step_id': {_py(str(step_id))}, "
                f"'description': {_py(desc)}, 'status': 'passed', 'error': None, "
                f"'screenshot': {shot_var}}})"
            )
        else:
            py_line = _method_to_py(method, params)
            if py_line:
                lines.append(textwrap.indent(py_line, "                ").rstrip())
                shot_var = f"_shot_{safe_step_id}"
                lines.append(f"                {shot_var} = os.path.join(SCREENSHOT_DIR, {_py(f'step_{step_id}.png')})")
                lines.append(f"                await page.screenshot(path={shot_var})")
                lines.append(
                    f"                _step_results.append({{'step_id': {_py(str(step_id))}, "
                    f"'description': {_py(desc)}, 'status': 'passed', 'error': None, "
                    f"'screenshot': {shot_var}}})"
                )
            else:
                lines.append(f"                pass  # unrecognized method: {method}")
                lines.append(
                    f"                _step_results.append({{'step_id': {_py(str(step_id))}, "
                    f"'description': {_py(desc)}, 'status': 'passed', 'error': None, 'screenshot': None}})"
                )

        lines.append("            except Exception as _step_err:")
        lines.append(
            f"                _step_results.append({{'step_id': {_py(str(step_id))}, "
            f"'description': {_py(desc)}, 'status': 'failed', 'error': str(_step_err), 'screenshot': None}})"
        )
        lines.append("                raise")

    lines += [
        "",
        "            print('Test completed')",
        "        except Exception as err:",
        "            print(f'Test failed: {err}')",
        "            raise",
        "        finally:",
        "            try:",
        "                with open(RESULT_PATH, 'w', encoding='utf-8') as _rf:",
        f"                    json.dump({{'test_case': {_py(stem)}, 'steps': _step_results}}, _rf, indent=2, ensure_ascii=False)",
        "            except Exception as _report_err:",
        "                print(f'[report] could not write result json: {_report_err}')",
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
                           step_description: str, step_id: int, status: str = "passed",
                           note: str = ""):
        async with self._lock:
            if test_case_id not in self._steps:
                return

            entry = {
                "jsonrpc": "2.0",
                "method": method,
                "step": step_description,
                "status": status,
                "params": params,
                "id": step_id,
                "note": note,
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