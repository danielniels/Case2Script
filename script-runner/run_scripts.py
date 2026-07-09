#!/usr/bin/env python3
"""
run_scripts.py — standalone batch runner for exported Case2Script Playwright scripts.

Fully independent of the Case2Script FastAPI backend / UI. Point it at ANY folder
containing auto-generated *.py Playwright scripts (e.g. Case2Script's
data/saved_playwright_scripts_py) and it will:

  1. List every script in the folder, numbered.
  2. Let you pick which ones to run (by number), or run all.
  3. Execute each as its own subprocess (own Python process -> own browser,
     own event loop). If one script errors/crashes, that subprocess just exits
     non-zero — the loop moves on to the next script. No zombie browsers, no
     leaked state bleeding between scripts.
  4. Print a pass/fail summary and write a JSON + HTML report.

--- Setup (per senior's request: own folder, own playwright install) -----------

    cd script-runner
    python3 -m venv venv
    source venv/bin/activate        # Windows: venv\\Scripts\\activate
    pip install -r requirements.txt
    playwright install chromium

--- Usage -----------------------------------------------------------------------

    # Interactive — lists scripts, prompts which numbers to run
    python run_scripts.py /path/to/data/saved_playwright_scripts_py

    # Run everything, sequential (default)
    python run_scripts.py /path/to/scripts --all

    # Run specific ones by number (as listed), comma or range syntax
    python run_scripts.py /path/to/scripts --only 1,3,5
    python run_scripts.py /path/to/scripts --only 1-4,7

    # Run all, in parallel (careful: N Chromium instances = N x RAM/CPU)
    python run_scripts.py /path/to/scripts --all --parallel 3

Exit code: 0 if every selected script passed, 1 if at least one failed.
That makes it usable in CI later even though it's a plain CLI tool today.
"""

import argparse
import html
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# discovery + selection
# ---------------------------------------------------------------------------

def discover_scripts(folder: Path) -> List[Path]:
    scripts = sorted(folder.glob("*.py"))
    # never try to "run" ourselves if someone points the tool at its own folder
    scripts = [s for s in scripts if s.resolve() != Path(__file__).resolve()]
    return scripts


def print_menu(scripts: List[Path]) -> None:
    print(f"\nFound {len(scripts)} script(s):\n")
    for i, s in enumerate(scripts, start=1):
        print(f"  [{i}] {s.name}")
    print()


def parse_selection(raw: str, total: int) -> List[int]:
    """
    '1,3,5'     -> [1, 3, 5]
    '1-4,7'     -> [1, 2, 3, 4, 7]
    'all' / '*' -> [1..total]
    Returns 1-based indices, de-duped, in the order given (range expanded ascending).
    """
    raw = raw.strip().lower()
    if raw in ("all", "*"):
        return list(range(1, total + 1))

    indices: List[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(part))

    seen = set()
    ordered = []
    for idx in indices:
        if idx < 1 or idx > total:
            raise ValueError(f"Selection {idx} out of range (1-{total})")
        if idx not in seen:
            seen.add(idx)
            ordered.append(idx)
    return ordered


def prompt_selection(total: int) -> List[int]:
    while True:
        raw = input(f"Pilih nomor script yang mau dijalankan (contoh: 1,3,5 / 1-4 / all): ").strip()
        try:
            selection = parse_selection(raw, total)
            if not selection:
                print("Tidak ada yang dipilih, coba lagi.")
                continue
            return selection
        except ValueError as exc:
            print(f"Input tidak valid: {exc}")


# ---------------------------------------------------------------------------
# execution
# ---------------------------------------------------------------------------

def _load_step_details(script: Path) -> List[dict]:
    """
    Case2Script's generator (stores.py::generate_playwright_py_from_json) writes
    a '<script_stem>.result.json' next to the script with per-step pass/fail +
    error, if the script was produced by that generator. Plain/manual scripts
    won't have this file — that's fine, we just fall back to stderr_tail.
    """
    result_path = script.with_suffix("").with_suffix(".result.json")
    if not result_path.exists():
        return []
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
        return data.get("steps", [])
    except Exception:
        return []


def run_one(script: Path, timeout: Optional[int], python_bin: str, allow_dialog: bool = False) -> dict:
    """Run a single script as its own subprocess. Never raises — always returns a result dict.

    allow_dialog=False (default) sets C2S_NO_DIALOG=1 in the child's env. Case2Script's
    generated upload-file helper (_resolve_upload_file) opens a native OS file picker as
    a last resort when it can't auto-resolve a file, and waits up to 120s for a human to
    click something. That's fine for a single manual run, but poisonous for a batch: the
    dialog can pop up behind other windows during an unattended --all run and silently
    eat 2 minutes per occurrence before timing out. Batch mode should fail fast instead.
    """
    started = time.monotonic()
    started_at = datetime.now().isoformat(timespec="seconds")
    env = None
    if not allow_dialog:
        import os as _os
        env = _os.environ.copy()
        env["C2S_NO_DIALOG"] = "1"
    try:
        proc = subprocess.run(
            [python_bin, str(script)],
            cwd=str(script.parent),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            # NOTE: no check=True on purpose — a non-zero exit must NOT raise here.
            # We want to record the failure and let the caller continue to the
            # next script regardless of this one's outcome.
        )
        ok = proc.returncode == 0
        return {
            "script": script.name,
            "ok": ok,
            "returncode": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
            "started_at": started_at,
            "duration_sec": round(time.monotonic() - started, 2),
            "timed_out": False,
            "step_details": _load_step_details(script),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "script": script.name,
            "ok": False,
            "returncode": None,
            "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": f"Timed out after {timeout}s",
            "started_at": started_at,
            "duration_sec": round(time.monotonic() - started, 2),
            "timed_out": True,
            "step_details": _load_step_details(script),
        }
    except Exception as exc:
        # Catch-all: e.g. python_bin not found. Still don't crash the batch.
        return {
            "script": script.name,
            "ok": False,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": str(exc),
            "started_at": started_at,
            "duration_sec": round(time.monotonic() - started, 2),
            "timed_out": False,
            "step_details": [],
        }


def run_sequential(scripts: List[Path], timeout: Optional[int], python_bin: str, allow_dialog: bool = False) -> List[dict]:
    results = []
    total = len(scripts)
    for i, script in enumerate(scripts, start=1):
        print(f"[{i}/{total}] Running {script.name} ...", flush=True)
        result = run_one(script, timeout, python_bin, allow_dialog)
        status = "PASSED" if result["ok"] else f"FAILED (exit={result['returncode']})"
        print(f"    -> {status}  ({result['duration_sec']}s)")
        if not result["ok"] and result["stderr_tail"]:
            print(f"    stderr: {result['stderr_tail'].strip().splitlines()[-1] if result['stderr_tail'].strip() else ''}")
        results.append(result)
    return results


def run_parallel(scripts: List[Path], timeout: Optional[int], python_bin: str, workers: int, allow_dialog: bool = False) -> List[dict]:
    print(f"Running {len(scripts)} script(s) in parallel (max {workers} concurrent)...\n")
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_one, s, timeout, python_bin, allow_dialog): s for s in scripts}
        for future in as_completed(futures):
            script = futures[future]
            result = future.result()
            status = "PASSED" if result["ok"] else f"FAILED (exit={result['returncode']})"
            print(f"{script.name}: {status}  ({result['duration_sec']}s)")
            results.append(result)
    # keep report order stable regardless of finish order
    order = {s.name: i for i, s in enumerate(scripts)}
    results.sort(key=lambda r: order[r["script"]])
    return results


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def print_summary(results: List[dict]) -> bool:
    passed = sum(1 for r in results if r["ok"])
    failed = len(results) - passed
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed, {len(results)} total")
    print("=" * 60)
    for r in results:
        mark = "PASS" if r["ok"] else "FAIL"
        print(f"  [{mark}] {r['script']}  ({r['duration_sec']}s)")
    print()
    return failed == 0


def write_report(results: List[dict], folder: Path) -> Path:
    reports_dir = folder / "reports"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"batch_run_{timestamp}.json"
    report_path.write_text(
        json.dumps(
            {
                "run_at": datetime.now().isoformat(timespec="seconds"),
                "total": len(results),
                "passed": sum(1 for r in results if r["ok"]),
                "failed": sum(1 for r in results if not r["ok"]),
                "results": results,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return report_path


# ---------------------------------------------------------------------------
# HTML report — self-contained, no server needed, double-click to open.
# Pass/fail icon per script; click a row to expand step-by-step detail when
# the script was produced by Case2Script's generator (has a .result.json).
# Falls back to the raw stderr tail for plain/manual scripts.
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Batch Run Report — {run_at}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", Arial, sans-serif; background:#0f1115; color:#e6e6e6; margin:0; padding:28px; }}
  h1 {{ font-size:20px; margin:0 0 4px; }}
  .meta {{ color:#9aa0a6; margin-bottom:18px; font-size:13px; }}
  .summary {{ display:flex; gap:10px; margin-bottom:20px; }}
  .badge {{ padding:6px 14px; border-radius:6px; font-weight:600; font-size:13px; }}
  .badge.pass {{ background:#123d24; color:#4ade80; }}
  .badge.fail {{ background:#3d1414; color:#f87171; }}
  details {{ background:#1a1d23; border:1px solid #2a2e37; border-radius:8px; margin-bottom:8px; }}
  summary {{ cursor:pointer; padding:12px 16px; display:flex; align-items:center; gap:10px; list-style:none; }}
  summary::-webkit-details-marker {{ display:none; }}
  summary::marker {{ content: ""; }}
  .icon {{ width:20px; height:20px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; flex-shrink:0; }}
  .icon.ok {{ background:#123d24; color:#4ade80; }}
  .icon.err {{ background:#5c1a1a; color:#ff6b6b; }}
  .script-name {{ font-weight:600; flex:1; }}
  .duration {{ color:#9aa0a6; font-size:12px; }}
  .body-inner {{ padding:0 16px 14px 46px; }}
  .step {{ padding:8px 0; border-top:1px solid #2a2e37; font-size:13px; }}
  .step:first-child {{ border-top:none; }}
  .step-head {{ display:flex; gap:8px; align-items:center; }}
  .step-status {{ font-size:11px; padding:2px 8px; border-radius:4px; font-weight:600; text-transform:uppercase; }}
  .step-status.passed {{ background:#123d24; color:#4ade80; }}
  .step-status.failed {{ background:#5c1a1a; color:#ff6b6b; }}
  .step-error {{ margin-top:4px; color:#ff8a8a; font-family:ui-monospace,Consolas,monospace; font-size:12px; white-space:pre-wrap; }}
  .stderr-box {{ background:#0d0f13; border-radius:6px; padding:10px 12px; font-family:ui-monospace,Consolas,monospace; font-size:12px; color:#ff8a8a; white-space:pre-wrap; max-height:220px; overflow:auto; }}
  .no-detail {{ color:#9aa0a6; font-size:12px; font-style:italic; }}
</style>
</head>
<body>
  <h1>Batch Run Report</h1>
  <div class="meta">{run_at} &middot; {folder}</div>
  <div class="summary">
    <span class="badge pass">{passed} passed</span>
    <span class="badge fail">{failed} failed</span>
  </div>
  {rows}
</body>
</html>
"""

_STEP_TEMPLATE = """    <div class="step">
      <div class="step-head">
        <span class="step-status {status_class}">{status}</span>
        <span>Step {step_id}: {description}</span>
      </div>
      {error_html}
    </div>
"""

_ROW_TEMPLATE = """  <details{open_attr}>
    <summary>
      <span class="icon {icon_class}">{icon_char}</span>
      <span class="script-name">{name}</span>
      <span class="duration">{duration}s</span>
    </summary>
    <div class="body-inner">
{body}
    </div>
  </details>
"""


def _render_row(result: dict) -> str:
    ok = result["ok"]
    steps = result.get("step_details") or []

    if steps:
        body = "".join(
            _STEP_TEMPLATE.format(
                status_class=s.get("status", "passed"),
                status=s.get("status", "passed"),
                step_id=html.escape(str(s.get("step_id", "?"))),
                description=html.escape(str(s.get("description", ""))),
                error_html=(
                    f'<div class="step-error">{html.escape(str(s.get("error")))}</div>'
                    if s.get("error") else ""
                ),
            )
            for s in steps
        )
    elif not ok:
        stderr = result.get("stderr_tail", "").strip()
        body = (
            f'<div class="stderr-box">{html.escape(stderr)}</div>'
            if stderr else '<div class="no-detail">No structured step detail available (not a Case2Script-generated script) and no stderr captured.</div>'
        )
    else:
        body = '<div class="no-detail">Passed — no structured step detail available for this script.</div>'

    return _ROW_TEMPLATE.format(
        open_attr=" open" if not ok else "",
        icon_class="ok" if ok else "err",
        icon_char="&#10003;" if ok else "!",
        name=html.escape(result["script"]),
        duration=result["duration_sec"],
        body=body,
    )


def write_html_report(results: List[dict], folder: Path, run_at: str) -> Path:
    reports_dir = folder / "reports"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = reports_dir / f"batch_run_{timestamp}.html"
    rows = "".join(_render_row(r) for r in results)
    html_content = _HTML_TEMPLATE.format(
        run_at=run_at,
        folder=html.escape(str(folder)),
        passed=sum(1 for r in results if r["ok"]),
        failed=sum(1 for r in results if not r["ok"]),
        rows=rows,
    )
    html_path.write_text(html_content, encoding="utf-8")
    return html_path


# ---------------------------------------------------------------------------
# entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-run exported Case2Script Playwright scripts.")
    parser.add_argument("folder", type=str, help="Folder containing the *.py scripts to run")
    parser.add_argument("--all", action="store_true", help="Run every script in the folder")
    parser.add_argument("--only", type=str, default=None, help="Comma/range list of script numbers, e.g. 1,3,5 or 1-4,7")
    parser.add_argument("--parallel", type=int, default=0, help="Run N scripts concurrently (default: 0 = sequential)")
    parser.add_argument("--timeout", type=int, default=180, help="Per-script timeout in seconds (default: 180)")
    parser.add_argument("--python-bin", type=str, default=sys.executable, help="Python interpreter to run each script with")
    parser.add_argument(
        "--allow-dialog", action="store_true",
        help=(
            "Allow Case2Script's upload-file fallback to open a native OS file picker "
            "when it can't auto-resolve a file (waits up to 120s per occurrence). "
            "OFF by default for batch runs — unresolved uploads fail fast instead, "
            "so one missing file doesn't stall an unattended --all run."
        ),
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Not a folder: {folder}")
        return 2

    scripts = discover_scripts(folder)
    if not scripts:
        print(f"No .py scripts found in {folder}")
        return 2

    print_menu(scripts)

    if args.all:
        selection = list(range(1, len(scripts) + 1))
    elif args.only:
        try:
            selection = parse_selection(args.only, len(scripts))
        except ValueError as exc:
            print(f"Invalid --only value: {exc}")
            return 2
    else:
        selection = prompt_selection(len(scripts))

    chosen = [scripts[i - 1] for i in selection]
    print(f"Selected {len(chosen)} script(s): {', '.join(s.name for s in chosen)}\n")

    if args.parallel and args.parallel > 1:
        results = run_parallel(chosen, args.timeout, args.python_bin, args.parallel, args.allow_dialog)
    else:
        results = run_sequential(chosen, args.timeout, args.python_bin, args.allow_dialog)

    all_passed = print_summary(results)
    run_at = datetime.now().isoformat(timespec="seconds")
    report_path = write_report(results, folder)
    html_path = write_html_report(results, folder, run_at)
    print(f"JSON report:  {report_path}")
    print(f"HTML report:  {html_path}  (open this in a browser)")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
