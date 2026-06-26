"""
All cmd_* command handlers + register_tool decorator + CMD_MAP.
Depends on: helpers.py, stores.py, credentials.py
"""

import asyncio
import base64
import os
import re
import time
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import pandas as pd
from bs4 import BeautifulSoup
from fastapi import Request
from playwright.async_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from credentials import get_credential_async
from helpers import (
    _find_locator,
    _force_action,
    _select2_pick,
    normalize_selector,
    resolve_toast_type,
    screenshot_to_base64,
)
from stores import Session


# ==================== Upload fixtures helpers ====================

FIXTURES_DIR = Path("data/fixtures")


def _resolve_fixtures(files: list[str]) -> list[str]:
    """Relative paths resolve into data/fixtures/. Absolute paths pass through.
    Raises FileNotFoundError with a clear message if the file is missing —
    so portability breaks loudly, not as an opaque Playwright timeout."""
    resolved = []
    for f in files:
        p = Path(f)
        if not p.is_absolute():
            p = FIXTURES_DIR / f
        if not p.exists():
            raise FileNotFoundError(f"upload file not found: {p} (cwd={Path.cwd()})")
        resolved.append(str(p.resolve()))
    return resolved


async def _verify_uploaded_filename(page, basenames: list[str], timeout: int = 5000) -> bool:
    """Confirm each filename actually landed. Two strategies:
    1. Read input.files[].name across all file inputs (works for direct/nested input).
    2. Fallback: poll the DOM text for the basename (the filename 'chip' a dropzone renders).
    """
    wanted = [Path(b).name for b in basenames]

    in_inputs = await page.evaluate("""() => {
        const names = [];
        for (const inp of document.querySelectorAll('input[type=file]')) {
            if (inp.files) for (const f of inp.files) names.push(f.name);
        }
        return names;
    }""")
    if all(any(w == n or w in n for n in in_inputs) for w in wanted) and in_inputs:
        return True

    deadline = asyncio.get_event_loop().time() + (timeout / 1000)
    while asyncio.get_event_loop().time() < deadline:
        body_txt = (await page.evaluate("() => document.body.innerText || ''")) or ""
        if all(w in body_txt for w in wanted):
            return True
        await asyncio.sleep(0.25)
    return False


# ==================== Tool Registry ====================

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_tool(name: str, description: str, input_schema: Optional[Dict] = None):
    """Declarative tool metadata for MCP compliance. Additive — does NOT change execution."""
    def decorator(func: Callable):
        TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema or {
                "type": "object",
                "properties": {},
                "required": []
            },
            "handler": func,
        }
        return func
    return decorator


# ==================== Toast Capture JS ====================

_ARM_JS = """() => {
  const old=document.getElementById('__amethyst_pin'); if(old) old.remove();
  window.__toastCap = new Promise(resolve => {
    const RE = /(swal2-popup|swal2-toast|toast|toastify|notyf__toast|MuiAlert-root|ant-message-notice|ant-notification-notice|v-snackbar__content|chakra-toast|alert-success|alert-danger|alert-warning)/i;
    const isNotif = el => el instanceof HTMLElement &&
      (el.matches('[role=alert],[role=status],[aria-live=assertive],[aria-live=polite]') || RE.test(el.className||''));
    const visible = el => { const s=getComputedStyle(el), r=el.getBoundingClientRect();
      return el.offsetParent!==null && s.display!=='none' && s.visibility!=='hidden' && +s.opacity>=0.1 && r.width>0 && r.height>0; };
    const grab = el => {
      try { if (window.Swal?.isVisible?.()) Swal.stopTimer(); } catch(e){}
      const hay=(el.className+' '+el.outerHTML).toLowerCase(), txt=(el.innerText||'').trim().replace(/\\s+/g,' '), t=txt.toLowerCase();
      const OK=/success|saved|created|updated|deleted|berhasil|sukses|tersimpan|disimpan|terhapus/;
      const ERR=/error|danger|fail|invalid|warning|gagal|salah|tidak|wajib|required/;
      let type='unknown';
      if(/swal2-success|alert-success|toast-success|--success|_success/.test(hay)||OK.test(t))type='success';
      else if(/swal2-error|alert-danger|toast-error|--error|_error|alert-warning/.test(hay)||ERR.test(t))type='error';
      const r=el.getBoundingClientRect();
      const d=document.createElement('div'); d.id='__amethyst_pin'; d.innerHTML=el.outerHTML;
      d.style.cssText=(r.width>0 ? `position:fixed;left:${r.left}px;top:${r.top}px;width:${r.width}px;`
                                 : `position:fixed;top:12px;right:12px;`)+'z-index:2147483647;pointer-events:none;';
      document.body.appendChild(d);
      el.style.opacity='0';
      return {type, text:txt};
    };
    const hasText = el => {
      const t = (el.innerText||'').trim();
      return t.length > 1 && !/^[×x✕✖✗]$/i.test(t);
    };
    const scan = n => { if(isNotif(n)&&visible(n)&&hasText(n))return n;
      if(n.querySelectorAll) for(const c of n.querySelectorAll('*')) if(isNotif(c)&&visible(c)&&hasText(c))return c; return null; };
    const obs = new MutationObserver(ms => { for(const m of ms) for(const n of m.addedNodes){
      const hit=scan(n); if(hit){obs.disconnect(); resolve(grab(hit)); return;} }});
    obs.observe(document.body, {childList:true, subtree:true});
    setTimeout(() => {
      const all=[...document.querySelectorAll('[role=alert],[role=status],[class*=toast],[class*=swal2],[class*=alert],[class*=snackbar],[class*=notyf]')].filter(el => visible(el) && hasText(el));
      if(all.length){ obs.disconnect(); resolve(grab(all[all.length-1])); }
    }, 50);
  });
}"""

_RACE_JS = """(ms) => Promise.race([
  (window.__toastCap || new Promise(()=>{})),
  new Promise(r => setTimeout(() => r(null), ms))
])"""

_FREEZE_JS = """(sel) => { const el=document.querySelector(sel); if(!el) return null;
  try { if (window.Swal?.isVisible?.()) Swal.stopTimer(); } catch(e){}
  const old=document.getElementById('__amethyst_pin'); if(old) old.remove();
  const r=el.getBoundingClientRect();
  const d=document.createElement('div'); d.id='__amethyst_pin'; d.innerHTML=el.outerHTML;
  d.style.cssText=(r.width>0 ? `position:fixed;left:${r.left}px;top:${r.top}px;width:${r.width}px;`
                              : `position:fixed;top:12px;right:12px;`)+'z-index:2147483647;pointer-events:none;';
  document.body.appendChild(d); return true; }"""

_CLASSIFY_JS = """(sel) => { const el=document.querySelector(sel); if(!el) return null;
  const hay=(el.className+' '+el.outerHTML).toLowerCase(), txt=(el.innerText||'').trim().replace(/\\s+/g,' '), t=txt.toLowerCase();
  const OK=/success|saved|created|updated|deleted|berhasil|sukses|tersimpan|disimpan|terhapus/;
  const ERR=/error|danger|fail|invalid|warning|gagal|salah|tidak|wajib|required/;
  let type='unknown';
  if(/swal2-success|alert-success|toast-success|--success|_success/.test(hay)||OK.test(t))type='success';
  else if(/swal2-error|alert-danger|toast-error|--error|_error|alert-warning/.test(hay)||ERR.test(t))type='error';
  return {type, text:txt}; }"""


# ==================== Command Handlers ====================

@register_tool(
    "select_option",
    "Select an option from a native <select> dropdown or a Select2 custom widget by value or visible text.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "value": {"type": "string"},
            "text": {"type": "string"},
        },
        "required": ["selector"]
    }
)
async def cmd_select_option(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    value = params.get("value", "") or params.get("text", "")
    async with session.lock:
        handled = await _select2_pick(session.page, sel, value)
        if not handled:
            is_select = await session.page.evaluate("""
                (sel) => {
                    try {
                        function isVisible(node) {
                            const s = window.getComputedStyle(node);
                            return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
                        }
                        let el = null;
                        if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                            const xsel = sel.replace('xpath=','');
                            const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            for (let i = 0; i < r.snapshotLength; i++) {
                                const node = r.snapshotItem(i);
                                if (isVisible(node)) { el = node; break; }
                            }
                        } else {
                            const nodes = document.querySelectorAll(sel);
                            for (const node of nodes) {
                                if (isVisible(node)) { el = node; break; }
                            }
                        }
                        return el?.tagName === 'SELECT';
                    } catch(e) { return false; }
                }
            """, sel)
            if is_select:
                try:
                    await session.page.select_option(sel, label=value)
                except Exception:
                    await session.page.select_option(sel, value=value)
            else:
                raise Exception(f"select_option failed: could not find Select2 or native <select> for value='{value}'")
        await asyncio.sleep(0.5)
    return {"selector": sel, "value": value}


@register_tool(
    "navigate",
    "Navigate the browser to a given URL. Waits for DOMContentLoaded, load, and networkidle.",
    {
        "type": "object",
        "properties": {
            "url": {"type": "string"}
        },
        "required": ["url"]
    }
)
async def cmd_navigate(params: dict, session: Session):
    async with session.lock:
        await session.page.evaluate("() => { const p=document.getElementById('__amethyst_pin'); if(p) p.remove(); }")
        await session.page.goto(params["url"], timeout=30000, wait_until="domcontentloaded")
        try:
            await session.page.wait_for_load_state("load", timeout=10000)
        except Exception:
            pass
        try:
            await session.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
    return {"url": params["url"]}


@register_tool(
    "click",
    "Click an element using a CSS or XPath selector. Optionally captures post-click toast/notification.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "capture_toast": {"type": "boolean"},
            "toast_selector": {"type": "string"},
            "expected_text": {"type": "string"},
            "toast_timeout": {"type": "integer"},
            "require_toast": {"type": "boolean"},
            "fail_on_error": {"type": "boolean"},
        },
        "required": ["selector"]
    }
)
async def cmd_click(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    resolved = None

    x = params.get("x")
    y = params.get("y")
    if x is not None and y is not None:
        async with session.lock:
            loc = session.page.locator(sel).first
            await loc.click(position={"x": int(x), "y": int(y)})
            await asyncio.sleep(0.3)
        return {"selector": sel, "x": x, "y": y}

    capture_toast  = bool(params.get("capture_toast", False))
    toast_selector = params.get("toast_selector") or ""
    expected_text  = params.get("expected_text") or ""
    toast_timeout  = int(params.get("toast_timeout", 6000))
    require_toast  = bool(params.get("require_toast", True))
    fail_on_error  = bool(params.get("fail_on_error", True))

    async with session.lock:
        _t0 = time.monotonic()
        await session.page.evaluate("() => { const p=document.getElementById('__amethyst_pin'); if(p) p.remove(); }")
        try:
            await session.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            pass
        try:
            await session.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass

        is_hidden_option = await session.page.evaluate("""
            (sel) => {
                try {
                    function isSelectVisible(node) {
                        const s = node.closest('select');
                        if (!s) return false;
                        const style = window.getComputedStyle(s);
                        return s.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden';
                    }
                    let el = null;
                    if (sel.startsWith('//')) {
                        const r = document.evaluate(sel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                        if (r.snapshotLength > 1) console.warn('[cmd_click] is_hidden_option: ' + r.snapshotLength + ' <option> candidates for: ' + sel);
                        for (let i = 0; i < r.snapshotLength; i++) {
                            const node = r.snapshotItem(i);
                            if (node.tagName === 'OPTION' && isSelectVisible(node)) { el = node; break; }
                        }
                        if (!el && r.snapshotLength > 0) { console.warn('[cmd_click] is_hidden_option: no visible-parent candidate, falling back to first match for: ' + sel); el = r.snapshotItem(0); }
                    } else {
                        const nodes = document.querySelectorAll(sel);
                        if (nodes.length > 1) console.warn('[cmd_click] is_hidden_option: ' + nodes.length + ' <option> candidates for: ' + sel);
                        for (const node of nodes) {
                            if (node.tagName === 'OPTION' && isSelectVisible(node)) { el = node; break; }
                        }
                        if (!el && nodes.length > 0) { console.warn('[cmd_click] is_hidden_option: no visible-parent candidate, falling back to first match for: ' + sel); el = nodes[0]; }
                    }
                    return el ? el.tagName === 'OPTION' : false;
                } catch(e) { return false; }
            }
        """, sel.replace("xpath=", ""))

        if is_hidden_option:
            option_text = await session.page.evaluate("""
                (sel) => {
                    try {
                        function isSelectVisible(node) {
                            const s = node.closest('select');
                            if (!s) return false;
                            const style = window.getComputedStyle(s);
                            return s.offsetParent !== null && style.display !== 'none' && style.visibility !== 'hidden';
                        }
                        let el = null;
                        if (sel.startsWith('//')) {
                            const r = document.evaluate(sel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            for (let i = 0; i < r.snapshotLength; i++) {
                                const node = r.snapshotItem(i);
                                if (node.tagName === 'OPTION' && isSelectVisible(node)) { el = node; break; }
                            }
                            if (!el && r.snapshotLength > 0) { console.warn('[cmd_click] option_text: no visible-parent candidate, falling back to first match for: ' + sel); el = r.snapshotItem(0); }
                        } else {
                            const nodes = document.querySelectorAll(sel);
                            for (const node of nodes) {
                                if (node.tagName === 'OPTION' && isSelectVisible(node)) { el = node; break; }
                            }
                            if (!el && nodes.length > 0) { console.warn('[cmd_click] option_text: no visible-parent candidate, falling back to first match for: ' + sel); el = nodes[0]; }
                        }
                        return el ? el.textContent.trim() : '';
                    } catch(e) { return ''; }
                }
            """, sel.replace("xpath=", ""))
            if option_text:
                handled = await _select2_pick(session.page, sel, option_text)
                if handled:
                    await asyncio.sleep(0.5)
                    try:
                        await session.page.wait_for_load_state("load", timeout=10000)
                    except Exception:
                        pass
                    return {"selector": sel, "resolved_selector": None}

        if capture_toast and not toast_selector:
            await session.page.evaluate(_ARM_JS)

        try:
            await session.page.locator(sel).first.wait_for(state="visible", timeout=3000)
        except Exception:
            pass

        loc = await _find_locator(session.page, sel)
        try:
            await loc.click(timeout=8000)
            success = True
            resolved = None
        except (PlaywrightTimeoutError, PlaywrightError):
            # Native actionability check failed — fall back to JS force-click.
            # Known limitation: _force_action's isVisible() does not check disabled
            # state or pointer-events, so a disabled-but-rendered element can
            # false-pass here. That is a pre-existing issue, out of scope for this change.
            result = await _force_action(session.page, sel, "click")
            success = bool(result)
            resolved = result.get("resolved") if isinstance(result, dict) else None
            if not success:
                raise ValueError(
                    f"Element not found or not clickable: {sel!r}. "
                    "Use get_interactable_elements to verify the selector."
                )

        if capture_toast:
            print(f"[TOAST TIMING] click returned at t={time.monotonic()-_t0:.2f}s")

        if success:
            await asyncio.sleep(0.5)

        # ── Toast capture: race against the FULL window immediately after click. ──
        # No "load" wait inserted here — for SPA actions (no real navigation),
        # the browser "load" event may have already fired on initial page load
        # and resolves instantly, telling us nothing about whether the async
        # action (API call → toast render) has completed. Racing immediately
        # with the full toast_timeout avoids burning the toast's visible window
        # on a wait that doesn't correspond to the actual async operation.
        if capture_toast:
            print(f"[TOAST TIMING] entering toast capture block at t={time.monotonic()-_t0:.2f}s")
            info = None
            navigated_away = False

            def _is_nav_destroyed_error(exc: Exception) -> bool:
                msg = str(exc)
                return (
                    "Execution context was destroyed" in msg
                    or "Target page" in msg
                    or "Target closed" in msg
                )

            if toast_selector:
                try:
                    await session.page.wait_for_selector(toast_selector, state="visible", timeout=toast_timeout)
                    await session.page.evaluate(_FREEZE_JS, toast_selector)
                    info = await session.page.evaluate(_CLASSIFY_JS, toast_selector)
                except Exception as e:
                    if _is_nav_destroyed_error(e):
                        navigated_away = True
                        print(f"[TOAST TIMING] toast_selector race interrupted by navigation at t={time.monotonic()-_t0:.2f}s")
                    info = None
            else:
                print(f"[TOAST TIMING] starting race (timeout={toast_timeout}ms) at t={time.monotonic()-_t0:.2f}s")
                try:
                    info = await session.page.evaluate(_RACE_JS, toast_timeout)
                    print(f"[TOAST TIMING] race resolved at t={time.monotonic()-_t0:.2f}s, info={info}")
                except Exception as e:
                    if _is_nav_destroyed_error(e):
                        navigated_away = True
                        print(f"[TOAST TIMING] race interrupted by navigation at t={time.monotonic()-_t0:.2f}s")
                    info = None

            if navigated_away:
                # The click triggered a real page navigation while the toast race
                # was still running. The click itself already succeeded (it's what
                # caused the navigation) — don't fail the step over a toast we no
                # longer have a page to look for. Report success, no toast info.
                try:
                    await session.page.wait_for_load_state("load", timeout=10000)
                except Exception:
                    pass
                try:
                    await session.page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                print(f"[TOAST TIMING] returning success (navigated away) at t={time.monotonic()-_t0:.2f}s")
                return {
                    "selector": sel, "resolved_selector": resolved,
                    "toast_found": False, "toast_type": "navigated",
                    "toast_text": "", "passed": True,
                    "note": "page navigated before toast capture completed — click likely succeeded",
                }

            toast_found = info is not None
            toast_type  = info["type"] if toast_found else "none"
            toast_text  = info["text"] if toast_found else ""
            toast_type  = resolve_toast_type(toast_type, toast_text)

            if toast_found:
                await asyncio.sleep(0.3)  # let CSS fade-in transition settle before screenshot

            if expected_text:
                passed = expected_text.lower() in toast_text.lower()
            else:
                passed = (toast_type == "success")

            if not toast_found and require_toast:
                raise AssertionError(f"No notification appeared within {toast_timeout}ms — step produced no feedback")
            if toast_found and not passed and fail_on_error:
                raise AssertionError(f"Step failed — toast_type={toast_type!r}, text={toast_text!r}")

            try:
                await session.page.wait_for_load_state("load", timeout=5000)
            except Exception:
                pass
            try:
                await session.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass

            print(f"[TOAST TIMING] about to return at t={time.monotonic()-_t0:.2f}s")
            return {
                "selector": sel, "resolved_selector": resolved,
                "toast_found": toast_found, "toast_type": toast_type,
                "toast_text": toast_text, "passed": passed,
            }

        try:
            await session.page.wait_for_load_state("load", timeout=10000)
        except Exception:
            pass
        try:
            await session.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
    return {"selector": sel, "resolved_selector": resolved}


@register_tool(
    "click_at_position",
    "Click at specific x,y coordinates relative to an element. Supports multiple clicks via 'clicks' array.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "x": {"type": "number"},
            "y": {"type": "number"},
            "clicks": {"type": "array", "items": {"type": "object"}},
        },
        "required": ["selector"]
    }
)
async def cmd_click_at_position(params: dict, session: Session):
    sel = params.get("selector", ".mapwrap svg")
    clicks = params.get("clicks")
    if not clicks:
        clicks = [{"x": params.get("x", 80), "y": params.get("y", 100)}]
    async with session.lock:
        loc = session.page.locator(sel).first
        for point in clicks:
            await loc.click(position={"x": int(point["x"]), "y": int(point["y"])})
            await asyncio.sleep(0.3)
    return {"selector": sel, "clicks": clicks, "count": len(clicks)}


@register_tool(
    "fill",
    "Fill a text input or textarea. Tries DOM injection first, falls back to Playwright locator.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "text": {"type": "string"},
        },
        "required": ["selector", "text"]
    }
)
async def cmd_fill(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    text = params.get("text", "")
    resolved = None
    async with session.lock:
        try:
            await session.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception:
            pass
        try:
            await session.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass

        result = await _force_action(session.page, sel, "fill", text)
        success = bool(result)
        resolved = result.get("resolved") if isinstance(result, dict) else None

        if success:
            await asyncio.sleep(0.5)
        else:
            loc = await _find_locator(session.page, sel)
            try:
                await loc.wait_for(state="visible", timeout=30000)
                await loc.fill(text)
            except Exception as e:
                raise ValueError(
                    f"Element not found or not interactable after 30s: {sel!r}. "
                    "Use get_interactable_elements to verify the selector."
                ) from e
    return {"selector": sel, "text": text, "resolved_selector": resolved}


@register_tool(
    "hover",
    "Hover the mouse over an element to trigger hover states, tooltips, or dropdown menus.",
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}
)
async def cmd_hover(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        await loc.hover()
    return {"selector": sel}


@register_tool(
    "get_text",
    "Get the text content of a single element. Tries DOM injection first, falls back to Playwright.",
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}
)
async def cmd_get_text(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        text = await _force_action(session.page, sel, "text")
        if not text:
            loc = await _find_locator(session.page, sel)
            text = await loc.text_content()
    return {"text": text}


@register_tool(
    "get_all_text",
    "Get the text content of ALL elements matching a selector.",
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}
)
async def cmd_get_all_text(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        els = await loc.all()
        texts = [await e.text_content() for e in els]
    return {"texts": texts}


@register_tool(
    "screenshot",
    "Capture a screenshot of the current page.",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "full_page": {"type": "boolean"},
            "return_base64": {"type": "boolean"},
        },
        "required": []
    }
)
async def cmd_screenshot(params: dict, session: Session):
    default_path = f"data/saved_screenshots/MCP_screenshots/screenshot_{datetime.now().strftime('%d%m%Y_%H%M%S')}.png"
    path = params.get("path", default_path)
    full_page = params.get("full_page", False)
    return_base64 = params.get("return_base64", False)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    async with session.lock:
        screenshot_bytes = await session.page.screenshot(path=path, full_page=full_page)
    result = {"path": path}
    if return_base64:
        result["screenshot"] = base64.b64encode(screenshot_bytes).decode()
        result["format"] = "base64"
    return result


@register_tool(
    "get_page_content",
    "Return the full raw HTML source of the current page.",
    {"type": "object", "properties": {}, "required": []}
)
async def cmd_get_page_content(params: dict, session: Session):
    async with session.lock:
        content = await session.page.content()
    return {"content": content}


@register_tool(
    "get_page_info",
    "Return the current page title and URL.",
    {"type": "object", "properties": {}, "required": []}
)
async def cmd_get_page_info(params: dict, session: Session):
    async with session.lock:
        return {"title": await session.page.title(), "url": session.page.url}


@register_tool(
    "close_session",
    "Close and destroy the browser session, releasing all browser resources.",
    {
        "type": "object",
        "properties": {"sessionId": {"type": "string"}},
        "required": ["sessionId"]
    }
)
async def cmd_close_session(params: dict, session: Session, request: Request):
    session_id = params["sessionId"]
    await request.app.state.sessions.close(session_id)
    return {"status": "closed"}


@register_tool(
    "get_interactable_elements",
    "Return all visible interactable elements on the current page across all frames.",
    {"type": "object", "properties": {}, "required": []}
)
async def cmd_get_interactable_elements(params: dict, session: Session):
    async with session.lock:
        try:
            await session.page.wait_for_load_state("load", timeout=15000)
        except Exception:
            pass
        try:
            await session.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        await asyncio.sleep(0.5)

        result = []
        for frame in session.page.frames:
            try:
                elements = await frame.query_selector_all(
                    "button, a, input, textarea, select, "
                    "[role='button'], [role='link'], [role='combobox'], [role='listbox'], "
                    "span[role='combobox'], span[role='button'], span[tabindex], "
                    "[data-act], [data-link]"
                )
            except Exception:
                continue

            for el in elements:
                try:
                    if not await el.is_visible():
                        continue
                except Exception:
                    continue
                try:
                    aria_hidden = await el.get_attribute("aria-hidden")
                    tabindex = await el.get_attribute("tabindex")
                    if aria_hidden == "true" and tabindex == "-1":
                        continue

                    tag_name = await el.evaluate("e => e.tagName")
                    text_content = (await el.text_content() or "").strip()
                    get_id = await el.get_attribute("id")
                    get_name = await el.get_attribute("name")
                    get_href = await el.get_attribute("href")
                    aria_label = await el.get_attribute("aria-label")
                    placeholder = await el.get_attribute("placeholder")
                    data_act = await el.get_attribute("data-act")

                    if tag_name not in ("INPUT", "TEXTAREA", "SELECT") and not (get_id or get_name or text_content or get_href or aria_label or placeholder):
                        continue

                    direct_text = await el.evaluate(
                        "e => Array.from(e.childNodes)"
                        ".filter(n => n.nodeType === 3)"
                        ".map(n => n.textContent.trim())"
                        ".filter(Boolean).join(' ')"
                    )

                    if get_id:
                        _suggested = f'xpath=//{tag_name.lower()}[@id="{get_id}"]'
                    elif get_name:
                        _suggested = f'xpath=//{tag_name.lower()}[@name="{get_name}"]'
                    elif aria_label:
                        _suggested = f'xpath=//{tag_name.lower()}[@aria-label="{aria_label}"]'
                    elif placeholder:
                        _suggested = f'xpath=//{tag_name.lower()}[@placeholder="{placeholder}"]'
                    elif direct_text:
                        _suggested = f'xpath=//{tag_name.lower()}[text()[normalize-space(.) = "{direct_text}"]]'
                    elif data_act and tag_name not in ("BUTTON", "A", "INPUT", "SELECT", "TEXTAREA"):
                        _suggested = f'xpath=//{tag_name.lower()}[@data-act="{data_act}" and .//*[normalize-space(.) = "{text_content.split(chr(10))[0].strip()}"]]'
                    elif text_content:
                        first_line = text_content.split('\n')[0].strip()
                        _suggested = f'xpath=//{tag_name.lower()}[.//text()[normalize-space(.) = "{first_line}"]]' if first_line else ""
                    else:
                        _suggested = ""

                    input_type = await el.get_attribute("type") if tag_name == "INPUT" else None
                    input_value = await el.evaluate("e => e.value ?? null") if tag_name in ("INPUT", "TEXTAREA", "SELECT") else None

                    result.append({
                        "id": get_id, "tag": tag_name, "type": input_type, "value": input_value,
                        "text": text_content, "disabled": await el.evaluate("e => !!e.disabled"),
                        "name": get_name, "href": get_href,
                        "role": await el.get_attribute("role"),
                        "aria_controls": await el.get_attribute("aria-controls"),
                        "tabindex": tabindex, "aria_hidden": aria_hidden,
                        "aria_label": aria_label, "placeholder": placeholder,
                        "data_act": data_act, "visible": True,
                        "in_iframe": frame != session.page.main_frame,
                        "suggested_selector": _suggested,
                    })
                except Exception:
                    continue
    return {"count": len(result), "elements": result}


async def cmd_click_by_index(params: dict, session: Session):
    index = params.get("index")
    if index is None:
        return {"error": "Missing required param: index"}
    elements_result = await cmd_get_interactable_elements(params, session)
    elements = elements_result.get("elements", [])
    if index < 0 or index >= len(elements):
        return {"error": f"Index {index} out of range", "total_elements": len(elements)}
    target = elements[index]
    selector = target.get("suggested_selector", "")
    if not selector:
        return {"error": f"Element at index {index} has no usable selector", "element": target}
    async with session.lock:
        await session.page.click(selector)
    return {"status": "clicked", "index": index, "selector": selector,
            "element_text": target.get("text", ""), "element_tag": target.get("tag", "")}


def _extract_text_lines(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [phrase.strip() for line in text.splitlines()
             for phrase in line.split("  ") if phrase.strip()]
    return "\n".join(lines)


async def _extract_and_save_txt(content: str, ts: str) -> dict:
    text_clean = _extract_text_lines(content)
    os.makedirs("saved_txt", exist_ok=True)
    filename = f"saved_txt/txt_crawl_{ts}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text_clean)
    return {"txt_saved": True, "filename": filename, "text_length": len(text_clean)}


@register_tool(
    "get_page_content_and_save_csv",
    "Scrape all HTML tables from the current page and save each as a CSV file.",
    {"type": "object", "properties": {}, "required": []}
)
async def cmd_get_page_content_and_save_csv(params: dict, session: Session):
    async with session.lock:
        try:
            await session.page.wait_for_load_state("load", timeout=15000)
        except Exception:
            pass
        try:
            await session.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            print(f"[WARNING] wait_for_load_state: {e}")
        content = await session.page.content()

    soup = BeautifulSoup(content, "html.parser")
    tables = soup.find_all("table")
    os.makedirs("saved_csv", exist_ok=True)
    ts = datetime.now().strftime("%d%m%Y_%H%M%S")

    if tables:
        saved_files = []
        total_rows = 0
        for i, table in enumerate(tables):
            try:
                df = pd.read_html(StringIO(str(table)))[0].dropna(how="all").reset_index(drop=True)
                suffix = f"_table_{i + 1}" if len(tables) > 1 else ""
                filename = f"saved_csv/csv_crawl_{ts}{suffix}.csv"
                df.to_csv(filename, index=False, encoding="utf-8-sig")
                saved_files.append({"filename": filename, "rows": len(df), "columns": list(df.columns)})
                total_rows += len(df)
            except Exception as e:
                print(f"[WARNING] Could not parse table {i + 1}: {e}")
                continue
        return {"csv_saved": True, "files": saved_files, "total_rows": total_rows,
                "tables": len(tables), "type": "table_data"}
    else:
        txt_result = await _extract_and_save_txt(content, ts)
        return {"csv_saved": False, "tables": 0, "type": "text_content", **txt_result}


@register_tool(
    "get_page_content_and_save_txt",
    "Strip scripts and styles from the current page HTML and save the clean plain text.",
    {"type": "object", "properties": {}, "required": []}
)
async def cmd_get_page_content_and_save_txt(params: dict, session: Session):
    async with session.lock:
        try:
            await session.page.wait_for_load_state("load", timeout=15000)
        except Exception:
            pass
        try:
            await session.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        content = await session.page.content()
    ts = datetime.now().strftime("%d%m%Y_%H%M%S")
    return await _extract_and_save_txt(content, ts)


@register_tool(
    "wait_for_load",
    "Wait for the page to reach a specific load state.",
    {
        "type": "object",
        "properties": {
            "state": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        "required": []
    }
)
async def cmd_wait_for_load(params: dict, session: Session):
    state = params.get("state", "load")
    timeout = params.get("timeout", 10000)
    async with session.lock:
        await session.page.wait_for_load_state(state=state, timeout=timeout)
    return {"state": state, "timeout": timeout}


@register_tool(
    "wait_for_selector",
    "Wait until an element matching the selector reaches the given state.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "state": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        "required": ["selector"]
    }
)
async def cmd_wait_for_selector(params: dict, session: Session):
    selector = normalize_selector(params["selector"])
    state = params.get("state", "visible")
    timeout = params.get("timeout", 10000)
    async with session.lock:
        loc = await _find_locator(session.page, selector)
        await loc.wait_for(state=state, timeout=timeout)
    return {"selector": selector, "state": state, "timeout": timeout}


async def cmd_execute_js(params: dict, session: Session):
    script = params.get("script", "")
    async with session.lock:
        result = await session.page.evaluate(script)
    return {"result": str(result)}


@register_tool(
    "press_key",
    "Press a keyboard key on the page.",
    {"type": "object", "properties": {"key": {"type": "string"}}, "required": []}
)
async def cmd_press_key(params: dict, session: Session):
    key = params.get("key", "Escape")
    async with session.lock:
        await session.page.keyboard.press(key)
        await asyncio.sleep(0.4)  
    return {"key": key}


@register_tool(
    "get_credentials",
    "Fetch decrypted username and password from the remote credential API by credential name.",
    {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"]
    }
)
async def cmd_get_credentials(params: dict, session: Session):
    name = params.get("name", "")
    cred = await get_credential_async(name)
    return cred


@register_tool(
    "scroll_to_element",
    "Scroll an element into the visible viewport before clicking or interacting with it.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        "required": ["selector"]
    }
)
async def cmd_scroll_to_element(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        await loc.scroll_into_view_if_needed(timeout=params.get("timeout", 5000))
    return {"selector": sel, "scrolled": True}


@register_tool(
    "double_click",
    "Double-click an element identified by a CSS or XPath selector.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        "required": ["selector"]
    }
)
async def cmd_double_click(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        await loc.dblclick(timeout=params.get("timeout", 10000))
    return {"selector": sel, "double_clicked": True}


@register_tool(
    "clear_input",
    "Clear a text input by triple-clicking to select all then pressing Backspace.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        "required": ["selector"]
    }
)
async def cmd_clear_input(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        await loc.click(click_count=3, timeout=params.get("timeout", 10000))
        await session.page.keyboard.press("Backspace")
    return {"selector": sel, "cleared": True}


@register_tool(
    "get_attribute",
    "Read the value of a specific HTML attribute from an element.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "attribute": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        "required": ["selector", "attribute"]
    }
)
async def cmd_get_attribute(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    attr = params["attribute"]
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        value = await loc.get_attribute(attr, timeout=params.get("timeout", 10000))
    return {"selector": sel, "attribute": attr, "value": value}


@register_tool(
    "assert_text",
    "Assert that an element's text content matches the expected string.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "expected": {"type": "string"},
            "exact": {"type": "boolean"},
            "timeout": {"type": "integer"},
        },
        "required": ["selector", "expected"]
    }
)
async def cmd_assert_text(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    expected = params["expected"]
    exact = params.get("exact", False)
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        actual = (await loc.text_content(timeout=params.get("timeout", 10000)) or "").strip()
    match = (actual == expected) if exact else (expected in actual)
    if not match:
        raise AssertionError(
            f"assert_text failed — selector: {sel!r}\n"
            f"  expected: {expected!r}\n"
            f"  actual:   {actual!r}"
        )
    return {"selector": sel, "expected": expected, "actual": actual, "passed": True}


@register_tool(
    "assert_visible",
    "Assert that an element is visible on the page. "
    "If the selector uses exact text matching and fails, automatically retries with a contains() fallback.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "timeout":  {"type": "integer", "description": "Max ms to wait for element (default 5000)."},
        },
        "required": ["selector"]
    }
)
async def cmd_assert_visible(params: dict, session: Session):
    sel     = normalize_selector(params["selector"])
    timeout = int(params.get("timeout", 5000))

    async def _check_visible(selector: str) -> bool:
        try:
            loc = session.page.locator(selector)
            await loc.first.wait_for(state="visible", timeout=timeout)
            return await loc.first.is_visible()
        except Exception:
            return False

    async with session.lock:
        visible = await _check_visible(sel)

        # Fallback: if exact text-match XPath failed, retry with contains()
        fallback_sel = None
        if not visible and 'normalize-space(.) =' in sel:
            import re as _re
            m = _re.search(r'normalize-space\(\.\)\s*=\s*["\'](.+?)["\']', sel)
            if m:
                text_fragment = m.group(1)[:80]
                fallback_sel = f'xpath=//*[contains(normalize-space(.), "{text_fragment}")]'
                visible = await _check_visible(fallback_sel)

    if not visible:
        raise AssertionError(f"assert_visible failed — element not visible: {sel!r}")
    return {"selector": sel, "fallback_selector": fallback_sel, "visible": True, "passed": True}


@register_tool(
    "assert_not_visible",
    "Assert that an element is NOT visible (hidden or absent from the page).",
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}
)
async def cmd_assert_not_visible(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = session.page.locator(sel)
        try:
            count = await loc.count()
        except Exception:
            count = 0
        visible = False
        if count > 0:
            visible = await loc.first.is_visible()
    if visible:
        raise AssertionError(f"assert_not_visible failed — element IS visible: {sel!r}")
    return {"selector": sel, "visible": False, "passed": True}


@register_tool(
    "assert_disabled",
    "Assert that an element is disabled.",
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}
)
async def cmd_assert_disabled(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        disabled = await loc.is_disabled()
    if not disabled:
        raise AssertionError(f"assert_disabled failed — element is enabled: {sel!r}")
    return {"selector": sel, "disabled": True, "passed": True}


@register_tool(
    "assert_url",
    "Assert that the current page URL contains the expected substring. Waits for navigation if needed.",
    {
        "type": "object",
        "properties": {
            "expected": {"type": "string"},
            "timeout": {"type": "integer"},
        },
        "required": ["expected"]
    }
)
async def cmd_assert_url(params: dict, session: Session):
    expected = params["expected"]
    timeout = int(params.get("timeout", 8000))
    try:
        await session.page.wait_for_url(f"**/*{expected}*", timeout=timeout)
    except Exception:
        pass  # fall through to final check below for the exact error message
    url = session.page.url
    if expected not in url:
        raise AssertionError(f"assert_url failed — expected {expected!r} in URL, got: {url!r}")
    return {"expected": expected, "actual": url, "passed": True}


@register_tool(
    "assert_toast",
    "Wait for a toast/notification to appear on the page and validate its text or type. "
    "Use this as a standalone step right after clicking submit/create/delete. "
    "Supports SweetAlert2, Toastify, Notyf, MUI Alert, Ant Design, Chakra, and any role=alert element.",
    {
        "type": "object",
        "properties": {
            "expected_text":  {"type": "string",  "description": "Substring to find in the toast text. If omitted, just checks that a success-type toast appeared."},
            "toast_selector": {"type": "string",  "description": "Optional CSS/XPath selector for the specific toast element. Auto-detected if omitted."},
            "timeout":        {"type": "integer", "description": "Max ms to wait for the toast to appear (default 6000)."},
            "require_toast":  {"type": "boolean", "description": "Throw error if no toast appears at all (default true)."},
            "fail_on_error":  {"type": "boolean", "description": "Throw error if toast appears but text/type does not match (default true)."},
        },
        "required": []
    }
)
async def cmd_assert_toast(params: dict, session: Session):
    expected_text  = params.get("expected_text") or ""
    toast_selector = params.get("toast_selector") or ""
    timeout        = int(params.get("timeout", 6000))
    require_toast  = bool(params.get("require_toast", True))
    fail_on_error  = bool(params.get("fail_on_error", True))

    async with session.lock:
        info = None
        if toast_selector:
            try:
                await session.page.wait_for_selector(toast_selector, state="visible", timeout=timeout)
                await session.page.evaluate(_FREEZE_JS, toast_selector)
                info = await session.page.evaluate(_CLASSIFY_JS, toast_selector)
            except Exception:
                info = None
        else:
            # Arm the MutationObserver listener first (catches toasts that appear after this)
            await session.page.evaluate(_ARM_JS)
            # Check if a toast is already visible right now
            info = await session.page.evaluate(_RACE_JS, 1500)
            if info is None:
                # Re-arm and wait for the remainder of the timeout
                await session.page.evaluate(_ARM_JS)
                remaining = max(timeout - 1500, 1000)
                info = await session.page.evaluate(_RACE_JS, remaining)

    toast_found = info is not None
    toast_type  = info["type"] if toast_found else "none"
    toast_text  = info["text"] if toast_found else ""
    toast_type  = resolve_toast_type(toast_type, toast_text)

    if expected_text:
        passed = expected_text.lower() in toast_text.lower()
    else:
        passed = (toast_type == "success")

    if not toast_found and require_toast:
        raise AssertionError(f"assert_toast failed — no notification appeared within {timeout}ms")
    if toast_found and not passed and fail_on_error:
        raise AssertionError(
            f"assert_toast failed — toast_type={toast_type!r}, text={toast_text!r}"
            + (f", expected_text={expected_text!r}" if expected_text else "")
        )

    return {
        "toast_found": toast_found,
        "toast_type":  toast_type,
        "toast_text":  toast_text,
        "passed":      passed,
    }


@register_tool(
    "upload_file",
    "Upload one or more files. Auto-detects the upload mechanism: (1) target IS a file input → set directly; "
    "(2) target is a dropzone/container wrapping a hidden file input → set on that input; "
    "(3) clicking the target opens a file chooser → intercept it. "
    "Relative file paths resolve into data/fixtures/. Verifies the filename landed after upload.",
    {
        "type": "object",
        "properties": {
            "selector": {"type": "string"},
            "files": {"type": ["string", "array"], "items": {"type": "string"}},
            "timeout": {"type": "integer"},
            "verify_filename": {"type": "boolean", "description": "Assert the uploaded filename appears after upload (default true)."},
        },
        "required": ["selector", "files"]
    }
)
async def cmd_upload_file(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    files = params["files"]
    if isinstance(files, str):
        files = [files]
    resolved = _resolve_fixtures(files)
    timeout = int(params.get("timeout", 10000))
    verify = params.get("verify_filename", True)

    _DETECT_JS = """(sel) => {
        let el;
        try {
            if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                el = document.evaluate(sel.replace('xpath=',''), document, null,
                     XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            } else {
                el = document.querySelector(sel.replace('css=',''));
            }
        } catch(e) { return {found:false}; }
        if (!el) return {found:false};
        if (el.tagName === 'INPUT' && el.type === 'file') return {found:true, isInput:true};
        let inp = el.querySelector('input[type=file]');
        if (!inp && el.closest) inp = el.closest('form, div, section')?.querySelector('input[type=file]');
        if (inp) {
            inp.setAttribute('data-amethyst-upload','1');
            inp.removeAttribute('hidden'); inp.style.display='block'; inp.style.visibility='visible';
            return {found:true, isInput:false, hasNested:true};
        }
        return {found:true, isInput:false, hasNested:false};
    }"""

    async with session.lock:
        det = await session.page.evaluate(_DETECT_JS, sel)

        if det.get("isInput"):
            loc = await _find_locator(session.page, sel)
            await loc.set_input_files(resolved, timeout=timeout)
            method = "direct"

        elif det.get("hasNested"):
            inp_loc = session.page.locator('[data-amethyst-upload="1"]')
            try:
                await inp_loc.set_input_files(resolved, timeout=timeout)
            finally:
                await session.page.evaluate(
                    "() => document.querySelector('[data-amethyst-upload=\\'1\\']')?.removeAttribute('data-amethyst-upload')"
                )
            method = "nested_input"

        else:
            async with session.page.expect_file_chooser(timeout=timeout) as fc_info:
                loc = await _find_locator(session.page, sel)
                await loc.click(timeout=timeout)
            chooser = await fc_info.value
            await chooser.set_files(resolved, timeout=timeout)
            method = "file_chooser"

        verified = True
        if verify:
            verified = await _verify_uploaded_filename(session.page, resolved, timeout=5000)

    if verify and not verified:
        names = [Path(f).name for f in resolved]
        raise AssertionError(
            f"upload_file: files were set via '{method}' but none of {names} "
            f"appeared in any file input or on the page — upload may have been rejected."
        )

    return {"selector": sel, "files": resolved, "method": method, "verified": verified, "uploaded": True}


@register_tool(
    "switch_tab",
    "Switch the active browser tab by zero-based index or by URL substring match.",
    {
        "type": "object",
        "properties": {
            "index": {"type": "integer"},
            "url_contains": {"type": "string"},
        },
        "required": []
    }
)
async def cmd_switch_tab(params: dict, session: Session):
    index = params.get("index")
    url_contains = params.get("url_contains", "")
    async with session.lock:
        pages = session.context.pages
        if not pages:
            raise RuntimeError("No open tabs found in this session")
        if index is not None:
            if index < 0 or index >= len(pages):
                raise IndexError(f"Tab index {index} out of range (0–{len(pages)-1})")
            session.page = pages[index]
        elif url_contains:
            matched = [p for p in pages if url_contains in p.url]
            if not matched:
                raise ValueError(f"No tab with URL containing {url_contains!r}. "
                                 f"Open tabs: {[p.url for p in pages]}")
            session.page = matched[0]
        else:
            raise ValueError("Provide 'index' or 'url_contains' to switch_tab")
        await session.page.bring_to_front()
    return {"active_url": session.page.url, "total_tabs": len(pages)}


# ==================== Command Dispatcher Map ====================

CMD_MAP = {
    "navigate": cmd_navigate,
    "click": cmd_click,
    "fill": cmd_fill,
    "hover": cmd_hover,
    "get_text": cmd_get_text,
    "get_all_text": cmd_get_all_text,
    "screenshot": cmd_screenshot,
    "get_page_content": cmd_get_page_content,
    "get_page_info": cmd_get_page_info,
    "get_interactable_elements": cmd_get_interactable_elements,
    "get_page_content_and_save_csv": cmd_get_page_content_and_save_csv,
    "get_page_content_and_save_txt": cmd_get_page_content_and_save_txt,
    "wait_for_load": cmd_wait_for_load,
    "wait_for_selector": cmd_wait_for_selector,
    "select_option": cmd_select_option,
    "press_key": cmd_press_key,
    "execute_js": cmd_execute_js,
    "close_session": cmd_close_session,
    "get_credentials": cmd_get_credentials,
    "scroll_to_element": cmd_scroll_to_element,
    "double_click": cmd_double_click,
    "clear_input": cmd_clear_input,
    "get_attribute": cmd_get_attribute,
    "assert_text": cmd_assert_text,
    "assert_visible": cmd_assert_visible,
    "assert_not_visible": cmd_assert_not_visible,
    "assert_disabled": cmd_assert_disabled,
    "assert_url": cmd_assert_url,
    "assert_toast": cmd_assert_toast,
    "upload_file": cmd_upload_file,
    "switch_tab": cmd_switch_tab,
    "click_by_index": cmd_click_by_index,
    "click_at_position": cmd_click_at_position,
}

VALID_METHODS = list(CMD_MAP.keys())
