import os
import io
import zipfile
import pytest
import fitz
from unittest.mock import MagicMock

from backend.app.services.export_strategies.by_element import (
    _process_element_task,
    ByElementExporter,
)
from backend.app.models.presets.resolution_preset import SolvedPreset
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJobConfig

@pytest.fixture
def dummy_pdf_path(tmp_path):
    """Creates a valid empty PDF file for testing."""
    pdf_path = tmp_path / "dummy.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_process_element_task_file_not_found(tmp_path):
    element_name = "test_element"
    inner_items = {
        "1-PIECE": {
            "archive_id": 1,
            "piece_std_name": "1-PIECE",
            "file": "missing.pdf",
            "copies": 1,
        }
    }
    archive_paths = {1: str(tmp_path)}
    config = {}

    name, pdf_bytes, logs = _process_element_task(
        element_name, inner_items, archive_paths, config
    )

    assert name == element_name
    assert pdf_bytes == b""
    assert len(logs) == 1
    assert "File not found" in logs[0]

def test_process_element_task_success(tmp_path, dummy_pdf_path):
    # Setup directory structure matching ArchiveFileManager.parse_name_to_file_manager
    doc_dir = tmp_path / "1-PIECE" / "partituras"
    doc_dir.mkdir(parents=True, exist_ok=True)
    target_pdf = doc_dir / "target.pdf"
    
    # Copy dummy PDF to target
    with open(dummy_pdf_path, "rb") as src, open(target_pdf, "wb") as dst:
        dst.write(src.read())

    element_name = "Trumpet"
    inner_items = {
        "1-PIECE": {
            "archive_id": 1,
            "piece_std_name": "1-PIECE",
            "file": "target.pdf",
            "copies": 1,
        }
    }
    archive_paths = {1: str(tmp_path)}
    config = {
        "add_piece_number": False,
        "add_index": False,
        "add_cover_page": False,
    }

    name, pdf_bytes, logs = _process_element_task(
        element_name, inner_items, archive_paths, config
    )

    assert name == element_name
    assert len(pdf_bytes) > 0
    assert len(logs) == 0

    # Ensure valid PDF
    doc = fitz.open("pdf", pdf_bytes)
    assert len(doc) >= 1
    doc.close()

def test_export_generates_zip(tmp_path, dummy_pdf_path, monkeypatch):
    # Setup dummy data on disk
    doc_dir = tmp_path / "1-PIECE" / "partituras"
    doc_dir.mkdir(parents=True, exist_ok=True)
    target_pdf = doc_dir / "target.pdf"
    with open(dummy_pdf_path, "rb") as src, open(target_pdf, "wb") as dst:
        dst.write(src.read())

    # Mock get_archive_path
    monkeypatch.setattr(
        "backend.app.services.export_strategies.by_element.get_archive_path",
        lambda session, arch_id: str(tmp_path)
    )

    session_mock = MagicMock()
    
    # Create mock SolvedPreset
    item_mock = MagicMock()
    item_mock.archive_id = 1
    item_mock.model_dump.return_value = {
        "archive_id": 1,
        "piece_std_name": "1-PIECE",
        "file": "target.pdf",
        "copies": 1,
    }

    solved_preset = MagicMock(spec=SolvedPreset)
    solved_preset.preset_name = "Test Preset"
    solved_preset.solution = {
        "Violin": { "1-PIECE": item_mock }
    }

    # Create mock config
    config = MagicMock(spec=PresetPrintJobConfig)
    config.model_dump.return_value = {}

    exporter = ByElementExporter()
    zip_bytes = exporter.export(session_mock, solved_preset, config)

    assert len(zip_bytes) > 0
    
    # Verify zip contents safely
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        file_list = zf.namelist()
        assert "Violin.pdf" in file_list
