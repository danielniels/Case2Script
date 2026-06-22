"""
POST /runs           Start a run
GET  /runs/{id}      Run status JSON
GET  /runs/{id}/events  SSE live progress
POST /runs/{id}/stop Stop a run
"""

import asyncio
import uuid

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from orchestrator.replay import _find_latest_script, _load_replay_steps, replay_test_case
from orchestrator.run_state import RunRegistry, RunState, _run_summary
from orchestrator.runner import run_test_case

router = APIRouter()


class RunRequest(BaseModel):
    suite_id: str
    test_case_id: str
    test_case_name: Optional[str] = ""
    test_data: dict = {}
    steps: List[dict]
    session_id: Optional[str] = None


class ReplayRequest(BaseModel):
    suite_id: str
    test_case_id: str
    test_case_name: Optional[str] = ""
    session_id: Optional[str] = None
    # If omitted, the most recently saved script for test_case_id is used.
    script_path: Optional[str] = None


@router.post("")
async def start_run(req: RunRequest, request: Request):
    """Start a new run. Returns run_id immediately; run proceeds in background."""
    registry: RunRegistry = request.app.state.runs

    session_id = req.session_id or str(uuid.uuid4())[:8]
    total_steps = len(req.steps)
    state: RunState = registry.new_run(
        req.suite_id, req.test_case_id, total_steps, req.test_case_name or ""
    )

    task = asyncio.create_task(
    run_test_case(state, req.steps, session_id, request, req.test_data)
    )
    state._task = task

    return {
        "run_id": state.run_id,
        "status": "running",
        "total_steps": total_steps,
        "session_id": session_id,
    }


@router.post("/replay")
async def start_replay(req: ReplayRequest, request: Request):
    """
    Replay a saved script deterministically.  LLM is only invoked if a
    selector-based step fails (targeted selector healing, not full re-resolve).

    Returns the same shape as POST /runs so the frontend and SSE stream
    (/runs/{run_id}/events) work identically for replay runs.
    """
    registry: RunRegistry = request.app.state.runs

    if req.script_path:
        from pathlib import Path as _Path
        script_file = _Path(req.script_path)
        if not script_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Script file not found: {req.script_path}",
            )
    else:
        script_file = _find_latest_script(req.test_case_id)
        if not script_file:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No saved script found for test_case_id={req.test_case_id!r}. "
                    "Run the test case at least once via POST /runs first."
                ),
            )

    steps = _load_replay_steps(script_file)
    if steps is None:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot parse script file: {script_file}",
        )
    if not steps:
        raise HTTPException(status_code=422, detail="Script has no steps to replay")

    session_id  = req.session_id or str(uuid.uuid4())[:8]
    total_steps = len(steps)

    state: RunState = registry.new_run(
        req.suite_id, req.test_case_id, total_steps, req.test_case_name or ""
    )
    task = asyncio.create_task(
        replay_test_case(state, steps, session_id, request)
    )
    state._task = task

    return {
        "run_id":      state.run_id,
        "status":      "running",
        "total_steps": total_steps,
        "session_id":  session_id,
        "replay":      True,
        "script_path": str(script_file),
    }


@router.get("")
async def list_runs(request: Request):
    registry: RunRegistry = request.app.state.runs
    return {"runs": registry.list_recent()}


@router.get("/{run_id}")
async def get_run(run_id: str, request: Request):
    registry: RunRegistry = request.app.state.runs
    state = registry.get(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")
    return _run_summary(state)


@router.get("/{run_id}/events")
async def run_events(run_id: str, request: Request):
    """SSE stream of step events for a run."""
    registry: RunRegistry = request.app.state.runs
    state = registry.get(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")

    return StreamingResponse(
        state.sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{run_id}/stop")
async def stop_run(run_id: str, request: Request):
    registry: RunRegistry = request.app.state.runs
    stopped = registry.stop(run_id)
    if not stopped:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found or not running")
    return {"run_id": run_id, "status": "stopped"}
