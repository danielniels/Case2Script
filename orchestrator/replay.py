"""
Deterministic script replay with targeted selector self-healing.

Execution model
───────────────
For each saved step:
  1. Execute directly via execute_step — no LLM.
     first attempt uses final_attempt=False so that a failure on a
     selector-based step does NOT record to the report yet.

  2. If the step fails AND the method uses a selector:
     a. Fetch current live page elements in-process.
     b. Call heal_selector() — asks the LLM for a corrected selector ONLY;
        action and intent stay fixed.
     c. Retry once with the healed selector (or the original selector if the
        LLM returns nothing).  This retry uses final_attempt=True so the
        final outcome (pass or fail) is recorded exactly once per step.

  3. If the method does not use a selector, final_attempt=True is used on
     the first call — no healing path, failure is recorded immediately.

History API: each step posts to post_step_history exactly once, same as the
LLM-driven runner.  The `detail` field carries a HEALED/HEAL_FAILED flag so
run results clearly show which steps did not replay cleanly.
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import Request

from engine import execute_step, get_session
from orchestrator.history import post_step_history
from orchestrator.llm import heal_selector
from orchestrator.run_state import RunState
from orchestrator.runner import (
    _emit_critical_stop,
    _is_critical_failure,
    _prepare_payload,
)

# Methods that carry a selector — self-healing applies to these only.
# Matches the set from the retired MCP/script_runner.py SELECTOR_METHODS.
_SELECTOR_METHODS = frozenset({
    "click", "fill", "hover", "get_text", "get_all_text", "wait_for_selector",
    "scroll_to_element", "double_click", "clear_input",
    "get_attribute", "assert_text", "assert_visible",
})


# ---------------------------------------------------------------------------
# Script loading helpers
# ---------------------------------------------------------------------------

def _find_latest_script(test_case_id: str) -> Optional[Path]:
    """Return the most recently modified saved-script JSON for test_case_id."""
    script_dir = Path("data/saved_scripts")
    if not script_dir.exists():
        return None
    clean = test_case_id.replace(" ", "_").replace("=", "")
    matches = sorted(
        script_dir.glob(f"{clean}_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def _load_replay_steps(path: Path) -> Optional[List[dict]]:
    """
    Read a saved script JSON and return the steps list.
    Accepts both the finalized format {"summary":..., "steps":[...]}
    and the bare list format [...].
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[Replay] Cannot read script file {path}: {exc}")
        return None

    if isinstance(data, dict) and "steps" in data:
        return data["steps"]
    if isinstance(data, list):
        return data

    print(f"[Replay] Unrecognised script format in {path}")
    return None


# ---------------------------------------------------------------------------
# Replay runner
# ---------------------------------------------------------------------------

async def replay_test_case(
    state: RunState,
    steps: List[dict],
    session_id: str,
    request: Request,
) -> None:
    """
    Deterministic replay loop.  Mirrors the structure of run_test_case() in
    orchestrator/runner.py — same RunState events, same history API calls —
    but skips all LLM step-resolution and only calls the LLM for targeted
    selector healing when a step fails.

    Each step in `steps` is a saved JSON-RPC record produced by ScriptStore:
        {"jsonrpc":"2.0", "method":..., "step":..., "params":{...}, "id":N}
    """
    total = len(steps)

    state.push_event({
        "type":        "run_start",
        "replay":      True,
        "total_steps": total,
    })

    try:
        for i, step in enumerate(steps, start=1):
            if state.status == "stopped":
                break

            state.current_step = i
            method    = str(step.get("method") or "").strip()
            step_desc = str(step.get("step") or f"Step {i}").strip()
            step_id   = str(step.get("id", i))
            raw_params = dict(step.get("params") or {})

            # sessionId is a top-level field in execute_step body — remove from params
            params = {k: v for k, v in raw_params.items() if k != "sessionId"}

            state.push_event({
                "type":             "step_start",
                "step_index":       i,
                "total_steps":      total,
                "step_description": step_desc,
                "replay":           True,
            })

            step_started_at = datetime.now(timezone.utc).isoformat()

            # Does this method use a selector?  Healing is only possible when yes.
            is_selector_step = method in _SELECTOR_METHODS and bool(params.get("selector"))

            # ── First attempt ─────────────────────────────────────────────────
            # final_attempt=False for selector steps so that a failure does NOT
            # yet write to the report/script stores (the retry will do that).
            # final_attempt=True for non-selector steps (no retry path; record
            # the outcome — pass or fail — immediately).
            body = _prepare_payload(
                method=method,
                params=params,
                session_id=session_id,
                state=state,
                step_index=i,
                step_id=step_id,
                step_desc=step_desc,
                step_started_at=step_started_at,
                final_attempt=not is_selector_step,
            )
            step_result = await execute_step(body, request)
            ok = step_result.get("ok", False)

            healed_selector: Optional[str] = None
            heal_attempted = False

            # ── Selector self-healing ─────────────────────────────────────────
            if not ok and is_selector_step:
                heal_attempted = True
                original_selector = params.get("selector", "")

                print(f"[Replay] Step {i} failed — attempting selector heal for '{method}'")
                state.push_event({
                    "type":             "heal_attempt",
                    "step_index":       i,
                    "step_description": step_desc,
                    "failed_selector":  original_selector,
                })

                elements: list = []
                try:
                    session = await get_session(request, session_id)
                    from tools import cmd_get_interactable_elements
                    el_resp = await cmd_get_interactable_elements({}, session)
                    elements = el_resp.get("elements", [])
                    print(f"[Replay] Heal: fetched {len(elements)} live element(s)")
                except Exception as exc:
                    print(f"[Replay] Heal: elements fetch failed: {exc}")

                if elements and original_selector:
                    healed_selector = await heal_selector(
                        original_selector, method, step_desc, elements
                    )

                # Retry: use healed selector if available, else rerun original params.
                # Either way this is the final attempt — records pass or fail exactly once.
                retry_params = ({**params, "selector": healed_selector}
                                if healed_selector else params)

                if healed_selector:
                    print(f"[Replay] Heal: retrying with new selector: {healed_selector}")
                else:
                    print(f"[Replay] Heal: LLM returned no selector — recording failure")

                retry_body = _prepare_payload(
                    method=method,
                    params=retry_params,
                    session_id=session_id,
                    state=state,
                    step_index=i,
                    step_id=step_id,
                    step_desc=step_desc,
                    step_started_at=step_started_at,
                    final_attempt=True,
                )
                step_result = await execute_step(retry_body, request)
                ok = step_result.get("ok", False)

                if ok:
                    print(f"[Replay] Step {i} healed successfully")
                else:
                    healed_selector = None  # healing did not help; clear for event metadata
                    print(f"[Replay] Step {i}: heal also failed")

            # ── Emit step_end ─────────────────────────────────────────────────
            _emit_step_end_replay(
                state, step_result, i, step_desc,
                heal_attempted=heal_attempted,
                healed_selector=healed_selector,
                heal_failed=heal_attempted and not ok,
            )

            # ── History API (same call signature as LLM runner) ───────────────
            detail = ""
            if heal_attempted:
                if healed_selector and ok:
                    detail = f"HEALED:{healed_selector}"
                else:
                    detail = "HEAL_FAILED"

            await post_step_history(
                job_name=state.test_case_name,
                run_id=state.test_case_id,
                process_name=step_desc,
                ok=ok,
                detail=detail,
                start=step_started_at,
                step_index=i,
                total_steps=total,
                test_step_id=step_id,
            )

            # ── Critical failure check (mirrors LLM runner) ───────────────────
            if _is_critical_failure(ok, step_desc):
                _emit_critical_stop(state, i, step_desc)
                break

        if state.status not in ("stopped", "failed"):
            state.status = "passed"

    except asyncio.CancelledError:
        state.status = "stopped"
    except Exception as exc:
        state.status = "failed"
        state.error = str(exc)
        state.push_event({"type": "error", "error": str(exc)})
    finally:
        state.finished_at = datetime.now(timezone.utc).isoformat()
        state.push_event({
            "type":        "run_end",
            "status":      state.status,
            "finished_at": state.finished_at,
            "replay":      True,
        })


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _emit_step_end_replay(
    state: RunState,
    result: dict,
    step_index: int,
    step_desc: str,
    heal_attempted: bool = False,
    healed_selector: Optional[str] = None,
    heal_failed: bool = False,
) -> None:
    """
    Like runner._emit_step_end but adds healing metadata.
    A healed step that succeeded carries healed_selector so callers can
    distinguish "clean deterministic pass" from "pass after selector fix".
    """
    ok = result.get("ok", False)
    state.push_event({
        "type":             "step_end",
        "step_index":       step_index,
        "step_description": step_desc,
        "ok":               ok,
        "status":           "passed" if ok else "failed",
        "error":            result.get("error"),
        "screenshot_path":  result.get("screenshot_path"),
        "heal_attempted":   heal_attempted,
        "healed_selector":  healed_selector,
        "heal_failed":      heal_failed,
    })
