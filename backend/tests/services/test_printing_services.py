import os
import fitz
import pytest
from unittest.mock import MagicMock

from backend.app.services.printing_services import process_simple_print_job
from backend.app.models.printers.jobs.simple_print_job import SimplePrintJob
from backend.app.models.printers.elements.printeable_file import PrinteableFile

def create_dummy_pdf(path: str):
    doc = fitz.open()
    doc.new_page()
    doc.save(path)
    doc.close()

def test_process_simple_print_job_success(tmp_path, monkeypatch):
    # Mocking dependencies to point to tmp_path
    monkeypatch.setattr("backend.app.services.printing_service.get_archive_path", lambda s, a_id: str(tmp_path))
    monkeypatch.setattr("backend.app.files_management.archive_file_manager.ArchiveFileManager.parse_name_to_file_manager", lambda name: "piece_folder")
    
    # Create required directory structure
    piece_dir = os.path.join(tmp_path, "piece_folder")
    os.makedirs(piece_dir, exist_ok=True)
    
    file1_path = os.path.join(piece_dir, "file1.pdf")
    file2_path = os.path.join(piece_dir, "file2.pdf")
    
    create_dummy_pdf(file1_path)
    create_dummy_pdf(file2_path)
    
    job = SimplePrintJob(
        files=[
            PrinteableFile(archive_id=1, piece_std_name="test1", file_name="file1.pdf", copies=2),
            PrinteableFile(archive_id=1, piece_std_name="test2", file_name="file2.pdf", copies=1),
        ]
    )
    
    session = MagicMock()
    result_bytes = process_simple_print_job(session, job)
    
    assert isinstance(result_bytes, bytes)
    
    # Read the bytes back to verify contents
    result_doc = fitz.open("pdf", result_bytes)
    assert result_doc.page_count == 3  # 2 copies of file1 (1 page each) + 1 copy of file2 (1 page)
    result_doc.close()

def test_process_simple_print_job_file_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.app.services.printing_service.get_archive_path", lambda s, a_id: str(tmp_path))
    monkeypatch.setattr("backend.app.files_management.archive_file_manager.ArchiveFileManager.parse_name_to_file_manager", lambda name: "piece_folder")
    
    piece_dir = os.path.join(tmp_path, "piece_folder")
    os.makedirs(piece_dir, exist_ok=True)
    
    job = SimplePrintJob(
        files=[
            PrinteableFile(archive_id=1, piece_std_name="test1", file_name="missing.pdf", copies=1),
        ]
    )
    
    session = MagicMock()
    
    with pytest.raises(FileNotFoundError, match="File not found"):
        process_simple_print_job(session, job)
