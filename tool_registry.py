"""
Single source of truth for tool metadata, shared between tools.py (CMD_MAP /
command dispatch) and orchestrator/prompts.py (the LLM-facing TOOLS listing
inside SYSTEM_PROMPT).

Why this lives in its own file instead of inside tools.py:
tools.py already does `from orchestrator.prompts import _relevance_score`
(see tools.py top-of-file import, which even carries a comment warning about
this). If TOOL_REGISTRY/register_tool lived in tools.py, prompts.py would
need to import them from tools.py to generate its TOOLS section — that's
tools -> prompts -> tools, a circular import. This module has zero
dependencies on either tools.py or prompts.py, so both can import it safely.

The point of this registry: previously the LLM-facing tool list in
prompts.py.SYSTEM_PROMPT was hand-typed English text, kept in sync with
CMD_MAP (the actual dispatcher) by memory/discipline only. That already drifted
in practice — click_by_index was dispatchable and documented in the prompt,
but had no @register_tool entry at all; TOOL_REGISTRY existed but was never
read by anything (dead metadata). This module makes the registry the actual
source the prompt is generated from, and verify_registry_matches() below turns
"forgot to update the other side" into a loud startup failure instead of a
silent "Unknown method" at runtime.
"""

from typing import Any, Callable, Dict, Iterable, Optional

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Category display order for the generated TOOLS table — mirrors the grouping
# that used to be hand-typed in orchestrator/prompts.py SYSTEM_PROMPT
# (action verbs, then verify/assert, then data-extraction, then wait/session).
# One blank line is inserted between non-empty groups.
_CATEGORY_ORDER = ["action", "verify", "extract", "wait_session", "other"]


def register_tool(
    name: str,
    description: str,
    input_schema: Optional[Dict] = None,
    *,
    category: str = "other",
    llm_doc: Optional[str] = None,
    visible_to_llm: bool = True,
):
    """Declarative tool metadata. Additive — does NOT change execution
    (CMD_MAP in tools.py is still what dispatch() actually calls).

    category:       grouping bucket for the generated TOOLS table, see
                     _CATEGORY_ORDER. Ignored when visible_to_llm=False.
    llm_doc:        the params shown to the LLM AFTER "sessionId, " — e.g.
                     "selector (XPath)" renders as "sessionId, selector
                     (XPath)". Every command requires sessionId (see
                     CONSTRAINTS in SYSTEM_PROMPT), so that part is added
                     automatically; pass None (default) for a tool that takes
                     no other params, which renders as "sessionId only". If
                     llm_doc is omitted but the schema has properties, a tail
                     is auto-derived from input_schema (see _auto_param_doc)
                     — less readable, but guarantees a tool registered
                     without a hand-written doc still shows up instead of
                     silently vanishing from the prompt.
    visible_to_llm: False for methods that are dispatchable (must still be
                     in CMD_MAP) but must NOT appear in the LLM's TOOLS menu —
                     e.g. execute_js (excluded per the no-JS-evaluate locator
                     policy; internal escape hatch only), or engine-internal
                     helpers the LLM reaches indirectly rather than by name
                     directly (get_interactable_elements, click_at_position,
                     no_match — the latter is still referenced by name in the
                     DECISION GUIDE prose, just not listed in the TOOLS table).
    """
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
            "category": category,
            "llm_doc": llm_doc,
            "visible_to_llm": visible_to_llm,
        }
        return func
    return decorator


def _auto_param_doc(schema: Dict) -> Optional[str]:
    """Fallback for the params-doc TAIL (everything after 'sessionId, '),
    derived straight from inputSchema when a tool is registered without an
    explicit llm_doc. Returns None if the tool takes no params beyond
    sessionId (caller then renders 'sessionId only'). Uglier than a
    hand-written line, but correct-by-construction — a newly added tool can
    never be missing from the LLM prompt just because nobody wrote the doc
    string yet."""
    props = (schema or {}).get("properties", {}) or {}
    if not props:
        return None
    required = set((schema or {}).get("required", []) or [])
    parts = [p if p in required else f"{p} (optional)" for p in props]
    return ", ".join(parts)


def _full_param_doc(meta: Dict) -> str:
    """Render the full 'params: ...' value for one tool: always 'sessionId'
    first (every command requires it — see the CONSTRAINTS section of
    SYSTEM_PROMPT), then either llm_doc (hand-written) or an auto-derived
    tail, or nothing ('sessionId only')."""
    tail = meta.get("llm_doc")
    if tail is None:
        tail = _auto_param_doc(meta["inputSchema"])
    return f"sessionId, {tail}" if tail else "sessionId only"


def render_tools_table() -> str:
    """Build the LLM-facing TOOLS listing from TOOL_REGISTRY, grouped by
    category in _CATEGORY_ORDER with one blank line between groups — the
    layout that used to be hand-typed in orchestrator/prompts.py. Tools
    registered with visible_to_llm=False are excluded entirely, so the LLM
    never learns their names."""
    groups: Dict[str, list] = {cat: [] for cat in _CATEGORY_ORDER}
    for name, meta in TOOL_REGISTRY.items():
        if not meta.get("visible_to_llm", True):
            continue
        groups.setdefault(meta.get("category", "other"), []).append((name, meta))

    blocks = []
    for cat in _CATEGORY_ORDER:
        entries = groups.get(cat) or []
        if not entries:
            continue
        width = max(len(n) for n, _ in entries)
        lines = [
            f"{name.ljust(width)} | params: {_full_param_doc(meta)}"
            for name, meta in entries
        ]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def verify_registry_matches(cmd_map_keys: Iterable[str]) -> None:
    """Fail loudly at import time if TOOL_REGISTRY and CMD_MAP have drifted
    apart — the exact bug class this registry exists to prevent. Call this
    from tools.py right after CMD_MAP is defined.

    Two failure directions:
    - registered but not dispatchable: the LLM would be told about (or the
      prompt would silently list) a method that dispatch() cannot execute
      -> guaranteed "Unknown method" at runtime the first time it's picked.
    - dispatchable but never registered: someone added a new cmd_* to
      CMD_MAP and forgot @register_tool entirely, so it's neither in the LLM
      prompt nor explicitly marked as intentionally hidden. Could be a genuine
      oversight (should be visible) or should have been visible_to_llm=False —
      either way, it must be a deliberate choice, not a silent gap.
    """
    registered = set(TOOL_REGISTRY.keys())
    dispatchable = set(cmd_map_keys)
    missing_from_cmd_map = registered - dispatchable
    missing_from_registry = dispatchable - registered
    if missing_from_cmd_map:
        raise RuntimeError(
            f"tool_registry: {sorted(missing_from_cmd_map)} are registered via "
            f"@register_tool but have no entry in CMD_MAP — dispatch() cannot "
            f"execute them, so the LLM must not be told they exist."
        )
    if missing_from_registry:
        raise RuntimeError(
            f"tool_registry: {sorted(missing_from_registry)} are in CMD_MAP but "
            f"were never @register_tool-decorated. Add @register_tool(..., "
            f"visible_to_llm=False) if intentionally internal-only, or with a "
            f"category+llm_doc if the LLM should be able to call it."
        )
