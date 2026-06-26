"""
Free-text prompt → TestSuite. Draft only — NEVER auto-runs.

Fast path: if input looks like a numbered list, parse with regex (no LLM, instant).
Slow path: free-form natural language → 1 Ollama call to structure it.
"""

import os
import re
import uuid

import httpx

from helpers import coerce_llm_json


_OLLAMA_URL     = os.getenv("OLLAMA_URL",     "http://localhost:11434")
_OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL",   "llama3.2:3b")
_OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "90"))

_SYSTEM = """You are a test case designer. Given a plain-text description of a software test scenario,
output a JSON test suite in the following format:

{
  "id": "<short_id>",
  "name": "<suite name>",
  "description": "<one-line description>",
  "test_cases": [
    {
      "test_case_id": "<tc_id>",
      "test_case_name": "<name>",
      "test_suite_id": "<suite_id>",
      "steps": [
        {"test_step_id": "1", "test_step_description": "<step>", "expected_result": "<expected>"},
        ...
      ]
    }
  ]
}

Rules:
- Output ONLY the JSON object — no markdown, no explanation.
- Each step must have a clear, actionable description.
- Include at least one assertion step (VALID: <text> or assert_text).
- Use realistic step descriptions for a web UI test (navigate, click, fill, etc.).
"""

# Matches "1. text", "2) text", "10. text" etc.
_NUMBERED_LINE = re.compile(r'^\d+[\.\)]\s+\S')


def _is_numbered_list(text: str) -> bool:
    """Return True if ≥60% of non-empty lines look like numbered list items."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return False
    matched = sum(1 for l in lines if _NUMBERED_LINE.match(l))
    return (matched / len(lines)) >= 0.6


def _parse_numbered_list(text: str, suite_name: str = "") -> dict:
    """Instant regex parse — no LLM needed."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    steps = []
    for line in lines:
        m = re.match(r'^\d+[\.\)]\s+(.+)', line)
        if m:
            steps.append({
                "test_step_id":          str(len(steps) + 1),
                "test_step_description": m.group(1).strip(),
                "expected_result":       "",
            })

    suite_id = str(uuid.uuid4())[:8]
    name     = suite_name or "Imported Steps"
    return {
        "id":          suite_id,
        "name":        name,
        "description": text[:120],
        "test_cases":  [{
            "test_case_id":   f"{suite_id}_TC001",
            "test_case_name": name,
            "test_suite_id":  suite_id,
            "steps":          steps,
        }],
        "draft": True,
    }


async def _ollama_parse(text: str, suite_name: str = "") -> dict:
    """Call Ollama to structure free-form natural language into a test suite."""
    payload = {
        "model":   _OLLAMA_MODEL,
        "prompt":  f"Create a test suite for the following scenario:\n\n{text}",
        "system":  _SYSTEM,
        "stream":  False,
        "options": {"temperature": 0.2, "num_predict": 1024},
    }
    async with httpx.AsyncClient(timeout=_OLLAMA_TIMEOUT) as client:
        resp = await client.post(f"{_OLLAMA_URL}/api/generate", json=payload)
        resp.raise_for_status()
        raw = resp.json().get("response", "")

    suite = coerce_llm_json(raw)
    if not suite or "test_cases" not in suite:
        suite_id = str(uuid.uuid4())[:8]
        suite = {
            "id":          suite_id,
            "name":        suite_name or "Generated Suite",
            "description": text[:120],
            "test_cases":  [{
                "test_case_id":   f"{suite_id}_TC001",
                "test_case_name": "Generated Test Case",
                "test_suite_id":  suite_id,
                "steps":          [{"test_step_id": "1", "test_step_description": text.strip(), "expected_result": ""}],
            }],
        }

    suite["draft"] = True
    suite.setdefault("id", str(uuid.uuid4())[:8])
    return suite


async def prompt_to_suite(text: str, suite_name: str = "") -> dict:
    """
    Convert free-text to a draft TestSuite.
    Fast path (regex) for numbered lists — no Ollama call.
    Slow path (Ollama) for natural language.
    """
    if _is_numbered_list(text):
        return _parse_numbered_list(text, suite_name)
    return await _ollama_parse(text, suite_name)
