import pytest
from unittest.mock import patch, MagicMock, mock_open

from sqlmodel import Session

from backend.app.services.classification_services import (
    precheck_classification, 
    extract_and_merge_pages, 
    backup_source_files, 
    restore_last_backup,
    save_generated_pdfs,
    classify
)
from backend.app.constants.constants import DIR_SCORES
from backend.app.models.classification.classification_job import ClassificationJob
from backend.app.models.classification.classified_document import ClassifiedDocument, ClassifiedDocumentConfig
from backend.app.models.classification.source_page import SourcePage
from backend.app.error import ClassificationFileExistsError


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@pytest.fixture
def base_job():
    page = SourcePage(file_name="source_1.pdf", page=0)
    config = ClassifiedDocumentConfig(overwrite=False, rename=None)
    doc = ClassifiedDocument(config=config, pages=[page])
    
    return ClassificationJob(
        piece_std_name="Test Piece",
        archive_id=1,
        source_files=["source_1.pdf"],
        classifications={"Flauta_1": doc}
    )

@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_precheck_unhandled_collision_raises_error(mock_get_archive, mock_exists, mock_session, base_job):
    mock_get_archive.return_value = "/mock/archive"
    # Make os.path.exists return True everywhere to trigger the collision check
    mock_exists.return_value = True

    with pytest.raises(ClassificationFileExistsError) as exc_info:
        precheck_classification(mock_session, base_job)
    
    assert "Flauta_1" in exc_info.value.incorrect_keys


@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_precheck_handled_collision_with_overwrite(mock_get_archive, mock_exists, mock_session, base_job):
    mock_get_archive.return_value = "/mock/archive"
    # Return True for everything, so target file appears to exist
    mock_exists.return_value = True
    
    # Configure to overwrite explicitly
    base_job.classifications["Flauta_1"].config.overwrite = True

    # Should not raise any error
    precheck_classification(mock_session, base_job)


@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_precheck_handled_collision_with_rename(mock_get_archive, mock_exists, mock_session, base_job):
    mock_get_archive.return_value = "/mock/archive"
    mock_exists.return_value = True
    
    # Configure to rename on collision
    base_job.classifications["Flauta_1"].config.rename = "Flauta_1_v2"

    precheck_classification(mock_session, base_job)
    
    # The dictionary key should have been renamed
    assert "Flauta_1" not in base_job.classifications
    assert "Flauta_1_v2" in base_job.classifications


@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_precheck_invalid_source_page_reference(mock_get_archive, mock_exists, mock_session, base_job):
    mock_get_archive.return_value = "/mock/archive"
    
    # Make dirs exist
    mock_exists.return_value = True 
    
    # Intentionally add a page from an undeclared source file
    bad_page = SourcePage(file_name="does_not_exist.pdf", page=0)
    base_job.classifications["Flauta_1"].pages.append(bad_page)

    with pytest.raises(ValueError, match="not found in source_files"):
        precheck_classification(mock_session, base_job)

@patch("backend.app.services.classification_services.fitz.open")
def test_extract_and_merge_pages_success(mock_fitz_open):
    # Setup mock behavior
    mock_merged_doc = MagicMock()
    mock_merged_doc.tobytes.return_value = b"mocked_pdf_bytes"
    
    mock_source_a = MagicMock()
    mock_source_b = MagicMock()
    
    def mock_open_side_effect(*args, **kwargs):
        if not args:
            return mock_merged_doc
        if "source_A.pdf" in args[0]:
            return mock_source_a
        if "source_B.pdf" in args[0]:
            return mock_source_b
        return MagicMock()
        
    mock_fitz_open.side_effect = mock_open_side_effect

    doc = ClassifiedDocument(
        config=ClassifiedDocumentConfig(),
        pages=[
            SourcePage(file_name="source_A.pdf", page=0),
            SourcePage(file_name="source_B.pdf", page=1)
        ]
    )
    classifications = {"Oboe_1": doc}

    # Execute
    result = extract_and_merge_pages(classifications, "/mock/dir")

    # Assert correct bytes returned
    assert "Oboe_1.pdf" in result
    assert result["Oboe_1.pdf"] == b"mocked_pdf_bytes"

    # Assert pages inserted from correct docs and indexes
    mock_merged_doc.insert_pdf.assert_any_call(mock_source_a, from_page=0, to_page=0)
    mock_merged_doc.insert_pdf.assert_any_call(mock_source_b, from_page=1, to_page=1)

    # Assert everything was closed
    mock_merged_doc.close.assert_called_once()
    mock_source_a.close.assert_called_once()
    mock_source_b.close.assert_called_once()

@patch("backend.app.services.classification_services.fitz.open")
def test_extract_and_merge_pages_empty_pages_list(mock_fitz_open):
    # Arrange
    mock_merged_doc = MagicMock()
    mock_merged_doc.tobytes.return_value = b"empty_pdf_bytes"
    mock_fitz_open.return_value = mock_merged_doc

    doc = ClassifiedDocument(
        config=ClassifiedDocumentConfig(),
        pages=[]  # Empty pages list
    )
    classifications = {"Empty_Instrument": doc}

    # Act
    result = extract_and_merge_pages(classifications, "/mock/source_dir")

    # Assert
    assert "Empty_Instrument.pdf" in result
    assert result["Empty_Instrument.pdf"] == b"empty_pdf_bytes"
    mock_merged_doc.insert_pdf.assert_not_called()
    mock_merged_doc.close.assert_called_once()

@patch("backend.app.services.classification_services.fitz.open")
def test_extract_and_merge_pages_closes_on_error(mock_fitz_open):
    mock_merged_doc = MagicMock()
    mock_source_a = MagicMock()
    
    # Simulate an error inserting the first page
    mock_merged_doc.insert_pdf.side_effect = Exception("Simulated PyMuPDF Error")
    
    def mock_open_side_effect(*args, **kwargs):
        if not args:
            return mock_merged_doc
        if "source_A.pdf" in args[0]:
            return mock_source_a
        return MagicMock()
        
    mock_fitz_open.side_effect = mock_open_side_effect

    doc = ClassifiedDocument(
        config=ClassifiedDocumentConfig(),
        pages=[SourcePage(file_name="source_A.pdf", page=0)]
    )
    classifications = {"Oboe_1": doc}

    # Execute and verify exception propagates
    with pytest.raises(Exception, match="Simulated PyMuPDF Error"):
        extract_and_merge_pages(classifications, "/mock/dir")

    # The opened source document A must STILL be closed via the finally block
    mock_source_a.close.assert_called_once()

@patch("backend.app.services.classification_services.datetime")
@patch("backend.app.services.classification_services.shutil.move")
@patch("backend.app.services.classification_services.os.makedirs")
@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_backup_source_files(mock_get_archive, mock_exists, mock_makedirs, mock_move, mock_datetime, mock_session):
    # Setup mocks
    mock_get_archive.return_value = "/mock/archive"
    
    # Let's say the target backup dir doesn't exist yet, but the source files do
    def exists_side_effect(path):
        if "backup" in path and "2023-01-01_12-00-00" in path:
            return False
        return True
    mock_exists.side_effect = exists_side_effect
    
    mock_date = MagicMock()
    mock_date.strftime.return_value = "2023-01-01_12-00-00"
    mock_datetime.datetime.now.return_value = mock_date

    # Execute
    result = backup_source_files(mock_session, 1, "Test Piece", ["file1.pdf", "file2.pdf"])

    # Assertions
    assert result == "2023-01-01_12-00-00"
    mock_makedirs.assert_called_once()
    assert mock_move.call_count == 2
    
    # We just ensure move was called with the right filenames
    assert "file1.pdf" in mock_move.call_args_list[0][0][0]
    assert "file2.pdf" in mock_move.call_args_list[1][0][0]

@patch("backend.app.services.classification_services.shutil.rmtree")
@patch("backend.app.services.classification_services.shutil.move")
@patch("backend.app.services.classification_services.os.path.isfile")
@patch("backend.app.services.classification_services.os.path.isdir")
@patch("backend.app.services.classification_services.os.listdir")
@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_restore_last_backup_success(mock_get_archive, mock_exists, mock_listdir, mock_isdir, mock_isfile, mock_move, mock_rmtree, mock_session):
    mock_get_archive.return_value = "/mock/archive"
    mock_exists.return_value = True
    
    # Mock listdir: first call for backup dir (returns folder names), second for the specific backup folder (returns files)
    def listdir_side_effect(path):
        if path.endswith("backup"):
            return ["2023-01-01_10-00-00", "2023-01-02_10-00-00"]
        return ["file1.pdf", "file2.pdf"]
    mock_listdir.side_effect = listdir_side_effect
    
    mock_isdir.return_value = True
    mock_isfile.return_value = True

    # Execute
    restore_last_backup(mock_session, 1, "Test Piece")

    # The latest folder is 2023-01-02_10-00-00
    assert mock_move.call_count == 2
    
    # Extract the args from the first move call
    src, dest = mock_move.call_args_list[0][0]
    assert "2023-01-02_10-00-00" in src
    assert "file1.pdf" in src
    assert DIR_SCORES in dest # Matches DIR_SCORES constant

    # Assert directory cleanup
    rmtree_path = mock_rmtree.call_args[0][0]
    assert "2023-01-02_10-00-00" in rmtree_path

@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_restore_last_backup_no_backup_folder(mock_get_archive, mock_exists, mock_session):
    mock_get_archive.return_value = "/mock/archive"
    mock_exists.return_value = False # backup folder doesn't exist

    with pytest.raises(FileNotFoundError, match="Backup folder not found"):
        restore_last_backup(mock_session, 1, "Test Piece")

@patch("backend.app.services.classification_services.os.listdir")
@patch("backend.app.services.classification_services.os.path.exists")
@patch("backend.app.services.classification_services.get_archive_path")
def test_restore_last_backup_empty_backups(mock_get_archive, mock_exists, mock_listdir, mock_session):
    mock_get_archive.return_value = "/mock/archive"
    mock_exists.return_value = True
    # backup folder exists, but it contains no inner directories
    mock_listdir.return_value = []

    with pytest.raises(FileNotFoundError, match="No backups found to restore"):
        restore_last_backup(mock_session, 1, "Test Piece")

@patch("backend.app.services.classification_services.get_archive_path")
@patch("backend.app.services.classification_services.ArchiveFileManager.parse_name_to_file_manager")
@patch("builtins.open", new_callable=mock_open)
def test_save_generated_pdfs(mock_file_open, mock_parse_name, mock_get_archive, mock_session):
    # Arrange
    mock_get_archive.return_value = "/mock/archive"
    mock_parse_name.return_value = "Test_Piece"
    
    generated_pdfs = {
        "Flauta_1.pdf": b"fake_pdf_bytes_1",
        "Oboe_1.pdf": b"fake_pdf_bytes_2"
    }

    # Act
    save_generated_pdfs(mock_session, 1, "Test Piece", generated_pdfs)

    # Assert
    assert mock_file_open.call_count == 2
    
    # Check Flauta_1.pdf write properly resolving paths
    mock_file_open.assert_any_call(f"/mock/archive\\Test_Piece\\{DIR_SCORES}\\Flauta_1.pdf", "wb")
    
    # Check Oboe_1.pdf write
    mock_file_open.assert_any_call(f"/mock/archive\\Test_Piece\\{DIR_SCORES}\\Oboe_1.pdf", "wb")
    
    # Check that bytes were written correctly
    file_handles = mock_file_open.return_value
    file_handles.write.assert_any_call(b"fake_pdf_bytes_1")
    file_handles.write.assert_any_call(b"fake_pdf_bytes_2")

@patch("backend.app.services.classification_services.save_generated_pdfs")
@patch("backend.app.services.classification_services.backup_source_files")
@patch("backend.app.services.classification_services.extract_and_merge_pages")
@patch("backend.app.services.classification_services.get_archive_path")
@patch("backend.app.services.classification_services.ArchiveFileManager.parse_name_to_file_manager")
@patch("backend.app.services.classification_services.precheck_classification")
def test_classify_success(mock_precheck, mock_parse_name, mock_get_archive, mock_extract, mock_backup, mock_save, mock_session, base_job):
    import os
    
    # Arrange
    mock_get_archive.return_value = "/mock/archive"
    mock_parse_name.return_value = "Test_Piece"
    mock_extract.return_value = {"Flauta_1.pdf": b"pdfbytes"}
    
    # Act
    result = classify(mock_session, base_job)

    # Assert
    assert result is True
    mock_precheck.assert_called_once_with(mock_session, base_job)
    
    expected_scores_path = os.path.join("/mock/archive", "Test_Piece", DIR_SCORES)
    mock_extract.assert_called_once_with(base_job.classifications, expected_scores_path)
    
    mock_backup.assert_called_once_with(mock_session, base_job.archive_id, base_job.piece_std_name, base_job.source_files)
    mock_save.assert_called_once_with(mock_session, base_job.archive_id, base_job.piece_std_name, {"Flauta_1.pdf": b"pdfbytes"})

@patch("backend.app.services.classification_services.restore_last_backup")
@patch("backend.app.services.classification_services.save_generated_pdfs")
@patch("backend.app.services.classification_services.backup_source_files")
@patch("backend.app.services.classification_services.extract_and_merge_pages")
@patch("backend.app.services.classification_services.get_archive_path")
@patch("backend.app.services.classification_services.ArchiveFileManager.parse_name_to_file_manager")
@patch("backend.app.services.classification_services.precheck_classification")
def test_classify_rollback_on_save_error(mock_precheck, mock_parse_name, mock_get_archive, mock_extract, mock_backup, mock_save, mock_restore, mock_session, base_job):
    # Arrange
    mock_get_archive.return_value = "/mock/archive"
    mock_parse_name.return_value = "Test_Piece"
    mock_extract.return_value = {"Flauta_1.pdf": b"pdfbytes"}
    
    # Simulate an error during file save
    mock_save.side_effect = Exception("Disk Full")
    
    # Act & Assert exception propagates
    with pytest.raises(Exception, match="Disk Full"):
        classify(mock_session, base_job)
        
    # Assert rollback was triggered
    mock_save.assert_called_once()
    mock_restore.assert_called_once_with(mock_session, base_job.archive_id, base_job.piece_std_name)


