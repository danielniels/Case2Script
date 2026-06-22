"""
xlsx → TestSuite (draft, never auto-runs).
Uses pandas to read the Excel. Expected columns:
  test_suite_id, test_suite_name, test_case_id, test_case_name,
  test_step_id, test_step_description, expected_result
"""

from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd

from helpers import clean_excel_formula


_REQUIRED_COLUMNS = {"test_step_description"}
_COLUMN_ALIASES = {
    "step": "test_step_description",
    "description": "test_step_description",
    "langkah": "test_step_description",
    "expected": "expected_result",
    "hasil": "expected_result",
    "case": "test_case_id",
    "tc": "test_case_id",
    "suite": "test_suite_id",
}


def _normalize_col(col: str) -> str:
    c = col.strip().lower().replace(" ", "_")
    return _COLUMN_ALIASES.get(c, c)


def excel_to_suite(file_bytes: bytes, filename: str = "upload.xlsx") -> dict:
    """
    Convert Excel bytes to canonical test suite dict (draft).
    Raises ValueError on unrecognizable format.
    """
    df = pd.read_excel(BytesIO(file_bytes), dtype=str)
    df.columns = [_normalize_col(c) for c in df.columns]
    df = df.dropna(how="all")

    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {missing}. Found: {list(df.columns)}")

    # Fill formula-cell artifacts
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: clean_excel_formula(str(x)) if pd.notna(x) else "")

    suite_id = df["test_suite_id"].iloc[0] if "test_suite_id" in df.columns else Path(filename).stem
    suite_name = df["test_suite_name"].iloc[0] if "test_suite_name" in df.columns else suite_id

    # Group by test_case_id
    if "test_case_id" in df.columns:
        cases = []
        for tc_id, group in df.groupby("test_case_id", sort=False):
            tc_name = group["test_case_name"].iloc[0] if "test_case_name" in group.columns else tc_id
            steps = _rows_to_steps(group)
            cases.append({
                "test_case_id": tc_id,
                "test_case_name": tc_name,
                "test_suite_id": suite_id,
                "steps": steps,
            })
    else:
        steps = _rows_to_steps(df)
        cases = [{
            "test_case_id": suite_id,
            "test_case_name": suite_name,
            "test_suite_id": suite_id,
            "steps": steps,
        }]

    return {
        "id": suite_id,
        "name": suite_name,
        "description": f"Imported from {filename}",
        "test_cases": cases,
        "draft": True,
    }


def _rows_to_steps(df: pd.DataFrame) -> list:
    steps = []
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        desc = str(row.get("test_step_description", "")).strip()
        if not desc:
            continue
        steps.append({
            "test_step_id": str(row.get("test_step_id", i)),
            "test_step_description": desc,
            "expected_result": str(row.get("expected_result", "")).strip(),
        })
    return steps


def generate_excel_template() -> bytes:
    """Return a blank Excel template with the expected columns."""
    df = pd.DataFrame(columns=[
        "test_suite_id", "test_suite_name",
        "test_case_id", "test_case_name",
        "test_step_id", "test_step_description", "expected_result",
    ])
    buf = BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()
