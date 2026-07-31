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
  GET  /api/scripts  Read .js or .py script file
  POST /api/scripts  Write .js or .py script file
"""

# Load .env before importing any module that reads env vars
from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import os
import re
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from playwright.async_api import async_playwright
from starlette.middleware.base import BaseHTTPMiddleware

# Force UTF-8 stdout/stderr regardless of the host OS's default console
# codepage. Without this, any log/print containing non-ASCII characters
# (→, ✔, etc — used throughout engine.py/runner.py log messages) crashes
# with UnicodeEncodeError on a default Windows console (cp1252). This must
# run before any other code that might print/log.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass  # stream doesn't support reconfigure (e.g. some redirected/piped cases) — non-fatal

# Import side effects — registers all cmd_* into CMD_MAP via @register_tool
import tools        # noqa: F401
import credentials  # noqa: F401

# Real MCP (Model Context Protocol) surface — must import AFTER tools/
# credentials above, since it reads TOOL_REGISTRY/CMD_MAP at import time to
# build the tool list. See mcp_protocol.py's module docstring for why this
# is separate from the /mcp endpoint below.
import mcp_protocol

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
    from db import init_db
    db_conn = await init_db()
    app.state.db = db_conn

    async with async_playwright() as pw:
        app.state.pw = pw
        sessions = SessionManager()
        sessions.start_reaper()
        app.state.sessions = sessions
        app.state.reports = ReportStore()
        app.state.scripts = ScriptStore()
        from orchestrator.run_state import RunRegistry
        app.state.runs = RunRegistry()

        # Hand the same Playwright driver + SessionManager to the MCP
        # surface — its tool wrappers have no FastAPI Request to pull
        # these from (see mcp_protocol.py::bind docstring).
        mcp_protocol.bind(pw, sessions)

        print("[Lifespan] Playwright + DB started.")
        # FastMCP's Streamable HTTP transport needs its own internal
        # session-manager task group started via this lifespan, or every
        # /mcp/v1 request 500s with "Task group is not initialized."
        # Verified locally (fastmcp 3.4.4) before wiring this in.
        async with mcp_protocol.mcp_app.lifespan(app):
            yield
        await sessions.stop_reaper()

    await db_conn.close()
    print("[Lifespan] Playwright + DB stopped.")


# ==================== App ====================

app = FastAPI(title="Case2Script MCP Server", lifespan=lifespan)


# ==================== API Key Middleware ====================

_MCP_API_KEY = os.getenv("MCP_API_KEY", "")


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # startswith, not ==  — /mcp/v1/* (the new real-MCP surface, mounted
        # as a sub-app) is a different path than the legacy /mcp endpoint,
        # and would otherwise ship with NO auth at all: a bigger hole than
        # the endpoint it's meant to upgrade, since it can drive a real
        # browser. Gate both under the same key until there's a reason to
        # split them.
        guarded = request.url.path == "/mcp" or request.url.path.startswith("/mcp/v1")
        if _MCP_API_KEY and guarded:
            key = request.headers.get("X-API-Key", "")
            if key != _MCP_API_KEY:
                return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=401)
        return await call_next(request)


app.add_middleware(APIKeyMiddleware)


# ==================== Sub-routers ====================

app.include_router(orchestrator_router, prefix="/runs", tags=["orchestrator"])
app.include_router(suites_router, prefix="/suites", tags=["suites"])
app.include_router(converters_router, prefix="/convert", tags=["converters"])

# Real MCP (Model Context Protocol) surface — Streamable HTTP transport,
# spec-compliant (initialize / tools/list / tools/call). Separate from the
# legacy /mcp JSON-RPC-lite endpoint below, which the internal orchestrator
# keeps using unchanged. See mcp_protocol.py's module docstring.
app.mount("/mcp/v1", mcp_protocol.mcp_app)


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

class _ScriptWrite(BaseModel):
    path: str
    content: str


class _ScriptRun(BaseModel):
    path: str


_SCRIPT_RUN_TIMEOUT = int(os.getenv("SCRIPT_RUN_TIMEOUT_SECONDS", "300"))
_SCREENSHOT_STATIC_ROOT = Path("data/saved_playwright_scripts_py/screenshots").resolve()
_DATA_ROOT = Path("data").resolve()


_ALLOWED_SCRIPT_SUFFIXES = {".js", ".py"}

# Directories from which scripts may be served or overwritten.
# Resolved at import time so Path.relative_to() comparisons are reliable.
_SCRIPT_ALLOWED_DIRS = [
    Path("data/saved_playwright_scripts_py").resolve(),
    Path("data/saved_scripts").resolve(),
    Path("saved_playwright_scripts").resolve(),  # legacy MCP-folder output
    Path("saved_scripts").resolve(),             # legacy MCP-folder output
]


def _resolve_safe_script_path(raw: str) -> Optional[Path]:
    """Resolve a client-supplied path and verify it stays within allowed dirs."""
    try:
        p = Path(raw).resolve()
    except Exception:
        return None
    if p.suffix not in _ALLOWED_SCRIPT_SUFFIXES:
        return None
    for allowed in _SCRIPT_ALLOWED_DIRS:
        try:
            p.relative_to(allowed)
            return p
        except ValueError:
            continue
    return None


def _find_latest_py_script(test_case_id: str) -> Optional[Path]:
    """Return the most-recently-modified .py script for test_case_id, or None."""
    script_dir = Path("data/saved_playwright_scripts_py")
    if not script_dir.exists():
        return None
    clean = test_case_id.replace(" ", "_").replace("=", "")
    matches = sorted(
        script_dir.glob(f"{clean}_*.py"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


@app.get("/api/scripts/latest-py")
async def get_latest_py_script(test_case_id: str):
    """Return path + content of the newest generated .py script for a test case."""
    p = _find_latest_py_script(test_case_id)
    if not p:
        raise HTTPException(
            status_code=404,
            detail=f"No .py script found for test_case_id='{test_case_id}'. Run the test first.",
        )
    return {"path": str(p).replace("\\", "/"), "content": p.read_text(encoding="utf-8")}


@app.get("/api/scripts")
async def read_script(path: str):
    p = _resolve_safe_script_path(path)
    if p is None or not p.exists():
        raise HTTPException(status_code=404, detail="Script not found")
    return {"path": str(p).replace("\\", "/"), "content": p.read_text(encoding="utf-8")}


@app.post("/api/scripts")
async def write_script(body: _ScriptWrite):
    p = _resolve_safe_script_path(body.path)
    if p is None:
        raise HTTPException(status_code=403, detail="Path not allowed")
    # Keep a backup of the previous version before overwriting
    if p.exists():
        backup = p.parent / (p.stem + "(backup)" + p.suffix + ".bak")
        p.replace(backup)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body.content, encoding="utf-8")
    return {"saved": True, "path": str(p).replace("\\", "/")}


@app.get("/api/scripts/download")
async def download_script(path: str):
    p = _resolve_safe_script_path(path)
    if p is None or not p.exists():
        raise HTTPException(status_code=404, detail="Script not found")
    media_type = "application/javascript" if p.suffix == ".js" else "text/x-python"
    return FileResponse(str(p), filename=p.name, media_type=media_type)


@app.post("/api/scripts/run")
async def run_script(body: _ScriptRun):
    p = _resolve_safe_script_path(body.path)
    if p is None:
        raise HTTPException(status_code=403, detail="Path not allowed")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Script not found")
    if p.suffix != ".py":
        raise HTTPException(status_code=400, detail="Only .py scripts can be executed")

    screenshot_dir = f"data/saved_playwright_scripts_py/screenshots/{p.stem}"

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(p),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to start subprocess: {exc}")

    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(), timeout=_SCRIPT_RUN_TIMEOUT
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        await proc.wait()
        return {
            "ok": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"[Case2Script] Script exceeded timeout ({_SCRIPT_RUN_TIMEOUT}s) and was killed.",
            "screenshot_dir": screenshot_dir,
            "timed_out": True,
        }

    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": stdout_b.decode("utf-8", errors="replace"),
        "stderr": stderr_b.decode("utf-8", errors="replace"),
        "screenshot_dir": screenshot_dir,
        "timed_out": False,
    }


_STEP_NUM_RE = re.compile(r"step_(\d+)")


def _screenshot_sort_key(f: Path):
    # step_N.png sorts numerically by N; anything else (e.g. FAILED.png) sorts after, alphabetically
    m = _STEP_NUM_RE.search(f.name)
    return (0, int(m.group(1))) if m else (1, f.name)


@app.get("/api/scripts/screenshots")
async def list_script_screenshots(screenshot_dir: str):
    try:
        d = Path(screenshot_dir).resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid directory path")
    try:
        d.relative_to(_SCREENSHOT_STATIC_ROOT)
    except ValueError:
        raise HTTPException(status_code=403, detail="Directory not in allowed path")
    if not d.exists() or not d.is_dir():
        return {"screenshots": []}
    pngs = sorted(d.glob("*.png"), key=_screenshot_sort_key)
    return {
        "screenshots": [
            {
                "name": f.name,
                "url": "/data/" + str(f.relative_to(_DATA_ROOT)).replace("\\", "/"),
            }
            for f in pngs
        ]
    }


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