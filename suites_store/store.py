"""
CRUD for test suites. Reads/writes data/test_suites/*.json.
Lock per-suite, atomic write (write to .tmp then rename).
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


_SUITES_DIR = Path("data/test_suites")
_locks: Dict[str, asyncio.Lock] = {}
_global_lock = asyncio.Lock()


def _suite_path(suite_id: str) -> Path:
    return _SUITES_DIR / f"{suite_id}.json"


async def _get_lock(suite_id: str) -> asyncio.Lock:
    async with _global_lock:
        if suite_id not in _locks:
            _locks[suite_id] = asyncio.Lock()
        return _locks[suite_id]


async def list_suites() -> List[dict]:
    _SUITES_DIR.mkdir(parents=True, exist_ok=True)
    suites = []
    for f in sorted(_SUITES_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            suites.append(_summary(data, f.stem))
        except Exception:
            continue
    return suites


async def get_suite(suite_id: str) -> Optional[dict]:
    p = _suite_path(suite_id)
    if not p.exists():
        return None
    lock = await _get_lock(suite_id)
    async with lock:
        return json.loads(p.read_text(encoding="utf-8"))


async def create_suite(data: dict) -> dict:
    _SUITES_DIR.mkdir(parents=True, exist_ok=True)
    suite_id = data.get("id") or str(uuid.uuid4())[:8]
    data["id"] = suite_id
    data.setdefault("created_at", datetime.utcnow().isoformat())
    data["updated_at"] = datetime.utcnow().isoformat()
    lock = await _get_lock(suite_id)
    async with lock:
        _atomic_write(_suite_path(suite_id), data)
    return data


async def update_suite(suite_id: str, data: dict) -> Optional[dict]:
    p = _suite_path(suite_id)
    if not p.exists():
        return None
    lock = await _get_lock(suite_id)
    async with lock:
        existing = json.loads(p.read_text(encoding="utf-8"))
        existing.update(data)
        existing["id"] = suite_id
        existing["updated_at"] = datetime.utcnow().isoformat()
        _atomic_write(p, existing)
        return existing


async def delete_suite(suite_id: str) -> bool:
    p = _suite_path(suite_id)
    if not p.exists():
        return False
    lock = await _get_lock(suite_id)
    async with lock:
        p.unlink()
    return True


def _atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _summary(data: dict, suite_id: str) -> dict:
    return {
        "id": data.get("id", suite_id),
        "name": data.get("name", suite_id),
        "description": data.get("description", ""),
        "test_case_count": len(data.get("test_cases", [])),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }
