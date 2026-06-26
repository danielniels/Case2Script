"""
In-memory run registry + SSE event queue.
Each run has a status, a list of step events, and an asyncio.Queue for SSE streaming.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class RunState:
    def __init__(self, run_id: str, suite_id: str, test_case_id: str,
                 total_steps: int, test_case_name: str = "", session_id: str = ""):
        self.run_id = run_id
        self.suite_id = suite_id
        self.test_case_id = test_case_id
        self.test_case_name = test_case_name
        self.session_id = session_id
        self.total_steps = total_steps
        self.status = "running"      # running | passed | failed | stopped
        self.current_step = 0
        self.events: List[dict] = []
        self._queue: asyncio.Queue = asyncio.Queue()
        self.started_at = datetime.utcnow().isoformat()
        self.finished_at: Optional[str] = None
        self.report_path: Optional[str] = None
        self.script_path: Optional[str] = None
        self.error: Optional[str] = None
        self._task: Optional[asyncio.Task] = None

    def push_event(self, event: dict):
        self.events.append(event)
        try:
            self._queue.put_nowait(event)
        except asyncio.QueueFull:
            pass

    async def sse_stream(self):
        """Async generator yielding SSE-formatted lines."""
        sent = 0
        # First flush already-recorded events
        while sent < len(self.events):
            yield self._format_sse(self.events[sent])
            sent += 1

        # Then stream new events
        while self.status == "running":
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=25)
                yield self._format_sse(event)
                sent += 1
            except asyncio.TimeoutError:
                yield "data: {\"type\": \"heartbeat\"}\n\n"

        # Flush any remaining events after run finishes
        while not self._queue.empty():
            try:
                event = self._queue.get_nowait()
                yield self._format_sse(event)
            except asyncio.QueueEmpty:
                break

        yield self._format_sse({"type": "done", "status": self.status})

    @staticmethod
    def _format_sse(event: dict) -> str:
        import json
        return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


class RunRegistry:
    """Thread-safe in-memory store of all active and recent runs."""

    def __init__(self):
        self._runs: Dict[str, RunState] = {}
        self._lock = asyncio.Lock()

    def new_run(self, suite_id: str, test_case_id: str, total_steps: int,
                test_case_name: str = "", session_id: str = "") -> RunState:
        run_id = str(uuid.uuid4())[:8]
        state = RunState(run_id, suite_id, test_case_id, total_steps, test_case_name, session_id)
        self._runs[run_id] = state
        return state

    def get(self, run_id: str) -> Optional[RunState]:
        return self._runs.get(run_id)

    def list_recent(self, limit: int = 50) -> List[dict]:
        runs = sorted(self._runs.values(), key=lambda r: r.started_at, reverse=True)
        return [_run_summary(r) for r in runs[:limit]]

    def stop(self, run_id: str) -> bool:
        state = self._runs.get(run_id)
        if state and state.status == "running":
            state.status = "stopped"
            state.finished_at = datetime.utcnow().isoformat()
            state.push_event({"type": "stopped", "run_id": run_id})
            if state._task and not state._task.done():
                state._task.cancel()
            return True
        return False


def _run_summary(r: RunState) -> dict:
    return {
        "run_id": r.run_id,
        "suite_id": r.suite_id,
        "test_case_id": r.test_case_id,
        "test_case_name": r.test_case_name,
        "status": r.status,
        "current_step": r.current_step,
        "total_steps": r.total_steps,
        "started_at": r.started_at,
        "finished_at": r.finished_at,
        "report_path": r.report_path,
        "script_path": r.script_path,
        "error": r.error,
    }
