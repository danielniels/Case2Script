"""
Command dispatch, execute_step (extracted), get_session, capture_step_screenshot.
Orchestrator imports execute_step from here to avoid circular imports with mcp_server.
Depends on: helpers.py, stores.py, tools.py
"""

import asyncio
import inspect
import re
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional, cast

from fastapi import Request

from helpers import (
    _fix_selector,
    clean_excel_formula,
    generate_expected_result,
    is_absolute_http_url,
    log,
    screenshot_to_base64,
    smart_fix_llm_output,
)
from stores import (
    ReportStore,
    ScriptStore,
    Session,
    finalize_test_report,
)
from tools import CMD_MAP, VALID_METHODS


# ==================== Session Helper ====================

async def get_session(request: Request, session_id: str) -> Session:
    return await request.app.state.sessions.get_or_create(
        session_id, request.app.state.pw
    )


# ==================== Screenshot Helper ====================

async def capture_step_screenshot(session_id: str, test_case_id: str,
                                   step_index: int, run_timestamp: str,
                                   run_number: int, session: Session) -> str:
    clean_tc = test_case_id.replace(" ", "_").replace("=", "")
    folder = f"{clean_tc}_{run_timestamp}_run_{run_number}"
    screenshot_dir = Path("data/saved_screenshots") / folder
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    filepath = screenshot_dir / f"step_{step_index}.png"
    async with session.lock:
        await session.page.screenshot(path=str(filepath), full_page=False)
    log(session_id, f"Screenshot saved: {filepath}")
    return str(filepath)


# ==================== Command Dispatcher ====================

async def dispatch(method: str, params: dict, session: Session, request: Request) -> dict:
    handler = CMD_MAP.get(method)
    if not handler:
        raise Exception(f"Unknown method: {method}")
    sig = inspect.signature(handler)
    fn = cast(Callable[..., Awaitable[dict]], handler)
    if "request" in sig.parameters:
        result = await fn(params, session, request)
    else:
        result = await fn(params, session)
    session.touch()
    return result


# ==================== Execute Step ====================

async def execute_step(body: dict, request: Request) -> dict:
    """
    Execute a single LLM-resolved step: dispatch → screenshot → record report.
    Extracted from _handle_execute so the orchestrator can import it directly
    without pulling in the FastAPI app/lifespan.
    """
    reports: ReportStore = request.app.state.reports
    scripts: ScriptStore = request.app.state.scripts

    sid = str(body.get("sessionId", "")).strip()
    method = str(body.get("method", "")).strip()
    params = dict(body.get("params") or {})
    test_case_id = clean_excel_formula(str(body.get("test_case_id") or ""))
    test_case_name = body.get("test_case_name")
    test_suite_id = clean_excel_formula(str(body.get("test_suite_id") or ""))

    _raw_si = body.get("step_index")
    _raw_ts = body.get("total_steps")
    try:
        step_index = int(_raw_si) if _raw_si is not None else None
    except (ValueError, TypeError):
        step_index = None
    try:
        total_steps = int(_raw_ts) if _raw_ts is not None else None
    except (ValueError, TypeError):
        total_steps = None

    test_step_id = clean_excel_formula(str(body.get("test_step_id") or ""))
    test_step_description = clean_excel_formula(str(body.get("test_step_description") or ""))
    expected_result = clean_excel_formula(str(body.get("expected_result") or ""))
    final_attempt = bool(body.get("final_attempt", True))
    step_desc = test_step_description or f"Step {step_index}"

    try:
        log(sid, f"=== EXECUTE {step_index}/{total_steps or '?'}: {step_desc} ===")
        log(sid, f"Received method from LLM: {method}")

        session = await get_session(request, sid)

        if not method or method not in VALID_METHODS:
            return {
                "ok": False,
                "error": f"Invalid method '{method}'. Valid methods: {VALID_METHODS}",
                "meta": {
                    "test_suite_id": test_suite_id,
                    "test_case_id": test_case_id,
                    "step_index": step_index,
                    "test_step_id": test_step_id,
                },
            }

        params["sessionId"] = sid

        # ── JS inject override [JS:...] ──
        _js_match = re.search(r'\[JS:(.+)\]', step_desc.strip(), re.DOTALL)
        if _js_match:
            method = "execute_js"
            params = {"script": _js_match.group(1).strip(), "sessionId": sid}
            log(sid, f"[JS OVERRIDE] execute_js → {params['script'][:80]}")

        # ── VALID: prefix → assert_text ──
        _valid_match = re.match(r'^VALID:\s*(.+)', step_desc.strip(), re.IGNORECASE)
        if _valid_match:
            _vtext = _valid_match.group(1).strip()
            if "→" in _vtext:
                expected_text = _vtext.split("→", 1)[1].strip()
            elif "->" in _vtext:
                expected_text = _vtext.split("->", 1)[1].strip()
            else:
                expected_text = _vtext
            method = "assert_text"
            params = {"selector": "//body", "expected": expected_text, "sessionId": sid}
            log(sid, f"[VALID: OVERRIDE] assert_text → {expected_text[:80]}")

        # ── Exact step-description overrides ──
        _STEP_METHOD_OVERRIDES = {
            "close_session": "close_session",
            "close session": "close_session",
            "tutup session": "close_session",
            "screenshot": "screenshot",
            "crawl": "get_page_content_and_save_csv",
        }
        _step_desc_lower = step_desc.strip().lower()
        if _step_desc_lower in _STEP_METHOD_OVERRIDES:
            method = _STEP_METHOD_OVERRIDES[_step_desc_lower]
            params = {"sessionId": sid}
            log(sid, f"[OVERRIDE] Step '{step_desc}' forced method → '{method}'")

        # ── Toast-capture override: force capture_toast=True for known toast-producing clicks ──
        # Purpose: eliminate the gap between click and toast detection by arming the
        # toast-capture JS (_ARM_JS/_RACE_JS in tools.py) INSIDE cmd_click itself,
        # rather than relying on a separate step that may run after the toast has
        # already auto-dismissed.
        _TOAST_CAPTURE_TRIGGERS = (
            "login button",
            "submit",
            "simpan",
            "save",
            "delete",
            "hapus",
            "create",
            "tambah",
            "push to isgs",
            "approve",
            "reject",
        )
        if method == "click" and any(trigger in _step_desc_lower for trigger in _TOAST_CAPTURE_TRIGGERS):
            params["capture_toast"] = True
            params["require_toast"] = False   # don't fail the step if no toast appears — best-effort capture, not assertion
            params["fail_on_error"] = False    # same reasoning — capture only, not validation
            log(sid, f"[TOAST CAPTURE] Step '{step_desc}' → arming toast capture before click")

        # ── smart_fix rules ──
        mcp_json = smart_fix_llm_output({"method": method, "params": params}, step_desc)
        method = mcp_json.get("method", method)
        params = mcp_json.get("params", params)
        params["sessionId"] = sid
        log(sid, f"[EXECUTE] Final params before execution: {params}")

        # ── Guardrail: navigate URL ──
        _PLACEHOLDER_DOMAINS = {"example.com", "example.org", "example.net", "localhost", "placeholder.com"}
        if method == "navigate":
            url = str(params.get("url", "")).strip()
            log(sid, f"[NAVIGATE] URL received: '{url}'")
            _url_host = re.search(r'https?://([^/\s"\'<>]+)', url)
            _is_placeholder = _url_host and any(
                _url_host.group(1).rstrip("/") == d or _url_host.group(1).rstrip("/").endswith("." + d)
                for d in _PLACEHOLDER_DOMAINS
            )
            if _is_placeholder:
                log(sid, f"[NAVIGATE] Placeholder URL detected: '{url}', falling back to get_page_info")
                method = "get_page_info"
                params = {"sessionId": sid}
            elif not is_absolute_http_url(url):
                def _ext_url(s):
                    if not s:
                        return None
                    m = re.search(r'https?://[^\s"\'<>]+', s)
                    return m.group(0) if m else None
                extracted = _ext_url(url) or _ext_url(step_desc)
                if extracted:
                    log(sid, f"[NAVIGATE] Extracted URL: '{extracted}'")
                    params["url"] = extracted
                else:
                    log(sid, f"[NAVIGATE] No valid URL in '{url}', falling back to get_page_info")
                    method = "get_page_info"
                    params = {"sessionId": sid}

        # ── Guardrail: selector normalization ──
        if method in ("click", "fill", "hover", "get_text", "get_all_text", "wait_for_selector"):
            sel = str(params.get("selector", "")).strip()
            if not sel:
                log(sid, f"[GUARDRAIL] method='{method}' has no selector")
                return {
                    "ok": False,
                    "error": f"method '{method}' requires a selector but none was provided.",
                    "meta": {
                        "test_suite_id": test_suite_id,
                        "test_case_id": test_case_id,
                        "step_index": step_index,
                        "test_step_id": test_step_id,
                    },
                }
            else:
                params["selector"] = _fix_selector(sel)

        # ── Record command ──
        command_record = {"jsonrpc": "2.0", "method": method, "params": params, "id": step_index or 1}
        session.command_history.append(command_record)
        if test_case_id:
            await reports.append_command(test_case_id, command_record)

        # ── Init report + script once per run (idempotent guard) ──
        # Condition: report not yet created OR script path not yet set.
        # Using report presence rather than step_index==1 so that replay runners
        # can call execute_step twice for the same step (initial + healed retry)
        # without triggering a re-init that would wipe in-progress data.
        _report_not_inited = test_case_id and (await reports.get_report(test_case_id)) is None
        _script_not_inited = test_case_id and (await scripts.get_script_path(test_case_id)) is None
        if test_case_id and (_report_not_inited or _script_not_inited):
            await reports.init_report(test_case_id, test_case_name, test_suite_id)
            run_ts_init = await reports.get_run_timestamp(test_case_id)
            await scripts.init_script(test_case_id, run_ts_init, sid)
            log(sid, f"[SCRIPT] Initialized for test_case_id={test_case_id!r} at step {step_index}")

        # ── Execute ──
        screenshot_path = None
        status = "passed"
        failure_reason = None

        try:
            executed = await dispatch(method, params, session, request)

            if isinstance(executed, dict) and executed.get("error"):
                raise RuntimeError(executed["error"])

            if test_case_id and step_index:
                try:
                    run_ts = await reports.get_run_timestamp(test_case_id)
                    rpt = await reports.get_report(test_case_id)
                    run_num = (rpt or {}).get("run_number", 1)
                    screenshot_path = await capture_step_screenshot(
                        sid, test_case_id, step_index, run_ts, run_num, session)
                except Exception as ss_err:
                    log(sid, f"[WARNING] Screenshot failed: {ss_err}")

            if test_case_id:
                await reports.add_step(test_case_id, {
                    "file": screenshot_to_base64(screenshot_path),
                    "test_step_id": test_step_id,
                    "test_step_number": step_index,
                    "test_step_description": step_desc,
                    "expected_result": generate_expected_result(method, params, step_desc, expected_result),
                    "status": "Passed",
                    "description": "pass",
                })

            log(sid, f"SUCCESS: Execute step {step_index} completed ({method})")

            if test_case_id and step_index:
                script_params = {k: v for k, v in params.items()}
                if isinstance(executed, dict) and executed.get("resolved_selector"):
                    script_params["resolved_selector"] = executed["resolved_selector"]
                await scripts.append_step(test_case_id, method, script_params, step_desc, step_index, status="passed")

            report_path = None
            script_path = None
            py_script_path = None
            _is_last_step = (
                (test_case_id and step_index and total_steps and step_index >= total_steps)
                or (test_case_id and method == "close_session")
            )
            if _is_last_step:
                finalized = await finalize_test_report(test_case_id, reports)
                report_path = finalized.get("report_path")
                script_path = await scripts.get_script_path(test_case_id)
                await scripts.finalize_script(test_case_id)
                py_script_path = await scripts.get_py_script_path(test_case_id)
                failed_steps = await scripts.get_failed_steps(test_case_id)
                log(sid, f"[REPORT SAVED] {report_path}")
                log(sid, f"[SCRIPT SAVED] {script_path}")
                if py_script_path:
                    log(sid, f"[PY SCRIPT] {py_script_path}")
                if not failed_steps:
                    log(sid, "  ✔  ALL STEPS PASSED")
                await request.app.state.sessions.close(sid)

            return {
                "ok": True,
                "status": status,
                "screenshot_path": screenshot_path,
                "llm_command": {"method": method, "params": params},
                "executed": executed,
                "meta": {
                    "test_suite_id": test_suite_id,
                    "test_case_id": test_case_id,
                    "step_index": step_index,
                    "test_step_id": test_step_id,
                    "report_path": report_path,
                    "script_path": script_path,
                    "py_script_path": py_script_path,
                },
            }

        except Exception as e:
            status = "failed"
            error_message = str(e)
            log(sid, f"Execute step execution failed: {error_message[:200]}")
            failure_reason = f"Step failed: {error_message}"

            if final_attempt:
                if test_case_id and step_index:
                    try:
                        run_ts = await reports.get_run_timestamp(test_case_id)
                        rpt = await reports.get_report(test_case_id)
                        run_num = (rpt or {}).get("run_number", 1)
                        screenshot_path = await capture_step_screenshot(
                            sid, test_case_id, step_index, run_ts, run_num, session)
                    except Exception as ss_err:
                        log(sid, f"[WARNING] Screenshot failed: {ss_err}")

                if test_case_id:
                    await reports.add_step(test_case_id, {
                        "file": screenshot_to_base64(screenshot_path),
                        "test_step_id": test_step_id,
                        "test_step_number": step_index,
                        "test_step_description": step_desc,
                        "expected_result": generate_expected_result(method, params, step_desc, expected_result),
                        "status": "Failed",
                        "description": failure_reason or error_message,
                    })

                if test_case_id and step_index:
                    await scripts.append_step(test_case_id, method, dict(params), step_desc, step_index, status="failed")

                report_path = None
                script_path = None
                py_script_path = None
                _is_last_step_fail = (
                    (test_case_id and step_index and total_steps and step_index >= total_steps)
                    or (test_case_id and method == "close_session")
                )
                if _is_last_step_fail:
                    finalized = await finalize_test_report(test_case_id, reports)
                    report_path = finalized.get("report_path")
                    script_path = await scripts.get_script_path(test_case_id)
                    await scripts.finalize_script(test_case_id)
                    py_script_path = await scripts.get_py_script_path(test_case_id)
                    log(sid, f"[REPORT SAVED] {report_path}")
                    log(sid, f"[SCRIPT SAVED] {script_path}")
                    if py_script_path:
                        log(sid, f"[PY SCRIPT] {py_script_path}")
                    await request.app.state.sessions.close(sid)
            else:
                report_path = None
                script_path = None
                py_script_path = None

            log(sid, f"FAILED: {type(e).__name__}: {error_message[:200]}")
            return {
                "ok": False,
                "status": status,
                "error": error_message,
                "error_type": type(e).__name__,
                "failure_reason": failure_reason,
                "screenshot_path": screenshot_path,
                "llm_command": {"method": method, "params": params},
                "meta": {
                    "test_suite_id": test_suite_id,
                    "test_case_id": test_case_id,
                    "step_index": step_index,
                    "test_step_id": test_step_id,
                    "report_path": report_path,
                    "script_path": script_path,
                    "py_script_path": py_script_path,
                },
            }

    except Exception as e:
        log(sid, f"[EXECUTE] OUTER ERROR: {type(e).__name__}: {str(e)[:200]}")
        return {
            "ok": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "meta": {
                "test_suite_id": test_suite_id,
                "test_case_id": test_case_id,
                "step_index": step_index,
                "test_step_id": test_step_id,
            },
        }
