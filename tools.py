"""
All cmd_* command handlers + CMD_MAP.
Depends on: helpers.py, stores.py, credentials.py, tool_registry.py

register_tool/TOOL_REGISTRY live in tool_registry.py, not here — see that
file's module docstring for why (tools.py imports orchestrator.prompts,
which needs to import the registry back to build its TOOLS section; keeping
the registry in tools.py would make that circular).
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
from orchestrator.prompts import _relevance_score  # verify no circular import — prompts.py must not import from tools.py
import uuid


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
from tool_registry import TOOL_REGISTRY, register_tool, verify_registry_matches


# ==================== Upload fixtures helpers ====================

FIXTURES_DIR = Path("data/fixtures")

# Lets a case description say "downloads/invoice.pdf" instead of a full
# absolute path or a pre-staged fixtures file. Resolves against the CURRENT
# QA's own home directory at execution time — since the MCP server runs
# locally per-QA (not a shared/remote server), "downloads/x.pdf" on QA-A's
# machine and QA-B's machine correctly point at each of their own files, no
# manual copy-to-fixtures step needed. This is what makes upload steps like
# "Upload Dokumen → downloads/invoice.pdf" fully automatable — set_input_files
# is called directly with the resolved path, zero dialog, zero manual click.
_HOME_SHORTCUTS = {
    "downloads": "Downloads",
    "download": "Downloads",
    "desktop": "Desktop",
    "documents": "Documents",
    "document": "Documents",
}


def _resolve_home_shortcut(f: str) -> Optional[Path]:
    """"<folder>/<rest>" -> Path.home()/<real folder>/<rest>.
    _HOME_SHORTCUTS is only an ALIAS table (translates common words like
    "download" to the real Windows folder name "Downloads") — it is not a
    whitelist. Any first path segment that's a real, existing directory
    under the home folder is accepted too, so this isn't limited to 5
    hardcoded names (Pictures, Music, OneDrive, "Gambar", whatever the OS
    actually has) as long as the folder genuinely exists."""
    normalized = f.replace("\\", "/")
    head, sep, rest = normalized.partition("/")
    if not sep or not rest:
        return None
    head = head.strip()

    folder_name = _HOME_SHORTCUTS.get(head.lower())
    if folder_name:
        home_folder = Path.home() / folder_name
        if home_folder.is_dir():
            return home_folder / rest

    # Not a known alias — case-insensitively scan the home dir's immediate
    # children for a real folder matching what the user typed (Pictures,
    # OneDrive, "Gambar", whatever actually exists). Explicit case-insensitive
    # compare instead of relying on the OS's own case sensitivity, since that
    # varies (Windows/macOS: insensitive by default, Linux: sensitive).
    try:
        for entry in Path.home().iterdir():
            if entry.is_dir() and entry.name.lower() == head.lower():
                return entry / rest
    except OSError:
        pass
    return None


# Priority order for scanning common OS folders when the case description
# gives a BARE filename with no folder prefix at all (e.g. "invoice.pdf",
# not "downloads/invoice.pdf"). Documents first, per project preference —
# change this order here if that priority should differ.
_BARE_FILENAME_SCAN_ORDER = ["Documents", "Downloads", "Desktop"]


def _scan_common_folders(filename: str) -> Optional[Path]:
    """Bare filename, no explicit folder — check common folders in priority
    order before giving up to fixtures. Top-level only (not recursive), so
    this stays fast and predictable rather than an open-ended filesystem
    crawl. Prints which folder matched so a hit is never a silent surprise."""
    for folder in _BARE_FILENAME_SCAN_ORDER:
        candidate = Path.home() / folder / filename
        if candidate.is_file():
            print(f"[upload] bare filename {filename!r} matched in ~/{folder}/ -> {candidate}")
            return candidate
    return None


def _resolve_fixtures(files: list[str]) -> list[str]:
    """Resolution order for each file path/hint:
    1. Absolute path — passes through as-is.
    2. Home-folder shortcut ("downloads/x.pdf", "desktop/x.pdf", "documents/x.pdf")
       — resolves against THIS machine's home directory.
    3. Bare filename with NO folder prefix ("invoice.pdf") — scans
       Documents -> Downloads -> Desktop (top-level only) before giving up.
       Does NOT apply when an explicit folder prefix was given but didn't
       resolve (e.g. "gambar/x.jpg" where "gambar" doesn't exist) — that
       case goes straight to fixtures rather than guessing a different folder.
    4. Falls back to data/fixtures/<name> (legacy pre-staged fixture files).
    Raises FileNotFoundError with a clear message if nothing matches — so
    portability breaks loudly, not as an opaque Playwright timeout."""
    resolved = []
    for f in files:
        p = Path(f)
        tried = [str(p)] if p.is_absolute() else []
        if not p.is_absolute():
            has_folder_prefix = "/" in f.replace("\\", "/")
            shortcut = _resolve_home_shortcut(f)
            if shortcut:
                tried.append(str(shortcut))

            if shortcut and shortcut.exists():
                p = shortcut
            elif not has_folder_prefix:
                scanned = _scan_common_folders(f)
                if scanned:
                    tried.append(str(scanned))
                    p = scanned
                else:
                    p = FIXTURES_DIR / f
                    tried.append(str(p))
            else:
                p = FIXTURES_DIR / f
                tried.append(str(p))
        if not p.exists():
            raise FileNotFoundError(
                f"upload file not found for hint {f!r} (cwd={Path.cwd()}). "
                f"Tried, in order: {tried}. None of these paths exist on this machine — "
                f"either the file isn't actually there yet, or (if you just edited tools.py) "
                f"the MCP server process is still running the OLD code and needs a restart."
            )
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

async def _aria_combobox_pick(page, sel: str, value: str) -> dict:
    """Returns {"success", "trigger_selector", "option_xpath", "matched_text"}.
    option_xpath/matched_text are only populated when success is True — codegen
    uses option_xpath to replay the exact option click without re-deriving it."""
    marker = f"pending-{uuid.uuid4().hex[:8]}"

    combo = await page.evaluate("""
        (args) => {
            const [sel, marker] = args;
            function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
            }
            let el = null;
            if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.replace('xpath=', '');
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
            if (!el) return null;
            const role = el.getAttribute('role');
            const hasPopup = el.getAttribute('aria-haspopup');
            if (role !== 'combobox' && hasPopup !== 'listbox') return null;

            el.setAttribute('data-c2s-target', marker);

            return {
                isOpen: el.getAttribute('data-state') === 'open' || el.getAttribute('aria-expanded') === 'true',
                listboxId: el.getAttribute('aria-controls') || null,
            };
        }
    """, [sel, marker])
    if combo is None:
        return {"success": False, "trigger_selector": sel, "option_xpath": None, "matched_text": None}

    # Scope to this trigger's own listbox when we know its id. Falls back
    # to a global query only if aria-controls isn't present — that fallback
    # still carries the stale-hidden-listbox risk this bug just exposed.
    listbox_id = combo.get("listboxId")
    if listbox_id:
        option_selector = f'[id="{listbox_id}"] [role="option"]'
    else:
        option_selector = '[role="listbox"] [role="option"]'

    clicked = False
    matched_text = None
    option_xpath = None
    try:
        if not combo["isOpen"]:
            opened = await _force_action(page, sel, "click")
            if not opened:
                return {"success": False, "trigger_selector": sel, "option_xpath": None, "matched_text": None}
            await page.wait_for_timeout(200)

        await page.wait_for_selector(option_selector, timeout=3000, state="visible")
        options = page.locator(option_selector)
        count = await options.count()
        norm_value = value.strip().lower()

        target = None
        for i in range(count):
            text = (await options.nth(i).inner_text()).strip()
            if text.lower() == norm_value:
                target = options.nth(i)
                matched_text = text
                break
        if target is None:
            for i in range(count):
                text = (await options.nth(i).inner_text()).strip()
                if norm_value in text.lower():
                    target = options.nth(i)
                    matched_text = text
                    break

        if target is None:
            return {"success": False, "trigger_selector": sel, "option_xpath": None, "matched_text": None}

        # Build a re-locatable XPath for this exact option now, while we still
        # know which one matched — codegen replays this as a second click.
        # A `"` in matched_text would break the double-quoted XPath string
        # literal below; no XPath-escaping helper exists in this codebase, so
        # skip building it rather than emit a broken selector (caller/codegen
        # falls back to a manual-fix comment when option_xpath is None).
        if '"' in matched_text:
            option_xpath = None
        elif listbox_id:
            option_xpath = (
                f'//*[@id="{listbox_id}"]//*[@role="option"]'
                f'[normalize-space(.) = "{matched_text}"]'
            )
        else:
            option_xpath = f'//*[@role="option"][normalize-space(.) = "{matched_text}"]'

        await target.click(timeout=3000)
        clicked = True

        confirmed = False
        last_seen = None
        deadline = asyncio.get_event_loop().time() + 5
        while asyncio.get_event_loop().time() < deadline:
            try:
                last_seen = await page.evaluate(
                    """(marker) => {
                        const el = document.querySelector(`[data-c2s-target="${marker}"]`);
                        return el ? el.innerText.trim() : null;
                    }""",
                    marker,
                )
            except PlaywrightError as nav_err:
                if "Execution context was destroyed" in str(nav_err) or "navigation" in str(nav_err).lower():
                    try:
                        await page.wait_for_load_state("load", timeout=8000)
                    except Exception:
                        pass
                    await page.wait_for_timeout(300)
                    continue
                raise

            if last_seen and norm_value in last_seen.lower():
                confirmed = True
                break
            await page.wait_for_timeout(150)

        if not confirmed:
            print(f"[ARIA combobox] selected '{value}' but trigger never confirmed it — last seen: {last_seen!r}")

    except PlaywrightTimeoutError:
        clicked = False
    finally:
        try:
            await page.evaluate(
                """(marker) => {
                    const el = document.querySelector(`[data-c2s-target="${marker}"]`);
                    if (el) el.removeAttribute('data-c2s-target');
                }""",
                marker,
            )
        except Exception:
            pass

    if not clicked:
        try:
            await page.keyboard.press("Escape")
        except Exception:
            pass
    return {
        "success": clicked,
        "trigger_selector": sel,
        "option_xpath": option_xpath if clicked else None,
        "matched_text": matched_text if clicked else None,
    }

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
    },
    category="action",
    llm_doc='selector (XPath), value (option label text)',
)
async def cmd_select_option(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    value = params.get("value", "") or params.get("text", "")
    aria_result = None
    async with session.lock:
        handled = await _select2_pick(session.page, sel, value)
        if not handled:
            aria_result = await _aria_combobox_pick(session.page, sel, value)
            handled = aria_result["success"]
        if not handled:
            # Resolve directly to an ElementHandle (instead of a boolean +
            # re-resolving `sel` again via page.select_option) so the exact
            # node we validate as a real <select> is the exact node we act
            # on. Also scope to the topmost open modal dialog, if any:
            # without this, a <select> matching `sel` in the background
            # (e.g. a page-level filter dropdown) can be silently picked
            # instead of the real in-modal control, reporting SUCCESS while
            # the visible field never changes.
            select_handle = await session.page.evaluate_handle("""
                (sel) => {
                    try {
                        function isVisible(node) {
                            const s = window.getComputedStyle(node);
                            return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
                        }
                        let modalRoot = null;
                        for (const d of document.querySelectorAll('[role="dialog"][aria-modal="true"]')) {
                            if (isVisible(d)) { modalRoot = d; break; }
                        }
                        function consider(node) {
                            if (!isVisible(node)) return false;
                            if (modalRoot && !modalRoot.contains(node)) return false;
                            return true;
                        }
                        let el = null;
                        if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                            const xsel = sel.replace('xpath=','');
                            const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            for (let i = 0; i < r.snapshotLength; i++) {
                                const node = r.snapshotItem(i);
                                if (consider(node)) { el = node; break; }
                            }
                        } else {
                            const nodes = document.querySelectorAll(sel);
                            for (const node of nodes) {
                                if (consider(node)) { el = node; break; }
                            }
                        }
                        return (el && el.tagName === 'SELECT') ? el : null;
                    } catch(e) { return null; }
                }
            """, sel)
            select_el = select_handle.as_element()
            if select_el:
                try:
                    await select_el.select_option(label=value)
                except Exception:
                    await select_el.select_option(value=value)
                await select_handle.dispose()
            else:
                await select_handle.dispose()
                raise Exception(f"select_option failed: could not find Select2, ARIA combobox, or native <select> for value='{value}' (checked inside the active modal dialog when one is open)")
        await asyncio.sleep(0.5)

    result = {"selector": sel, "value": value}
    if aria_result and aria_result["success"]:
        result["resolved_via"] = "aria_combobox"
        result["trigger_selector"] = aria_result["trigger_selector"]
        if aria_result.get("option_xpath"):
            result["option_selector"] = aria_result["option_xpath"]
    return result


@register_tool(
    "navigate",
    "Navigate the browser to a given URL. Waits for DOMContentLoaded, load, and networkidle.",
    {
        "type": "object",
        "properties": {
            "url": {"type": "string"}
        },
        "required": ["url"]
    },
    category="action",
    llm_doc="url",
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
    },
    category="action",
    # Only `selector` is documented to the LLM — the rest (capture_toast,
    # toast_selector, etc.) are engine-internal knobs set by engine.py's
    # toast-capture logic, not something the LLM is ever asked to fill in.
    llm_doc="selector (XPath)",
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
            # Playwright's own auto-scroll (inside .click()) only moves the
            # minimum distance needed — element often ends up flush against
            # the viewport edge, sometimes under a sticky header. Force a
            # centered scroll first so it lands with breathing room.
            await loc.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'})")
        except Exception:
            pass
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

        # Same popup-tracking as cmd_click_by_index (see there for full
        # rationale): if what we just clicked has aria-controls, remember it
        # as the currently-open popup so a following click_by_index step
        # ("pick option X from the list") can be scored against it. This
        # needed to live here TOO, not just in click_by_index — the LLM
        # doesn't consistently route trigger-opens through click_by_index; a
        # trigger with a stable id gets a plain `click` instead (reasonably,
        # per DECISION GUIDE's own id-selector preference), and that path was
        # silently not updating last_combobox_controls at all. Found via a
        # live shadcn "Banana" run where step 2 used `click` (id-based
        # selector) instead of click_by_index — 2026-07-09.
        try:
            _controls = await loc.get_attribute("aria-controls")
            if _controls:
                session.last_combobox_controls = _controls
        except Exception:
            pass

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
    },
    # Not in the LLM's TOOLS menu — a low-level coordinate-click helper the
    # LLM never picks directly (it uses click / click_by_index instead).
    visible_to_llm=False,
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
    },
    category="action",
    llm_doc="selector (XPath), text",
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

        # Native Playwright fill first — matches cmd_click/cmd_double_click.
        # Native .fill() carries Playwright's actionability checks (visible/
        # stable/enabled) AND a real focus->input->change->blur sequence that
        # JS-framework form validation (Angular/React) actually listens for.
        # _force_action's raw DOM-value-set + dispatchEvent can leave a form
        # LOOKING filled while the framework's own validity state never
        # updates — e.g. a submit button gated on form.invalid staying
        # disabled forever with no visible error. See 2026-07-23 register
        # button investigation.
        loc = await _find_locator(session.page, sel)
        try:
            # See cmd_click: force a centered scroll before acting so the
            # field doesn't land flush against the viewport edge.
            await loc.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'})")
        except Exception:
            pass
        try:
            await loc.wait_for(state="visible", timeout=8000)
            await loc.fill(text, timeout=8000)
            success = True
        except (PlaywrightTimeoutError, PlaywrightError):
            # Native actionability check failed — fall back to JS force-fill.
            # Known limitation: _force_action's isVisible() does not check disabled
            # state or pointer-events, so a disabled-but-rendered element can
            # false-pass here. That is a pre-existing issue, out of scope for this change.
            result = await _force_action(session.page, sel, "fill", text)
            success = bool(result)
            resolved = result.get("resolved") if isinstance(result, dict) else None
            if not success:
                raise ValueError(
                    f"Element not found or not interactable: {sel!r}. "
                    "Use get_interactable_elements to verify the selector."
                )

        await asyncio.sleep(0.5)
    return {"selector": sel, "text": text, "resolved_selector": resolved}


@register_tool(
    "hover",
    "Hover the mouse over an element to trigger hover states, tooltips, or dropdown menus.",
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]},
    category="action",
    llm_doc="selector (XPath)",
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
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]},
    category="extract",
    llm_doc="selector (XPath)",
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
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]},
    category="extract",
    llm_doc="selector (XPath)",
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
    },
    category="verify",
    # path/full_page/return_base64 are internal defaults, not LLM-set params —
    # llm_doc="" (not None) explicitly suppresses auto-derivation from the
    # schema's properties, which would otherwise list them as if the LLM
    # should fill them in.
    llm_doc="",
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
    {"type": "object", "properties": {}, "required": []},
    category="verify",
)
async def cmd_get_page_content(params: dict, session: Session):
    async with session.lock:
        content = await session.page.content()
    return {"content": content}


@register_tool(
    "get_page_info",
    "Return the current page title and URL.",
    {"type": "object", "properties": {}, "required": []},
    category="verify",
)
async def cmd_get_page_info(params: dict, session: Session):
    async with session.lock:
        return {"title": await session.page.title(), "url": session.page.url}


@register_tool(
    "no_match",
    "No element on the page matches this step's description. The LLM "
    "declined to guess an element rather than risk clicking the wrong one. "
    "This always resolves as a tracked failure, not a silent skip.",
    {"type": "object", "properties": {}, "required": []},
    # Not listed in the TOOLS table — the LLM is told to emit this via the
    # DECISION GUIDE prose ("Return exactly: {"method": "no_match", ...}"),
    # not by picking it off a menu, so it stays out of render_tools_table().
    visible_to_llm=False,
)
async def cmd_no_match(params: dict, session: Session):
    return {"error": "No element found matching this step's description — LLM declined to guess."}


@register_tool(
    "close_session",
    "Close and destroy the browser session, releasing all browser resources.",
    {
        "type": "object",
        "properties": {"sessionId": {"type": "string"}},
        "required": ["sessionId"]
    },
    category="wait_session",
    # schema's own "sessionId" property is the same sessionId every tool
    # already gets prefixed with — llm_doc="" avoids rendering it twice.
    llm_doc="",
)
async def cmd_close_session(params: dict, session: Session, request: Request):
    session_id = params["sessionId"]
    await request.app.state.sessions.close(session_id)
    return {"status": "closed"}


# Batched, single-round-trip element scraper. The previous implementation did
# ~18-22 separate `await el.get_attribute(...)`/`el.evaluate(...)` Playwright
# round trips PER element (visibility, aria-hidden, tabindex, tag, text, id,
# name, href, aria-label, placeholder, data-act, role, title, direct-text,
# combobox-label, child-count, input type/value, label lookup, row context,
# aria-controls, disabled). On an element-dense page (e.g. a docs site with a
# 100+ link sidebar) that's 1800-2000+ round trips just to scrape one snapshot
# — the actual cause of multi-second "why is this so slow after navigate"
# delays. This does the exact same extraction logic in ONE page.evaluate() per
# frame instead: one browser-side pass over the DOM, one round trip back.
# Every field name/priority-order below is a direct port of the old Python
# logic — same suggested_selector fallback chain, same row_context lookup,
# same combobox-label-vs-value-text handling. Behavior should be identical,
# just without the network fan-out.
_INTERACTABLE_ELEMENTS_JS = """
() => {
    function isVisible(el) {
        // Mirrors Playwright's own actionability "visible" definition exactly:
        // non-empty bounding box (width AND height both > 0) and no
        // visibility:hidden. Deliberately does NOT check opacity — Playwright's
        // real is_visible() doesn't either; an opacity:0 element (common for
        // fade-in animations, hover-reveal buttons) is still "visible" and
        // clickable per Playwright's own model. An earlier version of this
        // function added an opacity check and used AND instead of OR for the
        // width/height test — both were unintentional deviations from the
        // Playwright semantics the old per-element el.is_visible() scraper
        // actually had, found during a regression audit against TC_003 (a
        // previously-passing 9/9 test case) on 2026-07-09. Match Playwright's
        // behavior exactly here, don't invent stricter/looser rules.
        if (!el.isConnected) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return false;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;
        return true;
    }

    function findLabel(node) {
        if (node.id) {
            const lbl = document.querySelector('label[for="' + node.id + '"]');
            if (lbl) return lbl.textContent.trim();
        }
        let p = node.parentElement;
        while (p && p !== document.body) {
            const lbl = p.querySelector('label');
            if (lbl) return lbl.textContent.trim();
            p = p.parentElement;
        }
        return '';
    }

    const nodes = Array.from(document.querySelectorAll(
        "button, a, input, textarea, select, " +
        "[role='button'], [role='link'], [role='combobox'], [role='listbox'], " +
        "[role='option'], [role='checkbox'], " +
        "span[role='combobox'], span[role='button'], span[tabindex], " +
        "[data-act], [data-link]"
    ));

    const result = [];

    for (const e of nodes) {
        try {
            if (!isVisible(e)) continue;

            const ariaHidden = e.getAttribute('aria-hidden');
            const tabindex = e.getAttribute('tabindex');
            if (ariaHidden === 'true' && tabindex === '-1') continue;

            const tagName = e.tagName;
            const textContent = (e.textContent || '').trim();
            const getId = e.getAttribute('id');
            const getName = e.getAttribute('name');
            const getHref = e.getAttribute('href');
            const ariaLabel = e.getAttribute('aria-label');
            const placeholder = e.getAttribute('placeholder');
            const dataAct = e.getAttribute('data-act');
            const roleAttr = e.getAttribute('role');
            const titleAttr = e.getAttribute('title');

            // Icon-only elements (no text/aria-label/id/name) are dropped unless
            // they at least carry a title tooltip — see click_by_index icon fix.
            const isFormish = tagName === 'INPUT' || tagName === 'TEXTAREA' || tagName === 'SELECT';
            if (!isFormish && !(getId || getName || textContent || getHref || ariaLabel || placeholder || titleAttr)) {
                continue;
            }

            const directText = Array.from(e.childNodes)
                .filter(n => n.nodeType === 3)
                .map(n => n.textContent.trim())
                .filter(Boolean).join(' ');

            // combobox/listbox triggers show their CURRENTLY SELECTED VALUE as
            // their text (e.g. "Banana") — not a stable identifier, since it
            // changes with every selection. Prefer the adjacent <label> instead.
            let comboboxLabelText = '';
            if ((roleAttr === 'combobox' || roleAttr === 'listbox') && !(getId || getName || ariaLabel)) {
                comboboxLabelText = findLabel(e);
            }

            const tagLower = tagName.toLowerCase();
            let suggested = '';
            if (getId) {
                suggested = 'xpath=//' + tagLower + '[@id="' + getId + '"]';
            } else if (getName) {
                suggested = 'xpath=//' + tagLower + '[@name="' + getName + '"]';
            } else if (ariaLabel) {
                suggested = 'xpath=//' + tagLower + '[@aria-label="' + ariaLabel + '"]';
            } else if (titleAttr) {
                suggested = 'xpath=//' + tagLower + '[@title="' + titleAttr + '"]';
            } else if (placeholder) {
                suggested = 'xpath=//' + tagLower + '[@placeholder="' + placeholder + '"]';
            } else if (comboboxLabelText) {
                suggested = 'xpath=//label[normalize-space(.)="' + comboboxLabelText + '"]/following::*[@role="' + roleAttr + '"][1]';
            } else if (directText || textContent) {
                const sourceText = directText || textContent;
                const childTextCount = tagName === 'SELECT'
                    ? e.options.length
                    : Array.from(e.children).filter(c => (c.textContent || '').trim()).length;
                if (childTextCount > 1) {
                    suggested = '';
                } else {
                    const firstLine = sourceText.split('\\n')[0].trim();
                    suggested = firstLine ? 'xpath=//' + tagLower + '[.//text()[normalize-space(.) = "' + firstLine + '"]]' : '';
                }
            } else if (dataAct && !['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'].includes(tagName)) {
                const firstLine = (textContent.split('\\n')[0] || '').trim();
                suggested = 'xpath=//' + tagLower + '[@data-act="' + dataAct + '" and .//*[normalize-space(.) = "' + firstLine + '"]]';
            } else if (textContent) {
                const firstLine = textContent.split('\\n')[0].trim();
                suggested = firstLine ? 'xpath=//' + tagLower + '[.//text()[normalize-space(.) = "' + firstLine + '"]]' : '';
            }

            const inputType = tagName === 'INPUT' ? e.getAttribute('type') : null;
            const inputValue = isFormish ? (e.value ?? null) : null;

            let labelText = comboboxLabelText;
            if (!suggested && isFormish) {
                labelText = findLabel(e);
                if (labelText) {
                    suggested = '//label[normalize-space(.)="' + labelText + '"]/following::input[1]';
                }
            }

            // Row-level disambiguation for repeated icons (one View/Edit/Delete
            // per table/list row) — see click_by_index icon fix, 2026-07-08.
            const rowEl = e.closest('tr, [role="row"], li');
            const rowContext = rowEl ? rowEl.textContent.replace(/\\s+/g, ' ').trim().slice(0, 200) : '';

            // Widget-instance disambiguation: which popup/listbox does this
            // OPTION belong to? A page with several independent Select/combobox
            // widgets can have the same option text (or a value already shown
            // by a different, closed widget) appear more than once — matching
            // on text alone isn't enough to know which widget's option this is.
            // See [[project_click_by_index_icon_resolution]] "Banana" case,
            // 2026-07-09. Only computed for role=option since it's the only
            // case that needs it.
            let owningPopupId = '';
            if (roleAttr === 'option') {
                const popup = e.closest('[role="listbox"], [role="menu"], [id]');
                owningPopupId = popup ? (popup.id || '') : '';
            }

            // Grid/list-position disambiguation: a step like "click the first
            // product that appears" / "klik produk pertama" has NO keyword to
            // match against — the element's identity IS its position in a
            // repeated card/row pattern, not its text. _relevance_score has no
            // way to confirm that kind of instruction on its own, so give it a
            // structural signal here: walk up a few ancestors looking for a
            // parent with >=3 same-tag children (the actual grid/list
            // container), and record this element's 0-based index + the
            // group size among those siblings. >=3 is deliberate — two same-tag
            // siblings elsewhere on the page (e.g. two nav buttons) shouldn't
            // count as a "list", real product/result grids always have more.
            // See [[project_click_by_index_icon_resolution]] for the sibling
            // precedent (row_context/owning_popup_id above).
            let siblingGroupIndex = -1;
            let siblingGroupSize = 0;
            {
                let node = e;
                for (let depth = 0; depth < 4 && node.parentElement; depth++) {
                    const parent = node.parentElement;
                    const sameTagSiblings = Array.from(parent.children).filter(c => c.tagName === node.tagName);
                    if (sameTagSiblings.length >= 3) {
                        siblingGroupIndex = sameTagSiblings.indexOf(node);
                        siblingGroupSize = sameTagSiblings.length;
                        break;
                    }
                    node = parent;
                }
            }

            result.push({
                id: getId, tag: tagName, type: inputType, value: inputValue,
                text: textContent, disabled: !!e.disabled,
                name: getName, href: getHref,
                role: roleAttr,
                aria_controls: e.getAttribute('aria-controls'),
                tabindex: tabindex, aria_hidden: ariaHidden,
                aria_label: ariaLabel, placeholder: placeholder,
                title: titleAttr,
                data_act: dataAct, visible: true,
                label: labelText,
                row_context: rowContext,
                owning_popup_id: owningPopupId,
                sibling_group_index: siblingGroupIndex,
                sibling_group_size: siblingGroupSize,
                suggested_selector: suggested,
            });
        } catch (err) {
            continue;
        }
    }
    return result;
}
"""


@register_tool(
    "get_interactable_elements",
    "Return all visible interactable elements on the current page across all frames.",
    {"type": "object", "properties": {}, "required": []},
    # Not in the TOOLS menu — the engine calls this itself to build the
    # AVAILABLE ELEMENTS block of every prompt; the LLM never requests it by
    # name, it just consumes the resulting element list.
    visible_to_llm=False,
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
                frame_elements = await frame.evaluate(_INTERACTABLE_ELEMENTS_JS)
            except Exception:
                continue
            is_main = frame == session.page.main_frame
            for el in frame_elements:
                el["in_iframe"] = not is_main
                result.append(el)
    return {"count": len(result), "elements": result}



@register_tool(
    "click_by_index",
    "Click an element identified by its index in the AVAILABLE ELEMENTS list "
    "(from get_interactable_elements), with drift + relevance checks to "
    "refuse the click rather than hit the wrong element if the DOM shifted "
    "between prompt build and execution.",
    {
        "type": "object",
        "properties": {
            "index": {"type": "integer"},
            "expected_text": {"type": "string"},
            # Internal — threaded through from the calling step's own
            # description by engine.py, not something the LLM sets directly.
            "step_description": {"type": "string"},
        },
        "required": ["index", "expected_text"]
    },
    category="action",
    llm_doc="index (int, from elements list), expected_text (string, exact "
             "text shown at [index] in AVAILABLE ELEMENTS — required for "
             "drift detection)",
)
async def cmd_click_by_index(params: dict, session: Session):
    index = params.get("index")
    expected_text = (params.get("expected_text") or "").strip()
    step_description = (params.get("step_description") or "").strip()  # needs to be threaded through from the caller
    if index is None:
        return {"error": "Missing required param: index"}
    elements_result = await cmd_get_interactable_elements(params, session)
    elements = elements_result.get("elements", [])
    if index < 0 or index >= len(elements):
        return {"error": f"Index {index} out of range", "total_elements": len(elements)}
    target = elements[index]
    actual_text = (target.get("text") or "").strip()

    # Drift check must accept whatever field the LLM was told to copy from —
    # not just "text". Icon-only buttons (no text, identified by title or
    # aria-label instead) legitimately have expected_text pulled from those
    # fields. Comparing only against "text" made every title/aria-label-only
    # element fail drift detection forever, regardless of site. Compare
    # against any of the identifying fields; if ANY matches, it's the same
    # element and there's no real drift.
    actual_aria_label = (target.get("aria_label") or "").strip()
    actual_title = (target.get("title") or "").strip()

    # Substring match, not exact-equality: the LLM is instructed to copy ONLY
    # the identity value, but in practice sometimes wraps it in extra text
    # (e.g. "BUTTON title=\"View\" row=\"...\"" instead of plain "View"). If the
    # real identity value still appears inside whatever the model produced,
    # that's the same element — reject only when NONE of the identifying
    # fields show up at all, which is the actual signature of real DOM drift
    # (a different element with an unrelated identity at this index).
    def _contains_match(expected: str, *actual_values: str) -> bool:
        exp = expected.strip().lower()
        for val in actual_values:
            val = (val or "").strip().lower()
            if val and (val in exp or exp in val):
                return True
        return False

    if expected_text and not _contains_match(expected_text, actual_text, actual_aria_label, actual_title):
        return {
            "error": f"click_by_index drift: expected_text={expected_text!r}, "
                     f"actual text/aria-label/title={(actual_text, actual_aria_label, actual_title)!r} "
                     f"at index={index} — DOM order shifted between prompt build and "
                     f"execution, refusing to click"
        }

    # NEW: index was structurally valid, now check it's actually relevant to the step
    score = None
    if step_description:
        score = _relevance_score(step_description, target, session.last_combobox_controls)

        # --- TEMP: log every score during the tuning window ---
        print(f"[click_by_index relevance] step={step_description!r} idx={index} text={actual_text!r} score={score}")
        # -------------------------------------------------------

        if score <= 0:
            return {
                "error": f"click_by_index refused: element at index={index} "
                         f"(text={actual_text!r}) scored {score} relevance against "
                         f"step {step_description!r} — likely wrong target, not clicking blind"
            }
            
    selector = target.get("suggested_selector", "")
    if not selector:
        return {"error": f"Element at index {index} has no usable selector", "element": target}
    async with session.lock:
        await session.page.click(selector)

    # Remember which popup this click just opened (if any), so the NEXT
    # click_by_index call — the one that actually picks an option — can be
    # scored against "does this option belong to the popup we just opened."
    # Without this, opening trigger #1 then picking "Banana" has no way to
    # tell that trigger #1's popup is the relevant one when the page has
    # other Select/combobox widgets whose text coincidentally also says
    # "Banana". Cleared implicitly by being overwritten on the next trigger
    # click; intentionally NOT cleared on option-pick, since a step sequence
    # sometimes re-opens the same trigger (e.g. to change the selection again).
    #
    # Gating on role="combobox"/"listbox" turned out too narrow: shadcn's
    # newer Base UI Select trigger doesn't set an explicit role (relies on
    # native <button> + aria-haspopup semantics instead of Radix's
    # role="combobox"), so that check silently never fired and the whole
    # popup-scoping bonus/penalty stayed dead (score stuck at the pre-fix
    # baseline). aria-controls itself is the reliable, library-agnostic
    # signal — by definition it means "this element controls that other DOM
    # subtree," true whether the widget sets role=combobox, aria-haspopup, or
    # neither. A false positive here (e.g. a tab/accordion header, which also
    # uses aria-controls) can only ever hurt an UNRELATED role="option"
    # candidate elsewhere via the -10 penalty — which pushes it to a refusal
    # (score <= 0), not a wrong click. Fail-refuse is the acceptable failure
    # mode here, not silent mis-click.
    if target.get("aria_controls"):
        session.last_combobox_controls = target.get("aria_controls")

    # element_title/element_aria_label/element_row_context are surfaced so the
    # caller (engine.py) can persist them into the recorded script step. Without
    # this, the saved JSON only has {index, expected_text} — enough to replay
    # live (re-scores against a fresh snapshot) but not enough for the static
    # Playwright .py generator to build a real selector, since "index" has no
    # meaning outside a live session. See stores.py click_by_index normalization.
    return {"status": "clicked", "index": index, "selector": selector,
            "element_text": actual_text, "element_tag": target.get("tag", ""),
            "element_aria_label": actual_aria_label, "element_title": actual_title,
            "element_row_context": (target.get("row_context") or "").strip(),
            "relevance_score": score if step_description else None}


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
    {"type": "object", "properties": {}, "required": []},
    category="extract",
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
    {"type": "object", "properties": {}, "required": []},
    category="extract",
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
    },
    category="wait_session",
    llm_doc='state ("load" | "networkidle" | "domcontentloaded"), timeout (ms)',
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
    },
    category="wait_session",
    llm_doc='selector (XPath), state ("visible" | "hidden"), timeout (ms)',
)
async def cmd_wait_for_selector(params: dict, session: Session):
    selector = normalize_selector(params["selector"])
    state = params.get("state", "visible")
    timeout = params.get("timeout", 10000)
    async with session.lock:
        loc = await _find_locator(session.page, selector)
        await loc.wait_for(state=state, timeout=timeout)
    return {"selector": selector, "state": state, "timeout": timeout}


@register_tool(
    "execute_js",
    "Run an arbitrary JS expression via page.evaluate() and return the result. "
    "Internal escape hatch only — excluded from the LLM's TOOLS menu on "
    "purpose per the no-JS-evaluate locator policy (see feedback: "
    "locator strategy standard): step generation must resolve elements via "
    "semantic locators / XPath, never by asking the LLM to author raw JS.",
    {"type": "object", "properties": {"script": {"type": "string"}}, "required": ["script"]},
    visible_to_llm=False,
)
async def cmd_execute_js(params: dict, session: Session):
    script = params.get("script", "")
    async with session.lock:
        result = await session.page.evaluate(script)
    return {"result": str(result)}


@register_tool(
    "press_key",
    "Press a keyboard key on the page.",
    {"type": "object", "properties": {"key": {"type": "string"}}, "required": []},
    category="action",
    llm_doc='key ("Escape" | "Enter" | "Tab" | "ArrowDown" | "ArrowUp" | "Backspace")',
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
    },
    category="wait_session",
    llm_doc="name (credential name string)",
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
    },
    category="action",
    llm_doc="selector (XPath)",
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
    },
    category="action",
    llm_doc="selector (XPath)",
)
async def cmd_double_click(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        try:
            # See cmd_click: force a centered scroll before acting so the
            # element doesn't land flush against the viewport edge.
            await loc.evaluate("el => el.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'})")
        except Exception:
            pass
        try:
            await loc.dblclick(timeout=8000)
        except (PlaywrightTimeoutError, PlaywrightError):
            # Native actionability check failed — fall back to JS force-dblclick.
            # Known limitation: _force_action's isVisible() does not check disabled
            # state or pointer-events, so a disabled-but-rendered element can
            # false-pass here. That is a pre-existing issue, out of scope for this change.
            result = await _force_action(session.page, sel, "double_click")
            if not result:
                raise ValueError(
                    f"Element not found or not double-clickable: {sel!r}. "
                    "Use get_interactable_elements to verify the selector."
                )
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
    },
    category="action",
    llm_doc="selector (XPath)",
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
    },
    category="extract",
    llm_doc='selector (XPath), attribute (e.g. "href")',
)
async def cmd_get_attribute(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    attr = params["attribute"]
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        value = await loc.get_attribute(attr, timeout=params.get("timeout", 10000))
    return {"selector": sel, "attribute": attr, "value": value}


# Non-interactive text (a stat/counter like "3 events", a status label, etc.)
# never appears in AVAILABLE ELEMENTS — that scraper only tracks buttons/
# links/inputs/etc. So the LLM has no way to see whether such text actually
# exists before guessing an assert_text selector, and ends up cycling through
# increasingly broad guesses (a specific div → //body) across retries. //body
# is also actively misleading: Playwright's text_content() on it includes raw
# <script> tag source (Next.js hydration payloads etc.), so a "match" there
# can be pure coincidence and a "no match" can hide text that's really on the
# page just structured differently than guessed. This does one authoritative
# search across all VISIBLE text (script/style excluded) for the smallest
# element containing `expected`, so assert_text doesn't depend on the LLM's
# selector guess being exactly right.
_FIND_TEXT_ANYWHERE_JS = """
(expected) => {
    function isVisible(el) {
        if (!el.isConnected) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return false;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;
        return true;
    }
    const skipTags = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT']);
    const all = document.querySelectorAll('body *');
    let best = null;
    let bestLen = Infinity;
    for (const el of all) {
        if (skipTags.has(el.tagName)) continue;
        if (!isVisible(el)) continue;
        const text = (el.textContent || '').trim();
        if (text.includes(expected) && text.length < bestLen) {
            best = el;
            bestLen = text.length;
        }
    }
    if (!best) return { found: false };
    return {
        found: true,
        text: best.textContent.trim().slice(0, 300),
        tag: best.tagName,
        id: best.id || null,
    };
}
"""


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
    },
    category="verify",
    llm_doc="selector (XPath), expected (text substring) — for div/span/p/td/li; "
            "also works on input/textarea (reads value if no inner text)",
)
async def cmd_assert_text(params: dict, session: Session):
    sel = normalize_selector(params["selector"])
    expected = params["expected"]
    exact = params.get("exact", False)
    timeout = params.get("timeout", 10000)
    async with session.lock:
        loc = await _find_locator(session.page, sel)
        # Fast existence check — fail early instead of burning the full timeout on a wrong selector
        selector_attached = True
        try:
            await loc.wait_for(state="attached", timeout=min(timeout, 5000))
        except Exception:
            selector_attached = False

        actual = ""
        select_label = ""
        if selector_attached:
            # input_value() is the correct Playwright API for <input>/<select>/<textarea>,
            # but on a native <select> it returns the selected OPTION'S VALUE
            # ATTRIBUTE (e.g. "2"), not its visible label ("Option 2") — and since
            # it doesn't throw for a <select>, the text_content() fallback below
            # never fired for this case. Test descriptions almost always mean the
            # visible label. Found 2026-07-09 via a real .py-replay failure
            # (TC001): expected 'Option 2', got '2'. Capture the selected
            # option's own text as a second candidate; match against EITHER the
            # raw value/text OR the label, so a step that intentionally checks
            # a raw value (e.g. "2") still works too. Same fix mirrored in the
            # static .py generator (stores.py _assert_text_py).
            try:
                tag_name = (await loc.evaluate("el => el.tagName") or "").upper()
            except Exception:
                tag_name = ""
            if tag_name == "SELECT":
                try:
                    select_label = (await loc.evaluate(
                        "el => el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : ''"
                    ) or "").strip()
                except Exception:
                    pass
            try:
                actual = (await loc.input_value(timeout=3000) or "").strip()
            except Exception:
                pass
            if not actual:
                try:
                    actual = (await loc.text_content(timeout=3000) or "").strip()
                except Exception:
                    pass
            if not actual:
                actual = (await loc.evaluate("el => el.value || el.textContent || ''") or "").strip()

        if exact:
            match = (actual == expected) or (select_label == expected)
        else:
            match = (expected in actual) or bool(select_label and expected in select_label)
        if match and select_label and expected in select_label and expected not in actual:
            actual = select_label  # report whichever field actually matched

        # Selector either didn't resolve at all, or resolved but didn't contain
        # the expected text (includes the //body-full-of-script-garbage case,
        # since that "actual" text technically failed the `expected in actual`
        # check on its own if the real rendered text isn't part of it). Do one
        # real search of the visible page before giving up, bounded to a few
        # retries within the remaining timeout budget — covers async-rendered
        # counters/stats that just haven't painted yet on the first check.
        fallback_hit = None
        if not match and not exact:
            deadline = time.monotonic() + (timeout / 1000.0)
            while time.monotonic() < deadline:
                try:
                    result = await session.page.evaluate(_FIND_TEXT_ANYWHERE_JS, expected)
                except Exception:
                    result = None
                if result and result.get("found"):
                    fallback_hit = result
                    match = True
                    actual = result.get("text", actual)
                    break
                await asyncio.sleep(0.4)

    if not match:
        raise AssertionError(
            f"assert_text failed — selector: {sel!r}\n"
            f"  expected: {expected!r}\n"
            f"  actual:   {actual!r}\n"
            f"  (also searched all visible page text, not found anywhere)"
        )
    result = {"selector": sel, "expected": expected, "actual": actual, "passed": True}
    if fallback_hit:
        result["matched_via"] = "full_page_text_search"
        result["matched_tag"] = fallback_hit.get("tag")
    return result


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
    },
    category="verify",
    llm_doc="selector (XPath)",
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
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]},
    category="verify",
    llm_doc="selector (XPath)",
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
    {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]},
    category="verify",
    llm_doc="selector (XPath)",
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
    },
    category="verify",
    llm_doc="expected (URL substring)",
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
    },
    category="verify",
    llm_doc="expected_text (substring), timeout (ms, default 6000) — waits for a "
             "toast/popup/snackbar/SweetAlert to appear and validates its text",
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
    },
    category="action",
    llm_doc='selector (XPath targeting <input type="file">), files (path string — '
            "absolute path, OR a home-folder shortcut like "
            '"downloads/invoice.pdf" / "desktop/x.png" / "documents/y.docx" '
            "resolved against the current machine's home directory, exactly as "
            "written in the step description — do not invent an absolute path "
            "yourself)",
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
    },
    category="action",
    llm_doc="index (int, 0-based) OR url_contains (string)",
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
    "no_match": cmd_no_match,
}

VALID_METHODS = list(CMD_MAP.keys())

# Fail loudly at import time if TOOL_REGISTRY (source of the LLM-facing TOOLS
# prompt, see tool_registry.py) and CMD_MAP (the actual dispatcher) have
# drifted apart. This is the exact bug class that used to be possible
# silently: click_by_index was hand-typed into the SYSTEM_PROMPT text and was
# dispatchable via CMD_MAP, but had no @register_tool entry at all — nothing
# would have caught that if a future edit removed it from CMD_MAP (or from
# the prompt) without the other side being updated to match.
verify_registry_matches(CMD_MAP.keys())
