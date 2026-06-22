"""
Free-text prompt → TestSuite (1 Ollama call). Draft only — NEVER auto-runs.
"""

import json
import os
import re
import uuid

import httpx

from helpers import coerce_llm_json


_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

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


async def prompt_to_suite(text: str, suite_name: str = "") -> dict:
    """
    Call Ollama with the user's free-text prompt and return a draft TestSuite dict.
    Raises RuntimeError if Ollama is unreachable.
    """
    prompt = f"Create a test suite for the following scenario:\n\n{text}"
    payload = {
        "model": _OLLAMA_MODEL,
        "prompt": prompt,
        "system": _SYSTEM,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 1024},
    }
    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(f"{_OLLAMA_URL}/api/generate", json=payload)
        resp.raise_for_status()
        raw = resp.json().get("response", "")

    suite = coerce_llm_json(raw)
    if not suite or "test_cases" not in suite:
        # Fallback: wrap raw text as a single unnamed step
        suite_id = str(uuid.uuid4())[:8]
        suite = {
            "id": suite_id,
            "name": suite_name or "Generated Suite",
            "description": text[:120],
            "test_cases": [{
                "test_case_id": f"{suite_id}_TC001",
                "test_case_name": "Generated Test Case",
                "test_suite_id": suite_id,
                "steps": [
                    {"test_step_id": "1", "test_step_description": text.strip(), "expected_result": ""}
                ],
            }],
        }

    suite["draft"] = True
    suite.setdefault("id", str(uuid.uuid4())[:8])
    return suite
