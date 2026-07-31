"""
mcp_protocol.py
================
Real MCP (Model Context Protocol) surface for Case2Script, built on the
official `fastmcp` framework (https://gofastmcp.com) — separate from the
legacy `/mcp` JSON-RPC-lite endpoint in mcp_server.py.

Why this exists: the old `/mcp` endpoint (see mcp_server.py::_handle_jsonrpc)
borrows JSON-RPC vocabulary (jsonrpc/method/params/id) but never implements
the actual MCP handshake — no `initialize`, no capability negotiation, no
`tools/list`, no `tools/call`. No real MCP client (Claude Desktop, Claude
Code, any other conforming agent) can talk to it. That endpoint stays
exactly as-is; the internal orchestrator keeps calling engine.dispatch() the
same way it always has. This module is a NEW, additive surface that wraps
the SAME underlying tool logic (TOOL_REGISTRY + CMD_MAP, both untouched)
behind a spec-compliant transport so external MCP clients can actually
connect.

Wiring (see mcp_server.py):
  1. mcp_server.py imports this module AFTER `import tools` / `import
     credentials` — those side-effect imports are what populate
     TOOL_REGISTRY/CMD_MAP in the first place, so this module's
     _register_all_tools() call at import time must run after them.
  2. mcp_server.py's lifespan calls bind(pw, sessions) once, right after
     creating the SessionManager, so the tool wrappers below can resolve
     browser sessions. FastMCP tool functions are plain callables with no
     FastAPI Request available, so the Playwright driver instance and
     SessionManager are handed in directly instead of being reached via
     request.app.state (which is what engine.get_session() normally uses).
  3. mcp_server.py mounts `mcp_app` at /mcp/v1 AND combines its lifespan
     with the app's own lifespan (`async with mcp_app.lifespan(app):`) —
     FastMCP's Streamable HTTP transport needs its internal session-manager
     task group initialized via that lifespan, or every request 500s with
     "Task group is not initialized." Verified locally against fastmcp
     3.4.4 before wiring this into the real app.

Security — NOT every TOOL_REGISTRY entry is safe to hand to an arbitrary
external MCP client just because it's safe for the internal LLM:
  - `visible_to_llm=False` already flags internal-only tools (execute_js,
    click_at_position, no_match, get_interactable_elements) — reused here
    as the base filter, since those are never appropriate for ANY caller
    outside the engine itself.
  - `_EXTERNAL_MCP_EXCLUDE` below removes tools that ARE fine for the
    internal LLM (same trusted process) but must not be exposed to an
    external caller. Currently just get_credentials, which returns a
    decrypted username/password for whatever credential name is passed —
    handing that to any connected MCP client would leak real login
    credentials for the systems under test. Review this list by hand
    whenever a new tool is added to TOOL_REGISTRY that touches secrets,
    the filesystem, or anything else an external caller shouldn't reach.
"""

import logging
from typing import Any, Optional

from fastmcp import FastMCP
from fastmcp.tools import FunctionTool

from tool_registry import TOOL_REGISTRY
from tools import CMD_MAP

logger = logging.getLogger("mcp_protocol")

mcp = FastMCP("case2script")

# ASGI app mounted by mcp_server.py at /mcp/v1. transport="streamable-http"
# is the current MCP spec transport for a long-running HTTP server (as
# opposed to stdio, which is for a client-spawned local subprocess — wrong
# fit here since Case2Script already runs as a standing uvicorn service).
mcp_app = mcp.http_app(path="/", transport="streamable-http")

# Tools visible to the internal LLM (visible_to_llm=True in TOOL_REGISTRY)
# that must NOT be handed to an arbitrary external MCP client. See the
# "Security" note in the module docstring before removing anything from
# this set.
_EXTERNAL_MCP_EXCLUDE = {
    "get_credentials",  # decrypted username/password — internal-LLM-only
}

_pw = None        # bound Playwright driver instance (set by bind())
_sessions = None  # bound SessionManager instance (set by bind())


def bind(pw, sessions) -> None:
    """Called once from mcp_server.py's lifespan, right after the
    Playwright instance + SessionManager are created, so the tool
    wrappers registered below can resolve/create browser sessions without
    a FastAPI Request. Must run before any external MCP client's
    tools/call reaches this process — the wrapper raises if called too
    early instead of silently failing later with a confusing AttributeError."""
    global _pw, _sessions
    _pw = pw
    _sessions = sessions
    logger.info("[mcp_protocol] bound to shared Playwright driver + SessionManager")


def _make_tool_fn(tool_name: str, handler):
    """Build the async wrapper FastMCP invokes for one TOOL_REGISTRY entry.

    Every CMD_MAP handler is `async def cmd_x(params: dict, session: Session
    [, request: Request])`. External MCP tools/call requests arrive as
    **kwargs matching the tool's inputSchema — which always includes
    sessionId (added in _register_all_tools below, mirroring the same
    "every command requires sessionId" rule tool_registry.py's
    _full_param_doc already documents for the LLM-facing prompt).

    close_session is special-cased: its CMD_MAP handler takes a `request`
    param only to reach request.app.state.sessions.close(...) — since
    _sessions IS that same SessionManager instance here, we can call
    .close() directly instead of fabricating a fake Request object.
    """

    async def _fn(**kwargs) -> Any:
        if _sessions is None or _pw is None:
            raise RuntimeError(
                "mcp_protocol.bind(pw, sessions) has not run yet — the app "
                "lifespan must start before external MCP tool calls can be "
                "served. Check mcp_server.py's lifespan ordering."
            )

        session_id = kwargs.pop("sessionId", None)
        if not session_id:
            raise ValueError("sessionId is required")

        if tool_name == "close_session":
            await _sessions.close(session_id)
            return {"status": "closed"}

        session = await _sessions.get_or_create(session_id, _pw)
        result = await handler(kwargs, session)
        session.touch()
        return result

    _fn.__name__ = f"mcp_tool_{tool_name}"
    return _fn


def _register_all_tools() -> int:
    """Loop TOOL_REGISTRY and register every eligible entry as a real MCP
    tool. Deliberately generated from TOOL_REGISTRY rather than hand-listed
    here — a parallel hand-maintained tool list is exactly the drift class
    tool_registry.verify_registry_matches() already exists to prevent for
    the LLM-facing prompt; this surface reuses the same source of truth
    instead of inventing a second one that can silently fall out of sync."""
    count = 0
    for name, meta in TOOL_REGISTRY.items():
        if not meta.get("visible_to_llm", True):
            continue
        if name in _EXTERNAL_MCP_EXCLUDE:
            continue

        handler = CMD_MAP.get(name)
        if handler is None:
            # Should be unreachable — tool_registry.verify_registry_matches()
            # already guarantees TOOL_REGISTRY and CMD_MAP agree at import
            # time (tools.py calls it right after CMD_MAP is built). Guard
            # anyway rather than silently skip a tool if that invariant is
            # ever violated.
            raise RuntimeError(
                f"mcp_protocol: '{name}' is in TOOL_REGISTRY but missing "
                f"from CMD_MAP — refusing to register a tool that can't "
                f"actually be dispatched."
            )

        schema = dict(meta["inputSchema"])
        props = dict(schema.get("properties", {}))
        props.setdefault("sessionId", {
            "type": "string",
            "description": (
                "Browser session identifier. Reuse the same value across "
                "calls to keep operating on the same browser tab; a new "
                "value starts a fresh browser session."
            ),
        })
        schema["properties"] = props
        required = list(schema.get("required", []))
        if "sessionId" not in required:
            required.append("sessionId")
        schema["required"] = required

        mcp.add_tool(FunctionTool(
            name=name,
            description=meta["description"],
            parameters=schema,
            fn=_make_tool_fn(name, handler),
        ))
        count += 1

    logger.info(
        f"[mcp_protocol] Registered {count} tools on the external MCP "
        f"surface (excluded: {sorted(_EXTERNAL_MCP_EXCLUDE)})"
    )
    return count


_register_all_tools()
