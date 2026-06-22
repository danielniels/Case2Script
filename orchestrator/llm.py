"""
Ollama LLM call + response parser.
Ported verbatim from n8n nodes:
  - "Ollama call"     (HTTP Request node, retryOnFail:true, waitBetweenTries:5000)
  - "Parse LLM JSON"  (Code node)
"""

import asyncio
import json
import os
import re

import httpx

from orchestrator.prompts import build_step_prompt

# ---------------------------------------------------------------------------
# Config — mirrors n8n "Config" node
# ---------------------------------------------------------------------------
_OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://172.16.15.59:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud")
_OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))

# n8n "Ollama call" node: retryOnFail:true, waitBetweenTries:5000 (ms)
_HTTP_RETRY_COUNT = 3
_HTTP_RETRY_WAIT  = 5.0   # seconds


# ---------------------------------------------------------------------------
# call_ollama — port of n8n "Ollama call" HTTP Request node
#
# Endpoint  : POST {ollama_url}/api/chat           ← /api/chat, NOT /api/generate
# Payload   : {model, messages:[{role:"user",content}], stream:false, think:false}
# Response  : reads message.content first (primary for /api/chat),
#             falls back to response / content[0].text / data   (multi-source)
# Retry     : up to 3x with 5 s sleep between attempts         (retryOnFail)
# ---------------------------------------------------------------------------
async def call_ollama(prompt: str) -> str:
    payload = {
        "model":    _OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream":   False,
        "think":    False,
    }
    last_exc: Exception = RuntimeError("never set")
    for attempt in range(1, _HTTP_RETRY_COUNT + 1):
        try:
            async with httpx.AsyncClient(timeout=_OLLAMA_TIMEOUT) as client:
                resp = await client.post(f"{_OLLAMA_URL}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
            # Multi-source raw extraction — verbatim from n8n "Parse LLM JSON":
            #   $json.response ?? $json.message?.content ?? $json.content?.[0]?.text ?? $json.data ?? ""
            raw = (
                data.get("response")
                or (data.get("message") or {}).get("content")
                or ((data.get("content") or [{}])[0] or {}).get("text")
                or data.get("data")
                or ""
            )
            return raw
        except Exception as exc:
            last_exc = exc
            if attempt < _HTTP_RETRY_COUNT:
                print(
                    f"[Ollama] HTTP error (attempt {attempt}/{_HTTP_RETRY_COUNT}): {exc}"
                    f" — retrying in {_HTTP_RETRY_WAIT}s"
                )
                await asyncio.sleep(_HTTP_RETRY_WAIT)
    raise RuntimeError(
        f"Ollama call failed after {_HTTP_RETRY_COUNT} attempts: {last_exc}"
    )


# ---------------------------------------------------------------------------
# parse_llm_response — verbatim port of n8n "Parse LLM JSON" Code node
#
# Returns either:
#   {"_llm_error": True, "_attempt": N, "_raw_response": "...", "method": "noop", "params": {}}
#     when raw is garbage (< 5 chars, error-keyword prefix, or not JSON-shaped after cleanup)
#   {"method": ..., "params": {...}, "_attempt": N}
#     when parse succeeds
# Raises RuntimeError if raw looks like JSON but JSON.parse fails,
#   or if method is still missing after all heuristics.
# ---------------------------------------------------------------------------
_LOOKS_LIKE_ERROR_RE = re.compile(
    r"^(callback|undefined|null|error|TypeError|ReferenceError|SyntaxError)",
    re.IGNORECASE,
)


def parse_llm_response(raw: str, attempt: int = 1) -> dict:
    # ── looksLikeError check (verbatim from n8n) ──
    looks_like_error = (
        not raw
        or len(raw.strip()) < 5
        or bool(_LOOKS_LIKE_ERROR_RE.match(raw.strip()))
    )

    # ── strip <think>...</think> + markdown fences ──
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    looks_like_json = cleaned.startswith("{") or cleaned.startswith("[")

    if looks_like_error or not looks_like_json:
        return {
            "_llm_error":    True,
            "_attempt":      attempt,
            "_raw_response": str(raw)[:200],
            "method":        "noop",
            "params":        {},
        }

    try:
        parsed = json.loads(cleaned)
    except Exception as exc:
        raise RuntimeError(f"LLM returned invalid JSON: {raw[:300]}") from exc

    # ── action → method normalization ──
    if not parsed.get("method") and parsed.get("action"):
        parsed["method"] = parsed["action"]

    # ── guess method from payload shape ──
    if not parsed.get("method"):
        if parsed.get("value") is not None and (
            parsed.get("field") or parsed.get("target") or parsed.get("selector")
        ):
            parsed["method"] = "fill"
        elif parsed.get("url"):
            parsed["method"] = "navigate"
        elif parsed.get("target") or parsed.get("selector") or parsed.get("field"):
            parsed["method"] = "click"

    # ── build params from flat keys if params key is missing ──
    if parsed.get("method") and not parsed.get("params"):
        parsed["params"] = {
            "selector": parsed.get("selector") or parsed.get("target") or parsed.get("field") or "",
            "text":     parsed.get("text") or parsed.get("value") or "",
            "url":      parsed.get("url") or "",
        }

    if not parsed.get("method"):
        raise RuntimeError(f"LLM JSON missing method field. Raw: {raw[:300]}")

    parsed["_attempt"] = attempt
    return parsed


# ---------------------------------------------------------------------------
# heal_selector — targeted selector-only self-healing call
#
# Called by the replay runner when a selector-based step fails.  Unlike
# resolve_step (which re-resolves the full action), this prompt keeps the
# action and intent fixed and asks the LLM only for a corrected selector.
# Ported from MCP/script_runner.py ask_ollama_for_selector() but uses the
# existing async call_ollama() instead of the old synchronous requests.post.
# ---------------------------------------------------------------------------
async def heal_selector(
    failed_selector: str,
    method: str,
    step_description: str,
    elements: list,
) -> "str | None":
    """
    Ask the LLM for a corrected selector only — action and step intent stay fixed.
    Returns a raw selector string (XPath or CSS), or None if the LLM cannot fix it.
    """
    compact = [
        {
            "suggested_selector": el.get("suggested_selector"),
            "aria_label":  el.get("aria_label"),
            "placeholder": el.get("placeholder"),
            "tag":         el.get("tag"),
            "id":          el.get("id"),
            "name":        el.get("name"),
            "text":        (el.get("text") or "")[:80],
            "role":        el.get("role"),
        }
        for el in elements[:60]
    ]

    prompt = f"""/no_think
You are a Playwright automation expert helping with self-healing test scripts.

A test step failed because its selector no longer matches any element on the page.

FAILED STEP:
- Description: {step_description}
- Action: {method}
- Failed selector: {failed_selector}

CURRENT PAGE ELEMENTS (live snapshot):
{json.dumps(compact, indent=2, ensure_ascii=False)}

TASK:
Look at the current page elements and find the best matching element for the step description and action.
Each element has a "suggested_selector" field — prefer using that directly if the element matches.
Return ONLY the corrected XPath or CSS selector. Nothing else. No explanation, no markdown, no code block.
Just the raw selector string, for example: //INPUT[@id='email']
"""

    try:
        raw = await call_ollama(prompt)
    except Exception as exc:
        print(f"[HealSelector] Ollama error: {exc}")
        return None

    if not raw:
        return None

    # Strip <think> blocks and markdown fences
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"^```[a-z]*\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    if not raw:
        return None

    # Must look like an XPath or CSS selector
    if (
        raw.startswith("//")
        or raw.startswith("(//")
        or raw.startswith("xpath=")
        or raw.startswith("css=")
        or re.match(r'^[A-Z]+\[', raw)
    ):
        return raw

    # Try to extract an XPath if the LLM returned extra text
    m = re.search(r'((?:xpath=|css=)?//[^\s\n"\']+)', raw)
    if m:
        return m.group(1)

    return None


# ---------------------------------------------------------------------------
# resolve_step — convenience wrapper: prompt → call → parse
# Signature matches n8n data flow: step, sessionId, elements, test_data
# ---------------------------------------------------------------------------
async def resolve_step(
    step_description: str,
    session_id: str,
    elements: list,
    test_data: dict = None,
    attempt: int = 1,
) -> dict:
    prompt = build_step_prompt(step_description, session_id, elements, test_data)
    raw = await call_ollama(prompt)
    return parse_llm_response(raw, attempt)
