"""
Validate and normalize a JSON test suite upload.
Input: raw dict from user. Output: canonical TestSuite dict.
"""

from typing import List


def normalize_suite(raw: dict) -> dict:
    """
    Accept multiple JSON shapes and normalize to canonical form:
    {
      "id": str,
      "name": str,
      "description": str,
      "test_cases": [
        {
          "test_case_id": str,
          "test_case_name": str,
          "test_suite_id": str,
          "steps": [
            {
              "test_step_id": str,
              "test_step_description": str,
              "expected_result": str,
            }, ...
          ]
        }, ...
      ]
    }
    """
    # Support both flat {"test_cases": [...]} and wrapped {"suite": {...}}
    if "suite" in raw:
        raw = raw["suite"]

    suite_id = raw.get("id") or raw.get("suite_id") or raw.get("test_suite_id") or ""
    suite_name = raw.get("name") or raw.get("suite_name") or raw.get("test_suite_name") or suite_id
    description = raw.get("description") or ""

    test_cases = raw.get("test_cases") or raw.get("cases") or raw.get("tests") or []
    normalized_cases = [_normalize_case(tc, suite_id) for tc in test_cases]

    return {
        "id": suite_id,
        "name": suite_name,
        "description": description,
        "test_cases": normalized_cases,
    }


def _normalize_case(tc: dict, suite_id: str) -> dict:
    tc_id = tc.get("test_case_id") or tc.get("id") or tc.get("case_id") or ""
    tc_name = tc.get("test_case_name") or tc.get("name") or tc_id
    steps = tc.get("steps") or tc.get("test_steps") or []
    return {
        "test_case_id": tc_id,
        "test_case_name": tc_name,
        "test_suite_id": suite_id,
        "steps": [_normalize_step(s, i + 1) for i, s in enumerate(steps)],
    }


def _normalize_step(s: dict, index: int) -> dict:
    return {
        "test_step_id": s.get("test_step_id") or s.get("id") or str(index),
        "test_step_description": s.get("test_step_description") or s.get("description") or s.get("step") or "",
        "expected_result": s.get("expected_result") or s.get("expected") or "",
    }


def validate_suite(data: dict) -> List[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors = []
    if not data.get("id"):
        errors.append("Suite 'id' is required")
    cases = data.get("test_cases", [])
    if not cases:
        errors.append("Suite must have at least one test_case")
    for i, tc in enumerate(cases):
        if not tc.get("test_case_id"):
            errors.append(f"test_cases[{i}]: 'test_case_id' is required")
        steps = tc.get("steps", [])
        if not steps:
            errors.append(f"test_cases[{i}]: must have at least one step")
        for j, s in enumerate(steps):
            if not s.get("test_step_description"):
                errors.append(f"test_cases[{i}].steps[{j}]: 'test_step_description' is required")
    return errors
