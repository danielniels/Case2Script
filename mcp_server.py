"""
Playwright MCP Server
=====================
Run: uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --workers 1
workers=1 required — Playwright browser state lives in-process.

Endpoints:
  POST /mcp          Unified: JSON-RPC OR ExecuteRequest
  POST /submit-report  Submit saved report with JWT token
  GET  /health
  GET  /api/info     API docs
  GET  /runs/*       (mounted from orchestrator)
  GET  /suites/*     (mounted from suites_store)
  POST /convert/*    (mounted from converters)
  GET  /api/scripts  Read .js script file
  POST /api/scripts  Write .js script file
"""

# Load .env before importing any module that reads env vars
from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from playwright.async_api import async_playwright
from starlette.middleware.base import BaseHTTPMiddleware

# Import side effects — registers all cmd_* into CMD_MAP via @register_tool
import tools        # noqa: F401
import credentials  # noqa: F401

from engine import dispatch, execute_step, get_session
from helpers import clean_excel_formula
from stores import (
    ReportStore,
    ScriptStore,
    SessionManager,
    _find_latest_report_file,
    _normalize_timestamp,
    save_test_report,
    submit_report_to_submit_agent,
)
from orchestrator.routes import router as orchestrator_router
from suites_store.routes import router as suites_router
from converters.routes import router as converters_router


# ==================== Models ====================

class SubmitReportRequest(BaseModel):
    test_case_id: str
    token: str
    submit_url: Optional[str] = None


# ==================== Lifespan ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Playwright once per worker; clean up on shutdown."""
    async with async_playwright() as pw:
        app.state.pw = pw
        sessions = SessionManager()
        sessions.start_reaper()
        app.state.sessions = sessions
        app.state.reports = ReportStore()
        app.state.scripts = ScriptStore()
        # run_registry shared with orchestrator
        from orchestrator.run_state import RunRegistry
        app.state.runs = RunRegistry()
        print(f"[Lifespan] Playwright started.")
        yield
        await sessions.stop_reaper()
    print("[Lifespan] Playwright stopped.")


# ==================== App ====================

app = FastAPI(title="Case2Script MCP Server", lifespan=lifespan)


# ==================== API Key Middleware ====================

_MCP_API_KEY = os.getenv("MCP_API_KEY", "")


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if _MCP_API_KEY and request.url.path == "/mcp":
            key = request.headers.get("X-API-Key", "")
            if key != _MCP_API_KEY:
                return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
        return await call_next(request)


app.add_middleware(APIKeyMiddleware)


# ==================== Sub-routers ====================

app.include_router(orchestrator_router, prefix="/runs", tags=["orchestrator"])
app.include_router(suites_router, prefix="/suites", tags=["suites"])
app.include_router(converters_router, prefix="/convert", tags=["converters"])


# ==================== /mcp Endpoint ====================

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "Invalid JSON body"}, status_code=400)

    if "jsonrpc" in body:
        return await _handle_jsonrpc(body, request)
    else:
        return await execute_step(body, request)


async def _handle_jsonrpc(body: dict, request: Request):
    rpc_id = body.get("id", 0)
    method = str(body.get("method", "")).strip()
    params = body.get("params") or {}
    session_id = params.get("sessionId", "default")
    try:
        session = await get_session(request, session_id)
        result = await dispatch(method, params, session, request)
        return {"jsonrpc": "2.0", "result": result, "id": rpc_id}
    except Exception as e:
        return {"jsonrpc": "2.0", "error": {"message": str(e)}, "id": rpc_id}


# ==================== /submit-report Endpoint ====================

@app.post("/submit-report")
async def submit_report_endpoint(req: SubmitReportRequest, request: Request):
    test_case_id = clean_excel_formula(req.test_case_id)
    token = req.token.strip()

    if not token:
        return {"ok": False, "error": "token is required."}

    report_file = _find_latest_report_file(test_case_id)
    if not report_file:
        return {
            "ok": False,
            "error": f"No saved report found for test_case_id='{test_case_id}'. Run the test first.",
        }

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report = json.load(f)
    except Exception as e:
        return {"ok": False, "error": f"Failed to read report file: {e}"}

    print(f"[submit-report] Submitting {report_file} with token")
    submit_result = await submit_report_to_submit_agent(
        report, token=token, submit_url=req.submit_url or ""
    )
    return {
        "ok": submit_result.get("ok", False),
        "test_case_id": test_case_id,
        "report_file": str(report_file),
        "submit_agent": submit_result,
    }


# ==================== Health & Root ====================

@app.get("/health")
async def health_check(request: Request):
    sessions_mgr: SessionManager = request.app.state.sessions
    return {"status": "healthy", "active_sessions": sessions_mgr.active_sessions()}


@app.get("/api/info")
async def root():
    return {
        "message": "Case2Script MCP Server",
        "docs": "/docs",
        "endpoints": {
            "POST /mcp": "JSON-RPC OR ExecuteRequest",
            "POST /runs": "Start orchestrated run",
            "POST /runs/replay": "Deterministic replay of saved script (selector healing on failure)",
            "GET /runs/{id}": "Run status",
            "GET /runs/{id}/events": "SSE live progress",
            "GET /suites": "List test suites",
            "POST /convert/json": "Validate + import JSON suite",
            "POST /convert/excel": "Import Excel suite",
            "POST /convert/prompt": "Generate suite from text prompt",
            "POST /submit-report": "Submit saved report",
            "GET /health": "Health check",
        }
    }


# ==================== Script Read/Write API ====================

from fastapi.responses import FileResponse
from pydantic import BaseModel as _BM

class _ScriptWrite(_BM):
    path: str
    content: str


@app.get("/api/scripts")
async def read_script(path: str):
    p = Path(path)
    if not p.exists() or p.suffix != ".js":
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Script not found")
    return {"path": path, "content": p.read_text(encoding="utf-8")}


@app.post("/api/scripts")
async def write_script(body: _ScriptWrite):
    p = Path(body.path)
    if p.suffix != ".js":
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Only .js scripts can be saved")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body.content, encoding="utf-8")
    return {"saved": True, "path": body.path}


@app.get("/api/scripts/download")
async def download_script(path: str):
    p = Path(path)
    if not p.exists() or p.suffix != ".js":
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Script not found")
    return FileResponse(str(p), filename=p.name, media_type="application/javascript")


# ==================== Serve Static Data Files (screenshots, reports) ====================

_DATA_DIR = Path("data")
if _DATA_DIR.exists():
    app.mount("/data", StaticFiles(directory=str(_DATA_DIR)), name="data")


# ==================== Serve Frontend (LAST — catches all unmatched routes) ====================

_FRONTEND_DIST = Path("frontend/dist")
if _FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")


# ==================== Launcher ====================

if __name__ == "__main__":
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=8000, workers=1)
