"""
SQLite persistence for run history.
Tables:
  runs      — one row per run (metadata + final status)
  run_steps — one row per step per run
"""

import aiosqlite
from pathlib import Path
from typing import List, Optional

DB_PATH = Path("data/runs.db")

_CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS runs (
    run_id         TEXT PRIMARY KEY,
    suite_id       TEXT,
    test_case_id   TEXT,
    test_case_name TEXT,
    status         TEXT,
    total_steps    INTEGER,
    current_step   INTEGER DEFAULT 0,
    started_at     TEXT,
    finished_at    TEXT,
    script_path    TEXT,
    report_path    TEXT,
    error          TEXT
)
"""

_CREATE_STEPS = """
CREATE TABLE IF NOT EXISTS run_steps (
    run_id          TEXT,
    step_index      INTEGER,
    description     TEXT,
    status          TEXT,
    screenshot_path TEXT,
    error           TEXT,
    PRIMARY KEY (run_id, step_index)
)
"""


async def init_db() -> aiosqlite.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(DB_PATH))
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute(_CREATE_RUNS)
    await conn.execute(_CREATE_STEPS)
    # Migrate existing DB: add input_mode / input_content if not present
    for col in ("input_mode", "input_content"):
        try:
            await conn.execute(f"ALTER TABLE runs ADD COLUMN {col} TEXT")
        except Exception:
            pass
    await conn.commit()
    return conn


async def db_insert_run(
    conn: aiosqlite.Connection,
    *,
    run_id: str,
    suite_id: str,
    test_case_id: str,
    test_case_name: str,
    total_steps: int,
    started_at: str,
    input_mode: Optional[str] = None,
    input_content: Optional[str] = None,
) -> None:
    await conn.execute(
        """INSERT OR IGNORE INTO runs
           (run_id, suite_id, test_case_id, test_case_name, status, total_steps, started_at,
            input_mode, input_content)
           VALUES (?, ?, ?, ?, 'running', ?, ?, ?, ?)""",
        (run_id, suite_id, test_case_id, test_case_name, total_steps, started_at,
         input_mode, input_content),
    )
    await conn.commit()


async def db_update_run(conn: aiosqlite.Connection, run_id: str, **kwargs) -> None:
    if not kwargs:
        return
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [run_id]
    await conn.execute(f"UPDATE runs SET {sets} WHERE run_id = ?", vals)
    await conn.commit()


async def db_upsert_step(
    conn: aiosqlite.Connection,
    *,
    run_id: str,
    step_index: int,
    description: str,
    status: str,
    screenshot_path: Optional[str],
    error: Optional[str],
) -> None:
    await conn.execute(
        """INSERT INTO run_steps (run_id, step_index, description, status, screenshot_path, error)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(run_id, step_index) DO UPDATE SET
               status          = excluded.status,
               screenshot_path = excluded.screenshot_path,
               error           = excluded.error""",
        (run_id, step_index, description, status, screenshot_path, error),
    )
    await conn.commit()


async def db_get_run(conn: aiosqlite.Connection, run_id: str) -> Optional[dict]:
    async with conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None


async def db_get_steps(conn: aiosqlite.Connection, run_id: str) -> List[dict]:
    async with conn.execute(
        "SELECT * FROM run_steps WHERE run_id = ? ORDER BY step_index", (run_id,)
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]


async def db_delete_run(conn: aiosqlite.Connection, run_id: str) -> bool:
    async with conn.execute("SELECT run_id FROM runs WHERE run_id = ?", (run_id,)) as cur:
        if not await cur.fetchone():
            return False
    await conn.execute("DELETE FROM run_steps WHERE run_id = ?", (run_id,))
    await conn.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))
    await conn.commit()
    return True


async def db_list_runs(conn: aiosqlite.Connection, limit: int = 100) -> List[dict]:
    async with conn.execute(
        "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)
    ) as cur:
        return [dict(r) for r in await cur.fetchall()]
