"""Unit tests for extract_ibkr_data.py CLI script.

These tests operate at a functional/unit boundary:
- They call the in‑process `extract_ibkr_data` function directly (faster than spawning a subprocess).
- They verify that the expected CSV files are created in the output path.
- They check that the function handles multiple data types correctly.

Rationale: Ensure the containerized extraction step works outside Airflow, providing confidence
before orchestration integration tests (full E2E) are added later.
"""
import shutil
from pathlib import Path

import pandas as pd
import pytest

# Import after path adjustment to avoid package import errors when running from repo root.
import importlib.util
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "plugins" / "project_trading" / "extract_ibkr_data.py"
spec = importlib.util.spec_from_file_location("extract_ibkr_data", SCRIPT_PATH)
extract_ibkr_data = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = extract_ibkr_data
spec.loader.exec_module(extract_ibkr_data)


def test_extract_creates_files(tmp_path: Path):
    """The extraction should create one CSV per data type in the given directory."""
    data_types = ["trades", "positions", "market_data"]
    extract_ibkr_data.extract_ibkr_data(
        conn_id="unit_test_ibkr",
        data_types=data_types,
        start_date="2025-01-01",
        end_date="2025-01-02",
        output_path=str(tmp_path),
    )

    for dtype in data_types:
        file_path = tmp_path / f"{dtype}_2025-01-01_to_2025-01-02.csv"
        assert file_path.exists(), f"Expected output file for {dtype} not found"
        # Validate CSV content structure (dummy data has a 'dummy' column)
        df = pd.read_csv(file_path)
        assert "dummy" in df.columns


def test_extract_overwrites_existing(tmp_path: Path):
    """Calling extract twice should overwrite existing files without error."""
    first_path = tmp_path / "trades_2025-01-01_to_2025-01-02.csv"
    first_path.write_text("old data")

    extract_ibkr_data.extract_ibkr_data(
        conn_id="unit_test_ibkr",
        data_types=["trades"],
        start_date="2025-01-01",
        end_date="2025-01-02",
        output_path=str(tmp_path),
    )

    # File should have been overwritten with CSV header 'dummy'
    df = pd.read_csv(first_path)
    assert "dummy" in df.columns
