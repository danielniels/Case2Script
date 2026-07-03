"""
Background asyncio run loop — one step at a time with retry.
Replaces n8n sub-workflow: Explode steps → Test Step (loop) →
  Get Browser Interactables → build prompt → Ollama → Parse LLM JSON →
  Prepare Payload → Execute Browser Action → IF Step Success →
    TRUE  → Post History → next step
    FALSE → Check Retry (attempt<3?) → Prep Retry → re-fetch elements (retry)
                                      → no more retries → Post History → next step
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import Request

from db import db_update_run, db_upsert_step
from engine import execute_step, get_session
from orchestrator.history import post_step_history
from orchestrator.llm import OllamaQuotaExceeded, resolve_step
from orchestrator.run_state import RunState
from orchestrator.valid_steps import (
    extract_credential_fill,
    extract_page_assertion,
    extract_toast_assertion,
    extract_upload,
    extract_valid_assertion,
)

_MAX_ATTEMPTS = 3   # n8n: _can_retry = attempt < 3

_CRITICAL_STEP_KEYWORDS = ["login", "log in", "masuk", "submit"]


async def _emit_and_persist(db, state: RunState, result: dict, step_index: int, step_desc: str) -> None:
    """Emit step_end SSE event and persist step to DB."""
    _emit_step_end(state, result, step_index, step_desc)
    if db:
        ok = result.get("ok", False)
        await db_upsert_step(
            db,
            run_id=state.run_id,
            step_index=step_index,
            description=step_desc,
            status="passed" if ok else "failed",
            screenshot_path=result.get("screenshot_path"),
            error=result.get("error"),
        )


async def run_test_case(
    state: RunState,
    steps: List[dict],
    session_id: str,
    request: Request,
    test_data: Optional[dict] = None,
) -> None:
    """
    Run all steps sequentially, each with up to 3 attempts.
    Mirrors n8n "Test Step" SplitInBatches loop + retry graph exactly.

    test_data: case-level credential/value dict (NOT per-step).
               Passed once from the caller (routes.py RunRequest.test_data).
               Do NOT read test_data from individual step dicts.
    """
    test_data = test_data or {}
    db = getattr(request.app.state, "db", None)

    try:
        for i, step in enumerate(steps, start=1):
            if state.status == "stopped":
                break

            state.current_step = i
            step_desc = str(step.get("test_step_description") or f"Step {i}").strip()
            step_id   = step.get("test_step_id", str(i))
            # NOTE: test_data comes from the case level (parameter), NOT from step dict.

            # ── Template variable substitution ───────────────────────────────
            # Replace {{key}} placeholders with values from test_data.
            # Happens before every path (bypass + LLM) so test_data works everywhere.
            if test_data:
                for _td_key, _td_val in test_data.items():
                    step_desc = step_desc.replace(f"{{{{{_td_key}}}}}", str(_td_val))

            state.push_event({
                "type":             "step_start",
                "step_index":       i,
                "total_steps":      state.total_steps,
                "step_description": step_desc,
            })

            # ── Credential-fill bypass — fetch elements, skip LLM ───────────
            # Covers: "Mengisi/Isi Username|Email|Password → <value>"
            # Falls back to LLM if no matching element found on the page.
            cred = extract_credential_fill(step_desc)
            if cred:
                field_type, fill_value = cred
                cred_elements: list = []
                try:
                    cred_session = await get_session(request, session_id)
                    from tools import cmd_get_interactable_elements
                    el_resp = await cmd_get_interactable_elements({}, cred_session)
                    cred_elements = el_resp.get("elements", [])
                except Exception as exc:
                    print(f"[Runner] Credential bypass: elements fetch failed: {exc}")

                cred_selector = _find_credential_selector(cred_elements, field_type)

                if cred_selector:
                    step_started_at = datetime.now(timezone.utc).isoformat()
                    body = _prepare_payload(
                        method="fill",
                        params={"selector": cred_selector, "text": fill_value},
                        session_id=session_id,
                        state=state,
                        step_index=i,
                        step_id=step_id,
                        step_desc=step_desc,
                        step_started_at=step_started_at,
                        final_attempt=True,
                    )
                    result = await execute_step(body, request)
                    await _emit_and_persist(db, state, result, i, step_desc)
                    await post_step_history(
                        job_name=state.test_case_name,
                        run_id=state.test_case_id,
                        process_name=step_desc,
                        ok=result.get("ok", False),
                        detail="",
                        start=step_started_at,
                        step_index=i,
                        total_steps=state.total_steps,
                        test_step_id=step_id,
                    )
                    if _is_critical_failure(result.get("ok", False), step_desc):
                        _emit_critical_stop(state, i, step_desc)
                        break
                    continue
                else:
                    print(f"[Runner] Credential bypass: no '{field_type}' element found, falling back to LLM")
                    # Fall through — other deterministic checks won't match this
                    # step pattern, so execution proceeds directly to LLM path.

            # ── Upload bypass — fetch elements, skip LLM ────────────────────
            # Covers: "Upload <label> → <filename>" / "Unggah <label> → <filename>"
            # Falls back to LLM if no upload target found on the page.
            up = extract_upload(step_desc)
            if up:
                label_hint, filename = up
                up_elements: list = []
                try:
                    up_session = await get_session(request, session_id)
                    from tools import cmd_get_interactable_elements
                    el_resp = await cmd_get_interactable_elements({}, up_session)
                    up_elements = el_resp.get("elements", [])
                except Exception as exc:
                    print(f"[Runner] Upload bypass: elements fetch failed: {exc}")

                up_selector = _find_upload_selector(up_elements, label_hint)
                if up_selector:
                    step_started_at = datetime.now(timezone.utc).isoformat()
                    body = _prepare_payload(
                        method="upload_file",
                        params={"selector": up_selector, "files": filename, "verify_filename": True},
                        session_id=session_id, state=state, step_index=i, step_id=step_id,
                        step_desc=step_desc, step_started_at=step_started_at, final_attempt=True,
                    )
                    result = await execute_step(body, request)
                    await _emit_and_persist(db, state, result, i, step_desc)
                    await post_step_history(
                        job_name=state.test_case_name, run_id=state.test_case_id,
                        process_name=step_desc, ok=result.get("ok", False), detail="",
                        start=step_started_at, step_index=i, total_steps=state.total_steps,
                        test_step_id=step_id,
                    )
                    if _is_critical_failure(result.get("ok", False), step_desc):
                        _emit_critical_stop(state, i, step_desc)
                        break
                    continue
                else:
                    print(f"[Runner] Upload bypass: no upload target for hint '{label_hint}', falling back to LLM")

            # ── Page-assertion bypass — no LLM, direct assert_url ───────────
            # Covers: "Halaman <Name>" / "Menampilkan Halaman <Name>" (no URL in step).
            # Steps with URL (navigate descriptions) are excluded by extract_page_assertion.
            # Page-assertion failure is ALWAYS critical — wrong page means flow is broken.
            page_assert = extract_page_assertion(step_desc)
            if page_assert:
                _, url_keyword = page_assert
                step_started_at = datetime.now(timezone.utc).isoformat()
                body = _prepare_payload(
                    method="assert_url",
                    params={"expected": url_keyword},
                    session_id=session_id,
                    state=state,
                    step_index=i,
                    step_id=step_id,
                    step_desc=step_desc,
                    step_started_at=step_started_at,
                    final_attempt=True,
                )
                result = await execute_step(body, request)
                await _emit_and_persist(db, state, result, i, step_desc)
                await post_step_history(
                    job_name=state.test_case_name,
                    run_id=state.test_case_id,
                    process_name=step_desc,
                    ok=result.get("ok", False),
                    detail="",
                    start=step_started_at,
                    step_index=i,
                    total_steps=state.total_steps,
                    test_step_id=step_id,
                )
                if not result.get("ok", False):   # always critical — wrong page = broken flow
                    _emit_critical_stop(state, i, step_desc)
                    break
                continue

            # ── Toast bypass — no LLM, direct assert_toast ──────────────────
            # Covers: "Verifikasi muncul: <text>" / "Validasi muncul: <text>"
            # Uses keyword-based criticality — toast failure may not break entire flow.
            toast_expected = extract_toast_assertion(step_desc)
            if toast_expected:
                step_started_at = datetime.now(timezone.utc).isoformat()
                body = _prepare_payload(
                    method="assert_toast",
                    params={"expected_text": toast_expected},
                    session_id=session_id,
                    state=state,
                    step_index=i,
                    step_id=step_id,
                    step_desc=step_desc,
                    step_started_at=step_started_at,
                    final_attempt=True,
                )
                result = await execute_step(body, request)
                await _emit_and_persist(db, state, result, i, step_desc)
                await post_step_history(
                    job_name=state.test_case_name,
                    run_id=state.test_case_id,
                    process_name=step_desc,
                    ok=result.get("ok", False),
                    detail="",
                    start=step_started_at,
                    step_index=i,
                    total_steps=state.total_steps,
                    test_step_id=step_id,
                )
                if _is_critical_failure(result.get("ok", False), step_desc):
                    _emit_critical_stop(state, i, step_desc)
                    break
                continue

            # ── VALID: bypass — no LLM, direct assert_text ──────────────────
            # Uses keyword-based criticality — data assertion failure may not break flow.
            valid = extract_valid_assertion(step_desc)
            if valid:
                selector, expected_text = valid
                step_started_at = datetime.now(timezone.utc).isoformat()
                body = _prepare_payload(
                    method="assert_text",
                    params={"selector": selector, "expected": expected_text},
                    session_id=session_id,
                    state=state,
                    step_index=i,
                    step_id=step_id,
                    step_desc=step_desc,
                    step_started_at=step_started_at,
                    final_attempt=True,
                )
                result = await execute_step(body, request)
                await _emit_and_persist(db, state, result, i, step_desc)
                await post_step_history(
                    job_name=state.test_case_name,
                    run_id=state.test_case_id,
                    process_name=step_desc,
                    ok=result.get("ok", False),
                    detail="",
                    start=step_started_at,
                    step_index=i,
                    total_steps=state.total_steps,
                    test_step_id=step_id,
                )
                if _is_critical_failure(result.get("ok", False), step_desc):
                    _emit_critical_stop(state, i, step_desc)
                    break
                continue

            # ── Retry loop: up to _MAX_ATTEMPTS per step ─────────────────────
            # Mirrors n8n: Get Browser Interactables → build prompt → Ollama call →
            #   Parse LLM JSON → Prepare Payload → Execute Browser Action →
            #   IF Step Success → Check Retry → Prep Retry (loops back)
            step_result: dict = {"ok": False, "error": "not executed"}
            step_started_at = ""

            # ── Element cache scoped to this step's retry loop ──────────────────
            # Only refetch the interactable-elements DOM crawl when the page URL
            # actually changed since the last fetch. Avoids re-crawling the full
            # DOM (all frames) on every retry attempt when the previous attempt
            # failed without navigating anywhere.
            _cached_elements: list = []
            _cached_url: Optional[str] = None

            for attempt in range(1, _MAX_ATTEMPTS + 1):
                # ── Get Browser Interactables (cached by URL) ────────────────────
                try:
                    session = await get_session(request, session_id)
                    current_url = session.page.url
                except Exception as exc:
                    print(f"[Runner] get_session failed (attempt {attempt}): {exc}")
                    current_url = None

                if (
                    current_url is not None
                    and current_url == _cached_url
                    and _cached_elements
                    and attempt < _MAX_ATTEMPTS          # never reuse on the last attempt
                ):
                    elements = _cached_elements
                    print(f"[Runner] elements: reused cache (url unchanged, attempt {attempt})")
                else:
                    elements = []
                    try:
                        from tools import cmd_get_interactable_elements
                        el_resp = await cmd_get_interactable_elements({}, session)
                        elements = el_resp.get("elements", [])
                        _cached_elements = elements
                        _cached_url = current_url
                        print(f"[Runner] elements: refetched (url={current_url!r}, attempt {attempt})")
                    except Exception as exc:
                        print(f"[Runner] Elements fetch failed (attempt {attempt}): {exc}")
                        # Best-effort fallback: reuse stale cache instead of an empty
                        # list, so the LLM still has SOME context on this attempt.
                        elements = _cached_elements

                # ── build prompt → Ollama call → Parse LLM JSON ───────────────
                try:
                    parsed = await resolve_step(
                        step_desc, session_id, elements, test_data, attempt
                    )
                except OllamaQuotaExceeded as exc:
                    parsed = {
                        "_llm_error": True,
                        "method": "noop",
                        "params": {},
                        "_raw_response": str(exc)[:200],
                        "_quota_exceeded": True,
                    }
                    print(f"[Runner] LLM parse error (attempt {attempt}): {exc}")
                except RuntimeError as exc:
                    parsed = {
                        "_llm_error": True,
                        "method": "noop",
                        "params": {},
                        "_raw_response": str(exc)[:200],
                    }
                    print(f"[Runner] LLM parse error (attempt {attempt}): {exc}")

                # ── _llm_error → treat as failed, same retry path ─────────────
                if parsed.get("_llm_error"):
                    _raw = parsed.get('_raw_response', '')
                    step_result = {
                        "ok":    False,
                        "error": f"LLM error: {_raw[:100]}",
                    }
                    if parsed.get("_quota_exceeded"):
                        print(f"[Runner] Quota exceeded — skipping remaining attempts for this step")
                        break      # no point retrying — quota won't reset mid-run
                    if attempt < _MAX_ATTEMPTS:
                        continue   # Prep Retry → re-fetch elements, re-call LLM
                    break          # max retries exhausted

                # ── Prepare Payload for MCP Playwright ────────────────────────
                # Verbatim from n8n "Prepare Payload for MCP Playwright":
                #   final_attempt = attempt >= 3
                #   expected_result = test_step_description (not a separate field)
                #   sessionId removed from params (lives at top level)
                final_attempt = attempt >= _MAX_ATTEMPTS
                method        = parsed.get("method", "")
                params        = {
                    k: v
                    for k, v in (parsed.get("params") or {}).items()
                    if k != "sessionId"
                }
                step_started_at = datetime.now(timezone.utc).isoformat()

                body = _prepare_payload(
                    method=method,
                    params=params,
                    session_id=session_id,
                    state=state,
                    step_index=i,
                    step_id=step_id,
                    step_desc=step_desc,
                    step_started_at=step_started_at,
                    final_attempt=final_attempt,
                )

                # ── Execute Browser Action → IF Step Success ──────────────────
                step_result = await execute_step(body, request)
                ok = step_result.get("ok", False)

                if not ok:
                    print(f"[Runner] Step {i} attempt {attempt}/{_MAX_ATTEMPTS} failed: {step_result.get('error', '')[:150]}")

                if ok:
                    break   # IF Step Success TRUE → done, move to next step

                # IF Step Success FALSE → Check Retry
                if attempt < _MAX_ATTEMPTS:
                    continue   # Prep Retry → loop back to Get Browser Interactables
                break           # max retries exhausted → fall through to history

            # ── Post to History API (once, after all attempts) ────────────────
            await _emit_and_persist(db, state, step_result, i, step_desc)
            await post_step_history(
                job_name=state.test_case_name,
                run_id=state.test_case_id,
                process_name=step_desc,
                ok=step_result.get("ok", False),
                detail="",
                start=step_started_at,
                step_index=i,
                total_steps=state.total_steps,
                test_step_id=step_id,
            )

            # ── Stop-early safety net (LLM path) ─────────────────────────────
            # Non-critical step failures continue to next step (existing behavior).
            if _is_critical_failure(step_result.get("ok", False), step_desc):
                _emit_critical_stop(state, i, step_desc)
                break

        # ── Finalize ──────────────────────────────────────────────────────────
        if state.status != "stopped" and state.status != "failed":
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
        })
        if db:
            await db_update_run(
                db,
                state.run_id,
                status=state.status,
                current_step=state.current_step,
                finished_at=state.finished_at,
                script_path=state.script_path,
                report_path=state.report_path,
                error=state.error,
            )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _find_credential_selector(elements: list, field_type: str) -> Optional[str]:
    """
    Scan live page elements and return a selector for the credential field.
    Returns suggested_selector from the element if available, else builds one.
    Returns None if no matching element found (caller should fall back to LLM).
    """
    _USERNAME_HINTS = {"email", "username", "user", "login"}

    for el in elements:
        tag = (el.get("tag") or "").upper()
        if tag != "INPUT":
            continue
        el_type        = (el.get("type")        or "").lower()
        el_id          = (el.get("id")          or "").lower()
        el_name        = (el.get("name")        or "").lower()
        el_placeholder = (el.get("placeholder") or "").lower()

        if field_type == "password":
            if el_type == "password":
                if el.get("suggested_selector"):
                    return el["suggested_selector"]
                if el.get("id"):
                    return f'//INPUT[@id="{el["id"]}"]'
                return '//INPUT[@type="password"]'

        elif field_type in ("username", "email"):
            has_hint = any(
                hint in el_id or hint in el_name or hint in el_placeholder
                for hint in _USERNAME_HINTS
            )
            if el_type in ("email", "text") and has_hint:
                if el.get("suggested_selector"):
                    return el["suggested_selector"]
                if el.get("id"):
                    return f'//INPUT[@id="{el["id"]}"]'
                if el.get("name"):
                    return f'//INPUT[@name="{el["name"]}"]'

    return None


def _find_upload_selector(elements: list, label_hint: str) -> Optional[str]:
    """Find the upload target from live page elements.

    Priority tiers (stops at first hit):
      pass 1   : real file input — wins regardless of hint
      pass 2a-i: upload-word AND hint both match (most specific — disambiguates multi-upload pages)
      pass 2a-ii: upload-word only (no hint, or hint absent from blob)
      pass 2b  : hint only, no upload-word — lowest confidence
    Returns None → caller falls back to LLM.
    """
    hint = (label_hint or "").lower()
    _UPLOAD_WORDS = {"upload", "unggah", "browse", "choose file", "pilih file", "select file", "attach", "lampiran"}

    # pass 1: real file input wins unconditionally
    for el in elements:
        if (el.get("tag") or "").upper() == "INPUT" and (el.get("type") or "").lower() == "file":
            if el.get("suggested_selector"):
                return el["suggested_selector"]
            if el.get("id"):
                return f'//INPUT[@id="{el["id"]}"]'
            return '//INPUT[@type="file"]'

    # pass 2a-i: upload-word AND hint both present — most specific match
    if hint:
        for el in elements:
            blob = " ".join(str(el.get(k, "")) for k in ("text", "aria_label", "placeholder", "class", "id")).lower()
            if any(w in blob for w in _UPLOAD_WORDS) and hint in blob:
                if el.get("suggested_selector"):
                    return el["suggested_selector"]

    # pass 2a-ii: upload-word only — picks first upload target when hint absent or unmatched
    for el in elements:
        blob = " ".join(str(el.get(k, "")) for k in ("text", "aria_label", "placeholder", "class", "id")).lower()
        if any(w in blob for w in _UPLOAD_WORDS):
            if el.get("suggested_selector"):
                return el["suggested_selector"]

    # pass 2b: hint only, no upload-word — lowest confidence
    if hint:
        for el in elements:
            blob = " ".join(str(el.get(k, "")) for k in ("text", "aria_label", "placeholder", "class", "id")).lower()
            if hint in blob:
                if el.get("suggested_selector"):
                    return el["suggested_selector"]

    return None


def _is_critical_failure(ok: bool, step_desc: str) -> bool:
    """True if step failed AND its description contains a critical keyword."""
    return not ok and any(kw in step_desc.lower() for kw in _CRITICAL_STEP_KEYWORDS)


def _emit_critical_stop(state: RunState, step_index: int, step_desc: str) -> None:
    """Set state to failed and push critical_failure event. Call before break."""
    state.status = "failed"
    state.error = f"Critical step failed: {step_desc}"
    state.push_event({
        "type":             "critical_failure",
        "step_index":       step_index,
        "step_description": step_desc,
        "message":          "Run stopped early — critical step failed permanently",
    })


def _prepare_payload(
    *,
    method: str,
    params: dict,
    session_id: str,
    state: RunState,
    step_index: int,
    step_id: str,
    step_desc: str,
    step_started_at: str,
    final_attempt: bool,
) -> dict:
    """
    Verbatim from n8n node "Prepare Payload for MCP Playwright".
    sessionId is top-level; params must NOT contain sessionId.
    expected_result = test_step_description (n8n sets it this way).
    """
    return {
        "sessionId":             session_id,
        "method":                method,
        "params":                params,
        "test_suite_id":         state.suite_id,
        "test_case_id":          state.test_case_id,
        "test_case_name":        state.test_case_name,
        "step_index":            step_index,
        "total_steps":           state.total_steps,
        "test_step_id":          step_id,
        "test_step_description": step_desc,
        "step_started_at":       step_started_at,
        "final_attempt":         final_attempt,
        "expected_result":       step_desc,   # n8n: expected_result = test_step_description
    }


def _emit_step_end(
    state: RunState,
    result: dict,
    step_index: int,
    step_desc: str,
) -> None:
    ok = result.get("ok", False)
    # Capture finalized paths from last-step meta (non-null only on the last step)
    meta = result.get("meta") or {}
    if meta.get("py_script_path"):
        state.script_path = meta["py_script_path"]
    if meta.get("report_path"):
        state.report_path = meta["report_path"]
    state.push_event({
        "type":             "step_end",
        "step_index":       step_index,
        "step_description": step_desc,
        "ok":               ok,
        "status":           "passed" if ok else "failed",
        "error":            result.get("error"),
        "screenshot_path":  result.get("screenshot_path"),
    })
