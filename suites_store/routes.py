"""
GET  /suites              List all suites
POST /suites              Create suite
GET  /suites/{id}         Get suite
PUT  /suites/{id}         Update suite
DELETE /suites/{id}       Delete suite
"""

from fastapi import APIRouter, HTTPException
from typing import Any

from suites_store.store import (
    create_suite,
    delete_suite,
    get_suite,
    list_suites,
    update_suite,
)

router = APIRouter()


@router.get("")
async def list_all():
    return {"suites": await list_suites()}


@router.post("")
async def create(body: dict):
    suite = await create_suite(body)
    return suite


@router.get("/{suite_id}")
async def get_one(suite_id: str):
    suite = await get_suite(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail=f"Suite {suite_id!r} not found")
    return suite


@router.put("/{suite_id}")
async def update_one(suite_id: str, body: dict):
    suite = await update_suite(suite_id, body)
    if not suite:
        raise HTTPException(status_code=404, detail=f"Suite {suite_id!r} not found")
    return suite


@router.delete("/{suite_id}")
async def delete_one(suite_id: str):
    deleted = await delete_suite(suite_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Suite {suite_id!r} not found")
    return {"deleted": True, "id": suite_id}
