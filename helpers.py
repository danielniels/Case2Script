"""
Pure utilities + low-level Playwright DOM helpers.
No imports from other project files — zero circular risk.
"""

import base64
import json
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import Page, Locator

from toast_constants import TOAST_FAILURE_PHRASES, TOAST_SUCCESS_PHRASES


# ==================== JS string helper ====================

def _js(s: str) -> str:
    """Safely wrap a value as a JS double-quoted string."""
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


# ==================== Logging ====================

def log(session_id: str, msg: str):
    """Prefix every log line with sessionId for parallelism tracing."""
    print(f"[{session_id}] {msg}")


# ==================== Selector & URL helpers ====================

def normalize_selector(sel: str) -> str:
    sel = sel.strip()
    if sel.startswith(("//", "(//", "xpath=", "css=", "text=")):
        return sel
    if re.match(r'^[A-Z]+\[', sel):
        return f"xpath=//{sel}"
    if sel.startswith("./"):
        return f"xpath={sel}"
    return sel


def is_absolute_http_url(url: str) -> bool:
    try:
        r = urlparse(url)
        return r.scheme in ("http", "https") and bool(r.netloc)
    except Exception:
        return False


def extract_first_url(text: str) -> Optional[str]:
    """Extract the first http/https URL found in a string."""
    if not text:
        return None
    match = re.search(r'https?://[^\s"\'<>]+', text)
    return match.group(0) if match else None


def coerce_llm_json(maybe_json) -> dict:
    if isinstance(maybe_json, dict):
        return maybe_json
    if isinstance(maybe_json, str):
        cleaned = maybe_json.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except Exception:
            pass
    return {}


def clean_excel_formula(text: str) -> str:
    if text and isinstance(text, str) and text.startswith("="):
        return text[1:].strip()
    return text or ""


def screenshot_to_base64(screenshot_path: str) -> Optional[str]:
    if not screenshot_path:
        return None
    try:
        p = Path(screenshot_path)
        if not p.exists():
            return None
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def resolve_toast_type(toast_type: str, toast_text: str) -> str:
    """
    Upgrade an 'unknown' JS verdict using a curated text-phrase whitelist.
    Never overrides a class-based 'success'/'error' verdict from JS —
    CSS class detection is more reliable than text matching, so it always
    wins. Layer 3 in the resolution chain (after CSS class + generic
    OK/ERR keyword, both already decided in JS).
    """
    if toast_type != "unknown" or not toast_text:
        return toast_type

    text_lower = toast_text.lower()

    if any(phrase in text_lower for phrase in TOAST_FAILURE_PHRASES):
        return "error"
    if any(phrase in text_lower for phrase in TOAST_SUCCESS_PHRASES):
        return "success"

    return toast_type


def generate_expected_result(method: str, params: dict, step_description: str,
                             provided_expected: str = None) -> str:
    if provided_expected:
        return provided_expected
    templates = {
        "navigate": f"Successfully navigated to {params.get('url', 'the target URL')}",
        "click": f"Element '{params.get('selector', '')}' clicked successfully",
        "fill": f"Text '{params.get('text', '')}' entered in '{params.get('selector', '')}'",
        "hover": f"Hovered over '{params.get('selector', '')}'",
        "get_text": "Text content retrieved successfully",
        "screenshot": "Screenshot captured successfully",
        "get_page_info": "Page information retrieved",
        "get_interactable_elements": "Interactable elements listed",
        "press_key": f"Key '{params.get('key', '')}' pressed",
        "wait_for_load": "Page load completed",
        "close_session": "Session closed",
    }
    return templates.get(method, f"Step '{step_description}' completed successfully")


# ==================== XPath Fix ====================

def _fix_selector(sel: str) -> str:
    """Apply all XPath auto-fix rules consistently."""
    fixed = sel

    # Normalize Unicode curly/smart quotes → straight equivalents
    fixed = fixed.replace('“', '"').replace('”', '"')
    fixed = fixed.replace('‘', "'").replace('’', "'")

    def _fix_quote_conflict(s: str) -> str:
        pattern = r'normalize-space\(\.\)\s*=\s*"(.*)"'
        m = re.search(pattern, s, re.DOTALL)
        if m:
            raw = m.group(1)
            if '"' in raw:
                return s[:m.start()] + f"normalize-space(.) = '{raw}'" + s[m.end():]
        return s

    fixed = _fix_quote_conflict(fixed)

    if not fixed.startswith(("xpath=", "css=", "text=", "//")):
        m = re.match(r'^([A-Z]+)\[(.+)\]$', fixed)
        if m:
            tag, condition = m.groups()
            condition = condition.replace("text()", "normalize-space(.)")
            condition = re.sub(r"text=(['\"])", r"normalize-space(.)=\1", condition)
            fixed = f"xpath=//{tag}[{condition}]"
    if "text()" in fixed:
        fixed = re.sub(r'text\(\)\s*=', 'normalize-space(.)=', fixed)

    if 'text()[normalize-space' not in fixed:
        def _to_textnode(m):
            clean = m.group(1).split('\n')[0].strip()
            if not clean:
                return m.group(0)
            if '"' in clean:
                return f".//text()[normalize-space(.) = '{clean}']"
            return f'.//text()[normalize-space(.) = "{clean}"]'
        fixed = re.sub(r'normalize-space\(\.\)\s*=\s*"([^"]*)"', _to_textnode, fixed)

    return normalize_selector(fixed)


# ==================== Smart Fix LLM Output ====================

def smart_fix_llm_output(llm_output: dict, user_step_description: str = "") -> dict:
    """
    Normalize method names, detect popup keywords, fix XPath selectors.
    Purely rule-based — no network calls.
    """
    if not isinstance(llm_output, dict):
        return llm_output

    method = str(llm_output.get("method", "")).strip().lower()
    params = llm_output.get("params") or {}
    if not isinstance(params, dict):
        params = {}

    METHOD_ALIASES = {
        "go_to": "navigate", "goto": "navigate", "open": "navigate",
        "open_url": "navigate", "load": "navigate", "visit": "navigate",
        "tap": "click", "press": "click", "select": "click",
        "type": "fill", "input": "fill", "enter_text": "fill", "set_text": "fill",
        "write": "fill", "send_keys": "fill",
        "get_elements": "get_interactable_elements",
        "get_interactable": "get_interactable_elements",
        "elements": "get_interactable_elements",
        "take_screenshot": "screenshot", "capture": "screenshot",
        "get_content": "get_page_content", "page_content": "get_page_content",
        "get_info": "get_page_info", "page_info": "get_page_info",
        "wait": "wait_for_load", "wait_load": "wait_for_load",
        "select_option": "select_option", "selectoption": "select_option",
        "choose_option": "select_option", "pick_option": "select_option",
        "key": "press_key", "keyboard": "press_key",
        "close": "close_session",
        "scroll": "scroll_to_element", "scroll_into_view": "scroll_to_element",
        "dblclick": "double_click", "double_tap": "double_click",
        "clear": "clear_input", "clear_field": "clear_input",
        "get_attr": "get_attribute", "attribute": "get_attribute",
        "assert": "assert_text", "check_text": "assert_text",
        "check_visible": "assert_visible", "is_visible": "assert_visible",
        "upload": "upload_file", "file_upload": "upload_file",
        "switch_to_tab": "switch_tab", "focus_tab": "switch_tab",
    }
    method = METHOD_ALIASES.get(method, method)

    desc_lower = user_step_description.lower()
    popup_keywords = ["press esc", "esc key", "escape", "close popup", "close modal",
                      "dismiss", "click outside", "tutup popup", "tutup pop up", "tutup modal"]
    if any(k in desc_lower for k in popup_keywords):
        method = "press_key"
        params = {**params, "key": "Escape"}

    enter_keywords = ["press enter", "hit enter", "tekan enter", "submit form"]
    if any(k in desc_lower for k in enter_keywords) and method not in (
            "click", "fill", "navigate"):
        method = "press_key"
        params = {**params, "key": "Enter"}

    centang_keywords = ["centang", "checklist", "ceklis", "klik checkbox", "check "]
    if any(k in desc_lower for k in centang_keywords) and ":" in user_step_description:
        label_text = user_step_description.split(":", 1)[1].strip()
        if label_text:
            method = "click"
            params = {**params, "selector": (
                f'xpath=//input[@type="checkbox" and ('
                f'@id=(//label[contains(., "{label_text}")]/@for) or '
                f'ancestor::label[contains(., "{label_text}")]'
                f')]'
            )}

    assert_keywords = ["verifikasi muncul:", "pastikan muncul:", "cek muncul:", "assert:"]
    for ak in assert_keywords:
        if ak in desc_lower:
            element_text = user_step_description.split(":", 1)[1].strip()
            if element_text:
                method = "assert_text"
                params = {**params,
                          "selector": "//body",
                          "expected": element_text}
            break

    upload_keywords = ["klik untuk unggah", "click untuk unggah", "unggah dokumen", "untuk unggah"]
    if any(k in desc_lower for k in upload_keywords) and method == "click":
        parts = re.split(r'unggah\s+', user_step_description, flags=re.IGNORECASE)
        if len(parts) > 1:
            doc_name = parts[1].strip()
            if doc_name:
                params = {**params, "selector": (
                    f'xpath=//div[@data-act="pb-upload" and '
                    f'.//b[contains(normalize-space(.), "{doc_name}")]]'
                )}

    verification_keywords = [
        "berhasil", "sukses", "success", "successfully",
        "halaman ", "page ", "tampil", "muncul", "terlihat",
        "verify", "verifikasi", "pastikan", "cek ", "check ",
        "memastikan", "konfirmasi", "confirm",
    ]
    scraping_methods = {
        "get_page_content_and_save_csv", "get_page_content_and_save_txt",
        "get_page_content", "get_interactable_elements",
    }
    if any(k in desc_lower for k in verification_keywords) and method in scraping_methods:
        method = "screenshot"
        params = {k: v for k, v in params.items() if k == "sessionId"}

    if method == "fill" and "→" in user_step_description:
        parts = user_step_description.split("→", 1)
        extracted = parts[1].strip()
        if extracted:
            params = {**params, "text": extracted}

    selection_keywords = [
        "pilih ", "memilih ",
        "select ", "choose ", "pick ",
        "choisir ", "sélectionner ",
        "wählen ", "auswählen ",
        "seleccionar ", "elegir ", "escoger ",
        "selecionar ", "escolher ",
        "sentaku ", "erabu ",
    ]
    if method in ("fill", "select_option", "choose_option", "pick_option") and any(k in desc_lower for k in selection_keywords):
        if ":" in user_step_description and "→" not in user_step_description:
            target_value = user_step_description.split(":", 1)[1].strip()
            if target_value:
                method = "select_option"
                params = {**params, "value": target_value,
                          "selector": params.get("selector", "xpath=//*[normalize-space(.)='"+target_value+"']")}

    sel = params.get("selector", "")
    if sel:
        if "normalize-space(text())" in sel:
            sel = sel.replace("normalize-space(text())", "normalize-space(.)")
        sel = re.sub(r'text\(\)\s*=', 'normalize-space(.)=', sel)
        sel = sel.replace("@aria_label", "@aria-label")
        sel = sel.replace("@data_testid", "@data-testid")
        sel = sel.replace("@aria_controls", "@aria-controls")
        sel = sel.replace("@aria_hidden", "@aria-hidden")
        params = {**params, "selector": sel}

    return {"method": method, "params": params}


# ==================== DOM helpers (require Playwright Page) ====================

async def _force_action(page: Page, selector: str, action: str, text: str = ""):
    """
    Executes raw JavaScript inside the browser to forcefully find and interact with an element,
    even if it's hidden inside multiple layers of cross-origin iframes.
    """
    js_script = """
    (args) => {
        const [selector, action, text] = args;

        function isVisible(el) {
            if (!el || el.nodeType !== 1) return false;
            const style = window.getComputedStyle(el);
            if (style.display === 'none' || style.visibility === 'hidden') return false;
            const rect = el.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
        }

        function buildStableSelector(el) {
            if (el.id && !/\\d{3,}/.test(el.id) && !el.id.startsWith('select2-')) {
                return '#' + CSS.escape(el.id);
            }
            const testid = el.getAttribute('data-testid');
            if (testid) return `[data-testid="${testid}"]`;
            const name = el.getAttribute('name');
            if (name) return `${el.tagName.toLowerCase()}[name="${name}"]`;
            const aria = el.getAttribute('aria-label');
            if (aria) return `${el.tagName.toLowerCase()}[aria-label="${aria}"]`;
            const direct = Array.from(el.childNodes)
                .filter(n => n.nodeType === 3)
                .map(n => n.textContent.trim())
                .filter(Boolean).join(' ');
            if (direct) {
                return `//${el.tagName.toLowerCase()}[.//text()[normalize-space(.) = "${direct}"]]`;
            }
            if (typeof el.className === 'string' && el.className.trim()) {
                const cls = el.className.trim().split(/\\s+/).slice(0, 2).map(CSS.escape).join('.');
                return `${el.tagName.toLowerCase()}.${cls}`;
            }
            return null;
        }

        function findInDoc(doc) {
            let candidates = [];
            if (selector.startsWith('//') || selector.startsWith('/*')) {
                try {
                    const r = doc.evaluate(selector, doc, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                    for (let i = 0; i < r.snapshotLength; i++) candidates.push(r.snapshotItem(i));
                } catch(e) {}
            }
            if (candidates.length === 0) {
                try { candidates = Array.from(doc.querySelectorAll(selector)); } catch(e) {}
            }
            return candidates.find(isVisible) || candidates[0] || null;
        }

        function findElement(doc) {
            let el = findInDoc(doc);
            if (el) return el;
            const iframes = doc.querySelectorAll('iframe');
            for (let i = 0; i < iframes.length; i++) {
                try {
                    const frameDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                    if (frameDoc) {
                        const found = findElement(frameDoc);
                        if (found) return found;
                    }
                } catch(e) {}
            }
            return null;
        }

        const target = findElement(document);
        if (!target) return false;

        if (action === 'click') {
            if (target.tagName === 'OPTION') {
                const select = target.closest('select');
                const isSelect2 = select && (
                    select.classList.contains('select2-hidden-accessible') ||
                    select.hasAttribute('data-select2-id')
                );
                if (isSelect2) {
                    const s2id = select.getAttribute('data-select2-id');
                    let trigger = s2id
                        ? document.querySelector(`span.select2-container[data-select2-id="${s2id}"]`)
                          ?? document.querySelector(`span[data-select2-id]`)
                        : null;
                    if (!trigger) {
                        trigger = select.previousElementSibling?.classList?.contains('select2-container')
                            ? select.previousElementSibling
                            : select.parentElement?.querySelector('span.select2-container');
                    }
                    if (trigger) trigger.click();

                    return new Promise(resolve => {
                        setTimeout(() => {
                            const optionText = target.textContent.trim();
                            const optionValue = target.value;
                            const li = Array.from(document.querySelectorAll(
                                'li.select2-results__option, ul.select2-results__options li'
                            )).find(el =>
                                el.textContent.trim() === optionText ||
                                el.getAttribute('data-value') === optionValue ||
                                el.id?.includes(optionValue)
                            );
                            if (li) { li.click(); resolve({ ok: true, resolved: buildStableSelector(target) }); }
                            else resolve(false);
                        }, 400);
                    });
                }

                const select2 = target.closest('select');
                if (select2) {
                    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
                    if (nativeSetter?.set) nativeSetter.set.call(select2, target.value);
                    else select2.value = target.value;
                    select2.dispatchEvent(new Event('change', { bubbles: true }));
                    select2.dispatchEvent(new Event('input',  { bubbles: true }));
                    return { ok: true, resolved: buildStableSelector(target) };
                }
            }
            target.click();
            return { ok: true, resolved: buildStableSelector(target) };
        } else if (action === 'fill') {
            const desc = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')
                      || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
            if (desc && desc.set) {
                desc.set.call(target, text);
            } else {
                target.value = text;
            }
            target.dispatchEvent(new Event('input',  { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
            return { ok: true, resolved: buildStableSelector(target) };
        } else if (action === 'text') {
            return target.innerText || target.value || '';
        }
        return false;
    }
    """

    try:
        result = await page.evaluate(js_script, [selector, action, text])
        if result:
            print(f"[DOM-INJECT] '{action}' on '{selector}' via main page JS.")
            return result
    except Exception:
        pass

    for frame in page.frames:
        if frame == page.main_frame:
            continue
        try:
            result = await frame.evaluate(js_script, [selector, action, text])
            if result:
                print(f"[DOM-INJECT] '{action}' on '{selector}' inside iframe: {frame.name or frame.url}")
                return result
        except Exception:
            continue

    return False


async def _find_locator(page: Page, selector: str) -> "Locator":
    loc = page.locator(selector)
    try:
        if await loc.count() > 0:
            return loc.first
    except Exception:
        pass

    for frame in page.frames:
        if frame == page.main_frame:
            continue
        try:
            floc = frame.locator(selector)
            if await floc.count() > 0:
                return floc.first
        except Exception:
            pass

    aria_match = re.search(r"@aria-label=['\"]([^'\"]+)['\"]", selector)
    if aria_match:
        label_text = aria_match.group(1)
        for role in ("button", "link", "menuitem", "tab", "option"):
            try:
                fuzzy = page.get_by_role(role, name=label_text)
                if await fuzzy.count() > 0:
                    print(f"[_find_locator] Fuzzy match: role={role} name={label_text!r}")
                    return fuzzy.first
            except Exception:
                pass
        try:
            text_loc = page.get_by_text(label_text, exact=False)
            if await text_loc.count() > 0:
                print(f"[_find_locator] Text fallback match for: {label_text!r}")
                return text_loc.first
        except Exception:
            pass

    print(f"[_find_locator] Element not found immediately, relying on Playwright auto-wait: {selector!r}")
    return loc.first


async def _select2_pick(page: Page, selector: str, value: str) -> bool:
    """
    Open the correct Select2 trigger using Playwright's native click,
    then wait for <li> items and click the matching one.
    """
    info = await page.evaluate("""
        ([selector, value]) => {
            let select = null;
            try {
                function isVisible(node) {
                    const s = window.getComputedStyle(node);
                    return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
                }
                let el = null;
                if (selector.startsWith('//') || selector.startsWith('xpath=')) {
                    const xsel = selector.replace('xpath=','');
                    const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                    for (let i = 0; i < r.snapshotLength; i++) {
                        const node = r.snapshotItem(i);
                        if (isVisible(node)) { el = node; break; }
                    }
                } else {
                    const nodes = document.querySelectorAll(selector);
                    for (const node of nodes) {
                        if (isVisible(node)) { el = node; break; }
                    }
                }
                if (el?.tagName === 'SELECT') select = el;
                else if (el?.tagName === 'OPTION') select = el.closest('select');
            } catch(e) {}

            if (!select?.classList.contains('select2-hidden-accessible')) {
                for (const s of document.querySelectorAll('select.select2-hidden-accessible, select[data-select2-id]')) {
                    if (Array.from(s.options).some(o =>
                        o.text.trim() === value ||
                        o.text.trim().toLowerCase().includes(value.toLowerCase()) ||
                        o.value === value
                    )) { select = s; break; }
                }
            }
            if (!select) return null;

            const parent = select.parentElement;
            const container = parent?.querySelector('span.select2-container');
            return container ? container.getAttribute('data-select2-id') : null;
        }
    """, [selector, value])

    if not info:
        print(f"[Select2] No Select2 found containing option '{value}'")
        return False

    trigger_loc = page.locator(
        f'span.select2-container[data-select2-id="{info}"] span.select2-selection'
    )
    try:
        await trigger_loc.click(timeout=5000)
        print(f"[Select2] Trigger clicked for container data-select2-id='{info}'")
    except Exception as e:
        print(f"[Select2] Trigger click failed: {e}")
        return False

    try:
        await page.wait_for_selector("li.select2-results__option", state="visible", timeout=4000)
    except Exception:
        print(f"[Select2] Dropdown did not open after trigger click")
        return False

    items = page.locator("li.select2-results__option")
    count = await items.count()
    for i in range(count):
        li = items.nth(i)
        text = (await li.text_content() or "").strip()
        if text == value:
            await li.click()
            print(f"[Select2] Exact match clicked: '{text}'")
            return True
    for i in range(count):
        li = items.nth(i)
        text = (await li.text_content() or "").strip()
        if value.lower() in text.lower():
            await li.click()
            print(f"[Select2] Partial match clicked: '{text}' for '{value}'")
            return True

    print(f"[Select2] Option '{value}' not found in dropdown ({count} items)")
    return False
