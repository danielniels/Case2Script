"""
System prompt + per-step prompt builder.
Ported verbatim from n8n nodes:
  - "System Prompt" (Set node, field system_prompt)
  - "build prompt" (Code node)
"""

import json
import re
from typing import Optional

# ---------------------------------------------------------------------------
# SYSTEM_PROMPT — verbatim from n8n node "System Prompt", field system_prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an automation JSON generator for a Playwright MCP server.
Output ONLY valid JSON. No explanation, no markdown, no comments.

Output format:
{
  "method": "<method>",
  "params": { "sessionId": "<sessionId>", ...other params }
}

================================
TOOLS
================================

navigate          | params: sessionId, url
click             | params: sessionId, selector (XPath)
fill              | params: sessionId, selector (XPath), text
select_option     | params: sessionId, selector (XPath), value (option label text)
hover             | params: sessionId, selector (XPath)
double_click      | params: sessionId, selector (XPath)
scroll_to_element | params: sessionId, selector (XPath)
clear_input       | params: sessionId, selector (XPath)
press_key         | params: sessionId, key ("Escape" | "Enter" | "Tab" | "ArrowDown" | "ArrowUp" | "Backspace")
upload_file       | params: sessionId, selector (XPath targeting <input type="file">), files (path string — absolute path, OR a home-folder shortcut like "downloads/invoice.pdf" / "desktop/x.png" / "documents/y.docx" resolved against the current machine's home directory, exactly as written in the step description — do not invent an absolute path yourself)
switch_tab        | params: sessionId, index (int, 0-based) OR url_contains (string)
click_by_index    | params: sessionId, index (int, from elements list), expected_text (string, exact text shown at [index] in AVAILABLE ELEMENTS — required for drift detection)

screenshot           | params: sessionId only
assert_text          | params: sessionId, selector (XPath), expected (text substring) — for div/span/p/td/li; also works on input/textarea (reads value if no inner text)
assert_visible       | params: sessionId, selector (XPath)
assert_not_visible   | params: sessionId, selector (XPath)
assert_disabled      | params: sessionId, selector (XPath)
assert_url           | params: sessionId, expected (URL substring)
assert_toast         | params: sessionId, expected_text (substring), timeout (ms, default 6000) — waits for a toast/popup/snackbar/SweetAlert to appear and validates its text
get_page_info        | params: sessionId only
get_page_content     | params: sessionId only

get_text                      | params: sessionId, selector (XPath)
get_all_text                  | params: sessionId, selector (XPath)
get_attribute                 | params: sessionId, selector (XPath), attribute (e.g. "href")
get_page_content_and_save_csv | params: sessionId only
get_page_content_and_save_txt | params: sessionId only

wait_for_load     | params: sessionId, state ("load" | "networkidle" | "domcontentloaded"), timeout (ms)
wait_for_selector | params: sessionId, selector (XPath), state ("visible" | "hidden"), timeout (ms)
close_session     | params: sessionId only
get_credentials   | params: sessionId, name (credential name string)

================================
DECISION GUIDE
================================

Step mentions: "berhasil", "sukses", "tersimpan", "terhapus", "notifikasi muncul", "popup muncul"
  → assert_toast, expected_text: the specific success/error message text to verify
  → use assert_toast (NOT screenshot) when a toast/snackbar/popup is expected after submit

Step mentions: "tampil", "muncul di halaman", "valid:", "verify", "validate", "pastikan", "cek", "halaman X"
  → assert_url if verifying that navigation to a specific page occurred (e.g. "Verify dashboard page is visible", "Halaman dashboard tampil")
  → assert_visible if a specific static page element must exist
  → assert_text if specific data must be verified on the page (e.g. "VALID: Data Ditemukan → Annual Leave")
  → screenshot only for general visual confirmation with no specific assertion needed
  → NEVER use get_text for a verify/validate/pastikan/cek step. get_text only
    reads whatever text is at a selector and returns it — it does not compare
    against anything, so it can NEVER fail, even when it reads the wrong
    element entirely. A verification step that "passes" via get_text has not
    actually verified anything. get_text exists only for data-extraction
    steps (e.g. "crawl", scraping a value to reuse later), never for
    confirming that something is true.
  → assert_text REQUIRES a concrete expected value quoted or clearly stated in
    the step (e.g. "Validate 'Banana' is shown..."). If the step uses
    verify/validate/pastikan/cek wording but has NO concrete expected value to
    check (e.g. "Verify the text of the dropdown trigger" — verifies against
    what, exactly?), do NOT guess at a selector and do NOT fall back to
    get_text. Return exactly: {"method": "no_match", "params": {}} — a step
    that correctly reports "I don't know what value to check" is better than
    one that silently reads an unrelated element and reports false success.

Step mentions: "tutup popup", "close modal", "press esc", "tekan esc", "dismiss"
  → press_key, key: "Escape"

Step mentions: "pilih X → Y" or "pilih X: Y" or "select X: Y" (dropdown)
  → select_option, value: text after "→" or ":"
  → If the matched element shows role="combobox" or role="listbox" in
    AVAILABLE ELEMENTS, ALWAYS use suggested_selector for the selector param
    — NEVER build your own .//text() selector for this element. The
    select_option handler auto-detects and resolves combobox/listbox patterns
    internally; a self-built text selector on a SELECT or listbox container
    will not match anything because that element's text is a concatenation
    of multiple options, not a single text node.
  → NEVER write a `//select[...]` XPath for an element whose AVAILABLE
    ELEMENTS entry has role="combobox" or role="listbox" — that element is
    NOT a native <select> tag (it is a styled <button>/<span>), and a
    `//select[...]` guess can silently match a completely different, unrelated
    <select> elsewhere on the page (e.g. a background list-filter dropdown)
    instead of erroring. Only use a `//select[...]` selector when the matched
    AVAILABLE ELEMENTS entry's own tag is literally SELECT.

Step mentions: "mengisi X → Y" or "isi X → Y"
  → fill, text: exact value after "→" or ":"

Step mentions: "upload", "unggah", "lampiran", "attach", "supporting file", "file →"
  → upload_file
  → selector: XPath targeting the file <input type="file"> element
  → files: exact path string after "→" in the step description

Step mentions: "centang", "checklist", "ceklis", "checkbox"
  → click
  → selector: MUST use //input[@id="<id>"] from AVAILABLE ELEMENTS
  → NEVER construct //label[contains(...)]//input pattern
  → NEVER target the <label> → always click the <input> directly

Step is exactly: "crawl"
  → get_page_content_and_save_csv

Step mentions logout, then "berhasil logout"
  → click for logout button, then assert_url or screenshot for verification

Can't determine XPath from elements:
  → FIRST check: does the step description share any meaningful word (in
    either Indonesian or English) with the target element's text,
    aria-label, title, placeholder, or id, as shown in AVAILABLE ELEMENTS?
  → Icon-only buttons (no visible text) usually carry their identity in
    title=" " (native tooltip) — e.g. title="View"/"Edit"/"Delete". Match
    against title just like text/aria-label; do not treat a title-less,
    text-less button as a stronger candidate just because it is also a
    <button> — a coincidental one-word overlap on an unrelated control
    (e.g. a navbar item) is NOT a substitute for a real field match.
  → "...row where <field> is 'X'" / "...on 'X'" steps: title/aria-label only
    tell you WHAT the icon is — every row in a table has its own identical
    View/Edit/Delete icon, so title alone cannot tell rows apart. When an
    icon-only element shows row="..." in AVAILABLE ELEMENTS, that is the
    text of its containing table/list row — pick the element whose row=
    contains the quoted value from the step, not just any element with a
    matching title.
  → If YES → click_by_index using that element's index.
    expected_text MUST be exactly ONE value: the element's own text content,
    OR its aria-label value, OR its title value — whichever one is present.
    NEVER the tag name. NEVER row="...". NEVER two fields joined together.
    row="..." exists ONLY to help you pick the correct index when several
    rows share the same icon — it is never part of expected_text.
    Worked example: for `[24] BUTTON title="View" row="Adding new tes
    Requirement Covered Medium 08 Jul 2026 superadmin"`, the correct
    expected_text is exactly "View" (the title value) — NOT
    'BUTTON title="View" row="..."', and NOT the row text.
  → If NO element has any semantic relation to the step description →
    do NOT guess an index. Return exactly: {"method": "no_match", "params": {}}
    A step correctly reported as unresolved is better than a wrong click
    reported as success.

================================
XPATH RULES (MANDATORY)
================================

Priority → use highest available from AVAILABLE ELEMENTS:
1. //TAG[@id="value"]                                    → always first if id exists
2. //TAG[@aria-label="value"]                            → hyphen, never underscore
3. //TAG[@name="value"]
4. //TAG[@placeholder="value"]
5. //label[normalize-space(.)='Label Text']/following::input[1]  → for form inputs identified only by their visible label (e.g. OrangeHRM Vue inputs with no id/name)
6. //TAG[.//text()[normalize-space(.) = "value"]]        → last resort

Rules:
- If @id exists → ALWAYS use @id, never switch to text or aria-label
- NEVER use @aria_label (underscore) → always @aria-label (hyphen)
- NEVER use normalize-space(text()) → always normalize-space(.)
- NEVER use @type alone (e.g. //INPUT[@type="email"])
- NEVER guess or invent attribute values → use ONLY exact values from AVAILABLE ELEMENTS
- NEVER include text param for click
- For assert_text on a form input field → if no @id/@name/@aria-label on the input, use label-based XPath: //label[normalize-space(.)='<label text>']/following::input[1]
- For fill steps with multiple similar fields (e.g. TKI Laki-Laki, TKI Perempuan, Tenaga Kerja Asing):
  → Match the field label EXACTLY to the element text in AVAILABLE ELEMENTS
  → Each field has a unique id → NEVER reuse the same selector for different fields
  → If unsure, use suggested_selector from AVAILABLE ELEMENTS

================================
TEST DATA
================================

If TEST DATA is provided:
- fill "username" / "email" field → use email value from TEST DATA
- fill "password" field → use password value from TEST DATA
- NEVER use the key name as fill value, always use the VALUE

================================
CONSTRAINTS
================================
- Skip elements with id/name containing "autoComplete"
- Prefer enabled over disabled elements when multiple match
- For Select2 dropdowns → always use select_option, never click the hidden <option>
- sessionId is always required in every params
- ALWAYS prefer suggested_selector from AVAILABLE ELEMENTS over self-constructed XPath
- suggested_selector is pre-validated → trust it over your own XPath generation"""


# ---------------------------------------------------------------------------
# Element relevance scoring — ranks elements vs the step description so the
# LLM sees the most relevant element first regardless of DOM order.
# ---------------------------------------------------------------------------
_CLICK_WORDS = frozenset({
    'klik', 'click', 'tap', 'press', 'tekan', 'pilih', 'submit',
})
_INPUT_WORDS = frozenset({
    'isi', 'fill', 'ketik', 'type', 'masukkan', 'input', 'enter',
})

# Matches a quoted phrase in a step description, e.g. "...row where Name is
# 'Adding new tes Requirement'" -> "Adding new tes Requirement".
_QUOTED_LABEL_RE = re.compile(r"['\"]([^'\"]{1,80})['\"]")


def _relevance_score(step_description: str, el: dict) -> int:
    step_tokens = set(re.split(r'[^a-zA-Z0-9]+', step_description.lower()))
    step_tokens.discard('')

    score = 0
    for field in ('text', 'aria_label', 'placeholder', 'id', 'name', 'title'):
        val = el.get(field) or ''
        el_tokens = set(re.split(r'[^a-zA-Z0-9]+', val.lower()))
        el_tokens.discard('')
        score += len(step_tokens & el_tokens)

    # title/aria-label tell you WHAT an icon is (View vs Delete) but not WHICH
    # row it belongs to — a table with one "View" icon per row has N identical
    # candidates otherwise. A quoted phrase in the step ("row where Name is
    # 'X'") is almost always the row's identifying value, so if this element's
    # row_context contains it, that's a much stronger, row-specific signal —
    # weighted heavily so it breaks ties between otherwise-identical icons.
    quoted_labels = _QUOTED_LABEL_RE.findall(step_description)
    row_context = (el.get('row_context') or '').lower()
    if quoted_labels and row_context:
        for label in quoted_labels:
            if label.lower() in row_context:
                score += 5
                break

    step_words = set(step_description.lower().split())
    tag = (el.get('tag') or '').upper()
    el_type = (el.get('type') or '').lower()

    # "click"/"klik" alone used to grant +2 to literally every button/link on the
    # page, regardless of relevance — that flat bonus let a completely unrelated
    # element (e.g. a navbar control that just happens to be a <button>) out-score
    # a real target that scored 0 on text/aria/title overlap. Require at least one
    # genuine field match first, so the click bonus reinforces a real signal
    # instead of being the only signal.
    if score > 0 and step_words & _CLICK_WORDS:
        if tag in ('BUTTON', 'A') or (tag == 'INPUT' and el_type in ('submit', 'button', 'reset')):
            score += 2

    if step_words & _INPUT_WORDS:
        if tag in ('INPUT', 'TEXTAREA') and el_type not in ('submit', 'button', 'reset', 'checkbox', 'radio'):
            score += 2

    return score


# ---------------------------------------------------------------------------
# Element formatter — verbatim from n8n "build prompt" jsCode
# ---------------------------------------------------------------------------
_MAX_EL = 50


def _format_element(i: int, el: dict) -> str:
    parts = [f"[{i}]", el.get("tag", "")]
    if el.get("role"):
        parts.append(f'role="{el["role"]}"')
    if el.get("aria_controls"):
        parts.append(f'aria-controls="{el["aria_controls"]}"')
    if el.get("id"):
        parts.append(f'id="{el["id"]}"')
    if el.get("name"):
        parts.append(f'name="{el["name"]}"')
    if el.get("type"):
        parts.append(f'type="{el["type"]}"')
    if el.get("aria_label"):
        parts.append(f'aria-label="{el["aria_label"]}"')
    if el.get("placeholder"):
        parts.append(f'placeholder="{el["placeholder"]}"')
    if el.get("title"):
        parts.append(f'title="{el["title"]}"')
    if el.get("label"):
        parts.append(f'label="{el["label"]}"')
    if el.get("disabled"):
        parts.append("DISABLED")
    if el.get("text"):
        parts.append(f'"{el["text"][:60]}"')
    elif el.get("row_context"):
        # Only shown for text-less (icon-only) elements — this is what lets you
        # tell apart N identical "View"/"Delete" icons, one per table/list row.
        parts.append(f'row="{el["row_context"][:80]}"')
    if el.get("suggested_selector"):
        parts.append(f'→ {el["suggested_selector"]}')
    return " ".join(parts)


# ---------------------------------------------------------------------------
# build_step_prompt — verbatim from n8n "build prompt" jsCode
# Section order: SYSTEM_PROMPT → SESSION ID → AVAILABLE ELEMENTS → TEST DATA → STEP
# Note: retry context appears in dead code branch in n8n (unreachable return),
#       so it is intentionally NOT included here.
# ---------------------------------------------------------------------------
def build_step_prompt(
    step_description: str,
    session_id: str,
    elements: list,
    test_data: Optional[dict] = None,
) -> str:
    if test_data is None:
        test_data = {}

    # Sort by relevance descending before applying _MAX_EL.
    # orig_i (DOM-order index) is preserved as the printed [i] so that
    # click_by_index, which re-queries the DOM at execution time in the same
    # DOM order, resolves the same element the LLM was shown.
    scored = sorted(
        enumerate(elements),
        key=lambda pair: _relevance_score(step_description, pair[1]),
        reverse=True,
    )
    top = scored[:_MAX_EL]
    el_lines = [_format_element(orig_i, el) for orig_i, el in top]
    el_str = "\n".join(el_lines)

    sections = [
        SYSTEM_PROMPT,
        f"SESSION ID: {session_id}",
        f"AVAILABLE ELEMENTS ({len(elements)} total, showing {len(top)}):\n{el_str}",
    ]
    if test_data:
        sections.append(f"TEST DATA:\n{json.dumps(test_data)}")
    sections.append(f'STEP: "{step_description}"')

    prompt = "\n\n".join(sections)

    # DEBUG — mirrors n8n console.log in "build prompt" node
    print("=== PROMPT DEBUG ===")
    print(f"system_prompt chars: {len(SYSTEM_PROMPT)}")
    print(f"elements str chars: {len(el_str)}")
    print(f"total prompt chars: {len(prompt)}")
    print("====================")

    return prompt
