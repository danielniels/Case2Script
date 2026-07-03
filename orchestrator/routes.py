"""
POST /runs               Start a run
GET  /runs               List runs (from DB — persists across restarts)
GET  /runs/{id}          Run status JSON (memory first, then DB fallback)
GET  /runs/{id}/steps    Step list from DB (for history view)
GET  /runs/{id}/events   SSE live progress
POST /runs/{id}/stop     Stop a run
POST /runs/replay        Replay a saved script
"""

import asyncio
import uuid

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from db import db_delete_run, db_insert_run, db_get_run, db_get_steps, db_list_runs
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
    input_mode: Optional[str] = None
    input_content: Optional[str] = None


class ReplayRequest(BaseModel):
    suite_id: str
    test_case_id: str
    test_case_name: Optional[str] = ""
    session_id: Optional[str] = None
    script_path: Optional[str] = None


@router.post("")
async def start_run(req: RunRequest, request: Request):
    """Start a new run. Returns run_id immediately; run proceeds in background."""
    registry: RunRegistry = request.app.state.runs

    session_id = req.session_id or str(uuid.uuid4())[:8]
    total_steps = len(req.steps)
    state: RunState = registry.new_run(
        req.suite_id, req.test_case_id, total_steps, req.test_case_name or "", session_id
    )

    # Persist to DB immediately so history is available even if server restarts mid-run
    db = getattr(request.app.state, "db", None)
    if db:
        await db_insert_run(
            db,
            run_id=state.run_id,
            suite_id=req.suite_id,
            test_case_id=req.test_case_id,
            test_case_name=req.test_case_name or "",
            total_steps=total_steps,
            started_at=state.started_at,
            input_mode=req.input_mode,
            input_content=req.input_content,
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
        raise HTTPException(status_code=422, detail=f"Cannot parse script file: {script_file}")
    if not steps:
        raise HTTPException(status_code=422, detail="Script has no steps to replay")

    session_id  = req.session_id or str(uuid.uuid4())[:8]
    total_steps = len(steps)

    state: RunState = registry.new_run(
        req.suite_id, req.test_case_id, total_steps, req.test_case_name or "", session_id
    )

    db = getattr(request.app.state, "db", None)
    if db:
        await db_insert_run(
            db,
            run_id=state.run_id,
            suite_id=req.suite_id,
            test_case_id=req.test_case_id,
            test_case_name=req.test_case_name or "",
            total_steps=total_steps,
            started_at=state.started_at,
        )

    task = asyncio.create_task(replay_test_case(state, steps, session_id, request))
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
    """Return run history from DB (survives server restarts)."""
    db = getattr(request.app.state, "db", None)
    if db:
        rows = await db_list_runs(db)
        return {"runs": rows}
    # Fallback to in-memory if DB not available
    registry: RunRegistry = request.app.state.runs
    return {"runs": registry.list_recent()}


@router.get("/{run_id}/steps")
async def get_run_steps(run_id: str, request: Request):
    """Return persisted step list for a completed run (used by history view)."""
    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=503, detail="DB not available")
    steps = await db_get_steps(db, run_id)
    return {"steps": steps}


@router.get("/{run_id}")
async def get_run(run_id: str, request: Request):
    """Return run status. Checks in-memory first (live runs), then DB (history)."""
    registry: RunRegistry = request.app.state.runs
    state = registry.get(run_id)
    if state:
        return _run_summary(state)

    # Fallback to DB for completed/historical runs
    db = getattr(request.app.state, "db", None)
    if db:
        row = await db_get_run(db, run_id)
        if row:
            return row

    raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")


@router.get("/{run_id}/events")
async def run_events(run_id: str, request: Request):
    """SSE stream of step events for a live run."""
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
    state = registry.get(run_id)
    stopped = registry.stop(run_id)
    if not stopped:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found or not running")
    if state and state.session_id:
        sessions = request.app.state.sessions
        await sessions.close(state.session_id)
    return {"run_id": run_id, "status": "stopped"}


@router.delete("/{run_id}")
async def delete_run(run_id: str, request: Request):
    """Delete a run and its steps from DB. Cannot delete a run that is still running."""
    registry: RunRegistry = request.app.state.runs
    state = registry.get(run_id)
    if state and state.status == "running":
        raise HTTPException(status_code=409, detail="Cannot delete a run that is still running. Stop it first.")

    db = getattr(request.app.state, "db", None)
    if not db:
        raise HTTPException(status_code=503, detail="DB not available")

    deleted = await db_delete_run(db, run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")

    # Also evict from in-memory registry if present
    if state:
        registry._runs.pop(run_id, None)

    return {"run_id": run_id, "deleted": True}
