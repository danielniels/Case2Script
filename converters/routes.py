"""
POST /convert/json          Validate + normalize JSON suite
POST /convert/excel         Parse Excel → draft suite
POST /convert/prompt        Text prompt → draft suite (1 Ollama call)
GET  /convert/excel/template  Download blank Excel template
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel

from converters.excel import excel_to_suite, generate_excel_template
from converters.json_input import normalize_suite, validate_suite
from converters.prompt_to_steps import prompt_to_suite

router = APIRouter()


@router.post("/json")
async def convert_json(body: dict):
    """Validate and normalize an uploaded JSON test suite."""
    suite = normalize_suite(body)
    errors = validate_suite(suite)
    if errors:
        raise HTTPException(status_code=422, detail={"errors": errors})
    return suite


@router.post("/excel")
async def convert_excel(file: UploadFile = File(...)):
    """Parse an Excel file and return a draft test suite."""
    contents = await file.read()
    try:
        suite = excel_to_suite(contents, file.filename or "upload.xlsx")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return suite


class PromptRequest(BaseModel):
    text: str
    name: Optional[str] = ""


@router.post("/prompt")
async def convert_prompt(req: PromptRequest):
    """Generate a draft test suite from a free-text scenario description."""
    try:
        suite = await prompt_to_suite(req.text, req.name or "")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama error: {e}")
    return suite


@router.get("/excel/template")
async def get_excel_template():
    """Download a blank Excel template with the expected column headers."""
    xlsx = generate_excel_template()
    return Response(
        content=xlsx,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=test_suite_template.xlsx"},
    )
