"""
POST per-step history to Amethyst (best-effort — never fails the run).
Ported from n8n node "Post to History API - Amethyst" (disabled in n8n, but payload
structure is preserved verbatim here).

n8n node payload fields (from body expression):
  job_name     ← test_case_name
  run_id       ← test_case_id        (NOTE: this is test_case_id, not the orchestrator run_id)
  process_name ← test_step_description
  status       ← ok ? 'Completed' : 'Failed'
  detail       ← snippet || ''       (cleaned page text; pass '' if not available)
  start        ← step_started_at     (ISO string from Prepare Payload node)
  end          ← new Date().toISOString()
  step_index   ← step_index
  total_steps  ← total_steps
  test_step_id ← test_step_id

URL: http://103.107.205.86:3000/api/robot/history  (overrideable via AMETHYST_HISTORY_URL)
"""

import os
from datetime import datetime, timezone

import httpx

_HISTORY_URL = os.getenv(
    "AMETHYST_HISTORY_URL",
    "http://103.107.205.86:3000/api/robot/history",
)


async def post_step_history(
    *,
    job_name: str,
    run_id: str,
    process_name: str,
    ok: bool,
    detail: str = "",
    start: str = "",
    step_index: int = 0,
    total_steps: int = 0,
    test_step_id: str = "",
) -> None:
    """
    Fire-and-forget: POST one step result to Amethyst history endpoint.
    Mirrors the body expression in n8n node "Post to History API - Amethyst".
    Never raises — a failed POST must not abort the run.
    """
    if not _HISTORY_URL:
        return
    payload = {
        "job_name":     job_name,
        "run_id":       run_id,
        "process_name": process_name,
        "status":       "Completed" if ok else "Failed",
        "detail":       detail or "",
        "start":        start or "",
        "end":          datetime.now(timezone.utc).isoformat(),
        "step_index":   step_index,
        "total_steps":  total_steps,
        "test_step_id": test_step_id,
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(_HISTORY_URL, json=payload)
        print(f"[History] step {step_index}/{total_steps} → {payload['status']}")
    except Exception as exc:
        print(f"[History] POST failed (step {step_index}): {exc}")
