"""
System prompt + per-step prompt builder.
Ported verbatim from n8n nodes:
  - "System Prompt" (Set node, field system_prompt)
  - "build prompt" (Code node)

The TOOLS section of the system prompt is the one part NOT verbatim/static
anymore — it's generated at request time from tool_registry.TOOL_REGISTRY
(see _get_system_prompt below) so it can never drift out of sync with
tools.CMD_MAP the way the old hand-typed copy could.
"""

import json
import re
from typing import Optional

# ---------------------------------------------------------------------------
# SYSTEM_PROMPT — head/tail are verbatim from n8n node "System Prompt", field
# system_prompt; the TOOLS section between them is generated, see
# _get_system_prompt().
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT_HEAD = """You are an automation JSON generator for a Playwright MCP server.
Output ONLY valid JSON. No explanation, no markdown, no comments.

Output format:
{
  "method": "<method>",
  "params": { "sessionId": "<sessionId>", ...other params }
}

================================
TOOLS
================================"""

_system_prompt_cache: Optional[str] = None


def _get_system_prompt() -> str:
    """Lazily build SYSTEM_PROMPT: head (static) + TOOLS table (generated from
    tool_registry.TOOL_REGISTRY, single source of truth shared with
    tools.CMD_MAP) + tail (static — decision guide / xpath rules / test data
    / constraints, unchanged).

    Must stay lazy, not a module-level constant: tools.py does
    `from orchestrator.prompts import _relevance_score` near the top of its
    file, BEFORE any of its @register_tool decorators run further down — if
    this module built the prompt at import time, TOOL_REGISTRY would still be
    empty and the TOOLS section would render blank. By the time
    build_step_prompt() is actually called at request time, tools.py has
    finished importing and every tool is registered, so building once here
    (cached) is both correct and cheap.
    """
    global _system_prompt_cache
    if _system_prompt_cache is None:
        from tool_registry import render_tools_table
        _system_prompt_cache = (
            # _SYSTEM_PROMPT_TAIL already starts with its own leading "\n"
            # (left over from the original file's blank line before the
            # DECISION GUIDE divider) — so only one more "\n" is needed here
            # to reproduce the original single blank line between the TOOLS
            # table and that divider, not two.
            _SYSTEM_PROMPT_HEAD + "\n\n" + render_tools_table() + "\n" + _SYSTEM_PROMPT_TAIL
        )
    return _system_prompt_cache


_SYSTEM_PROMPT_TAIL = """
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
  → IMPORTANT exception to the "must appear in AVAILABLE ELEMENTS" rule
    (that rule is about click/click_by_index picking a REAL element to
    interact with — it does not apply here): assert_text's target is very
    often plain non-interactive text (a stat, counter, status label) that
    NEVER appears in AVAILABLE ELEMENTS at all, since that list only tracks
    interactive elements (buttons/links/inputs/etc). Do NOT return no_match
    just because the expected value isn't visible in AVAILABLE ELEMENTS — as
    long as the step has a concrete expected value, emit assert_text with
    your best-effort selector (a specific container if you can identify one,
    otherwise selector: "//body" is an acceptable default). assert_text
    itself now does a full-page visible-text search as a fallback if your
    selector guess doesn't directly contain the expected text, so it does not
    need to be exact. Reserve no_match for when there is genuinely no
    concrete expected value to check, not for "I don't see it in the element
    list."

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

# Ordinal words -> 0-based position (English + Indonesian). -1 means "last",
# resolved against sibling_group_size at score time since it's a negative
# index into the group, not a literal position.
_ORDINAL_WORDS = {
    'first': 0, 'pertama': 0, 'satu': 0, '1st': 0,
    'second': 1, 'kedua': 1, '2nd': 1,
    'third': 2, 'ketiga': 2, '3rd': 2,
    'last': -1, 'terakhir': -1,
}


def _ordinal_index_from_step(step_description: str) -> Optional[int]:
    """Pull an ordinal position out of a step description, e.g. "Click the
    first product that appears" -> 0, "klik produk pertama" -> 0, "click the
    last item" -> -1. Returns None if no ordinal word is present — most
    steps aren't positional and shouldn't get the structural bypass below."""
    for word in re.split(r'[^a-zA-Z0-9]+', step_description.lower()):
        if word in _ORDINAL_WORDS:
            return _ORDINAL_WORDS[word]
    return None


def _relevance_score(step_description: str, el: dict, last_combobox_controls: str = None) -> int:
    step_tokens = set(re.split(r'[^a-zA-Z0-9]+', step_description.lower()))
    step_tokens.discard('')

    score = 0
    for field in ('text', 'aria_label', 'placeholder', 'id', 'name', 'title'):
        val = el.get(field) or ''
        el_tokens = set(re.split(r'[^a-zA-Z0-9]+', val.lower()))
        el_tokens.discard('')
        score += len(step_tokens & el_tokens)

    # Token-set overlap misses compound-word vs multi-word mismatches — e.g.
    # step says "login" (one word) but the button's actual label is "Log In"
    # (tokenizes to {"log", "in"}), so neither token equals "login" and
    # overlap is 0 even though it's obviously the right element. Found via a
    # real TC_003 regression: "Click the login button" scored 0 against the
    # "Log In" button once the click-verb bonus below was gated on score > 0,
    # so a step that always worked got refused. Catch this by also comparing
    # flattened (spaces/punctuation stripped) forms: if the element's own
    # text/aria-label/title, flattened, appears as a contiguous substring of
    # the flattened step description, that's a strong signal on its own —
    # length-gated at 4 chars so short fields like "ok"/"id" don't trigger
    # coincidental matches.
    step_flat = re.sub(r'[^a-z0-9]', '', step_description.lower())
    for field in ('text', 'aria_label', 'title'):
        val_flat = re.sub(r'[^a-z0-9]', '', (el.get(field) or '').lower())
        if len(val_flat) >= 4 and val_flat in step_flat:
            score += 2
            break

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

    # Widget-instance disambiguation: a page can host several independent
    # Select/combobox widgets (e.g. a component-library docs page stacking
    # multiple demos). An option's text alone can coincidentally match a value
    # already displayed by a DIFFERENT, closed widget elsewhere on the page —
    # e.g. one demo's trigger already shows "Banana" as its committed value
    # while we're actually trying to pick "Banana" from a DIFFERENT, currently
    # OPEN listbox. last_combobox_controls is the aria-controls id of the
    # trigger most recently clicked open in THIS session — an option whose
    # owning_popup_id matches it is confirmed to be in the popup we actually
    # just opened; an option belonging to a different popup is very likely the
    # wrong instance, even though its bare text matched.
    if last_combobox_controls and el.get('role') == 'option':
        owning = el.get('owning_popup_id') or ''
        if owning and owning == last_combobox_controls:
            score += 5
        elif owning and owning != last_combobox_controls:
            score -= 10

    # Ordinal/positional instructions ("click the first product that
    # appears" / "klik produk pertama") have no keyword to overlap with —
    # the target's own text (a product name, price, etc.) shares zero tokens
    # with a generic instruction like that BY DESIGN. Every score source
    # above requires some kind of text/label match, so this class of step
    # always scored 0 and got hard-refused by cmd_click_by_index even when
    # the right element was picked (tools.py). Confirm it structurally
    # instead: if the step names a position and this element sits at that
    # exact position within a real repeated group (sibling_group_size >= 3 —
    # set in tools.py's get_interactable_elements scraper), that's as valid
    # an identity signal as matching text is for named targets. Gated on a
    # real group size so two unrelated same-tag elements elsewhere on the
    # page (nav buttons, etc.) can't accidentally satisfy "first".
    ordinal = _ordinal_index_from_step(step_description)
    group_size = el.get('sibling_group_size') or 0
    if ordinal is not None and group_size >= 3:
        group_index = el.get('sibling_group_index')
        target_index = ordinal if ordinal >= 0 else group_size + ordinal
        if group_index is not None and group_index == target_index:
            score += 6

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

    system_prompt = _get_system_prompt()
    sections = [
        system_prompt,
        f"SESSION ID: {session_id}",
        f"AVAILABLE ELEMENTS ({len(elements)} total, showing {len(top)}):\n{el_str}",
    ]
    if test_data:
        sections.append(f"TEST DATA:\n{json.dumps(test_data)}")
    sections.append(f'STEP: "{step_description}"')

    prompt = "\n\n".join(sections)

    # DEBUG — mirrors n8n console.log in "build prompt" node
    print("=== PROMPT DEBUG ===")
    print(f"system_prompt chars: {len(system_prompt)}")
    print(f"elements str chars: {len(el_str)}")
    print(f"total prompt chars: {len(prompt)}")
    print("====================")

    return prompt
