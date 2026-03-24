import os
import pytest
from pathlib import Path
from unittest.mock import patch

from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.constants.constants import DIR_SCORES, DIR_EXTRAS, HYPHEN


@pytest.fixture
def manager(tmp_path):
    return ArchiveFileManager(str(tmp_path))

@pytest.mark.parametrize(
    "input_name, expected",
    [
        ("1-café<|>*:?", f"1{HYPHEN}CAFE"),
        ("2 - múSîc/\\\"", f"2{HYPHEN}MUSIC"),
        ("sïmplé", "SIMPLE"),
        ("3- already-clean", f"3{HYPHEN}ALREADY-CLEAN"),
        ("no-number-hyphen", f"NO{HYPHEN}NUMBER-HYPHEN"),
        ("  4   -   spaces  ", f"4{HYPHEN}SPACES"),
        (" 5- emojis 😊😊😊", "5-EMOJIS"),
        ("8--rare chars 𢎐𢎐", "8--RARE CHARS"),
    ]
)
def test_parse_name_to_file_manager(manager, input_name, expected):
    assert manager.parse_name_to_file_manager(input_name) == expected

@patch('backend.app.files_management.archive_file_manager.File.is_pdf')
def test_copy_files_in_archive(mock_is_pdf, manager, tmp_path):
    mock_is_pdf.side_effect = lambda path: str(path).endswith('.pdf')
    piece_path = "1-TEST"
    manager.make_dir(piece_path)
    
    score_file = tmp_path / "test.pdf"
    extra_file = tmp_path / "test.txt"
    score_file.write_text("pdf")
    extra_file.write_text("txt")
    
    result = manager.copy_files_in_archive(piece_path, [str(score_file), str(extra_file)])
    assert result is True
    assert os.path.exists(os.path.join(manager.archive_path, piece_path, DIR_SCORES, "test.pdf"))
    assert os.path.exists(os.path.join(manager.archive_path, piece_path, DIR_EXTRAS, "test.txt"))

@patch('backend.app.files_management.archive_file_manager.File.is_pdf')
def test_copy_files_in_archive_removes_uuid_prefix(mock_is_pdf, manager, tmp_path):
    mock_is_pdf.side_effect = lambda path: str(path).endswith('.pdf')
    piece_path = "1-TEST"
    manager.make_dir(piece_path)
    
    score_file = tmp_path / "624af065-2681-464c-907e-a951304aff9e_my_score.pdf"
    extra_file = tmp_path / "someuuid123_my_extra_file.txt"
    score_file.write_text("pdf content")
    extra_file.write_text("txt content")
    
    result = manager.copy_files_in_archive(piece_path, [str(score_file), str(extra_file)])
    assert result is True
    assert os.path.exists(os.path.join(manager.archive_path, piece_path, DIR_SCORES, "my_score.pdf"))
    assert os.path.exists(os.path.join(manager.archive_path, piece_path, DIR_EXTRAS, "my_extra_file.txt"))

def test_move_files(manager, tmp_path):
    src = tmp_path / "source.txt"
    src.write_text("content")
    
    dest_path = manager.move_files(str(src), "dest.txt")
    assert dest_path == str(tmp_path / "dest.txt")
    assert os.path.exists(dest_path)
    assert not os.path.exists(src)

def test_get_file_names(manager, tmp_path):
    d = tmp_path / "folder"
    d.mkdir()
    (d / "file1.txt").write_text("")
    (d / ".DS_Store").write_text("")
    
    names = manager._get_file_names(str(d))
    assert "file1.txt" in names
    assert ".DS_Store" not in names

def test_get_scores_and_extras(manager):
    piece = "1-TEST"
    manager.make_dir(piece)
    
    score_path = os.path.join(manager.archive_path, piece, DIR_SCORES, "score.pdf")
    extra_path = os.path.join(manager.archive_path, piece, DIR_EXTRAS, "extra.txt")
    Path(score_path).write_text("")
    Path(extra_path).write_text("")
    
    assert "score.pdf" in manager.get_scores(os.path.join(manager.archive_path, piece))
    assert "extra.txt" in manager.get_extras(os.path.join(manager.archive_path, piece))

def test_make_dir(manager):
    manager.make_dir("new_piece")
    assert os.path.exists(os.path.join(manager.archive_path, "new_piece", DIR_SCORES))
    assert os.path.exists(os.path.join(manager.archive_path, "new_piece", DIR_EXTRAS))

def test_delete_piece(manager):
    manager.make_dir("to_delete")
    manager.delete_piece("to_delete")
    assert not os.path.exists(os.path.join(manager.archive_path, "to_delete"))

def test_change_piece_dir_name(manager):
    manager.make_dir("old_name")
    manager.change_piece_dir_name("old_name", "new_name")
    assert not os.path.exists(os.path.join(manager.archive_path, "old_name"))
    assert os.path.exists(os.path.join(manager.archive_path, "new_name"))

def test_get_piece_path(manager):
    manager.make_dir("101-TEST_PIECE")
    path = manager.get_piece_path("101")
    assert path == os.path.join(manager.archive_path, "101-TEST_PIECE")
    
    assert manager.get_piece_path("999") == ""

def test_md5_hash_and_are_the_same(manager, tmp_path):
    f1 = tmp_path / "f1.txt"
    f2 = tmp_path / "f2.txt"
    f3 = tmp_path / "f3.txt"
    
    f1.write_text("Hello")
    f2.write_text("Hello")
    f3.write_text("World")
    
    assert manager.are_the_same(str(f1), str(f2)) is True
    assert manager.are_the_same(str(f1), str(f3)) is False

def test_sanitize_archive_folder_names(manager):
    bad_name = "1-bád/name" 
    manager.make_dir(bad_name)
    manager.sanitize_archive_folder_names()

    expected_good = f"1{HYPHEN}BADNAME"
    assert os.path.exists(os.path.join(manager.archive_path, expected_good))

def test_move_uppercase_pdfs_to_scores(manager):
    piece = "1-TEST"
    manager.make_dir(piece)
    
    pdf_path = Path(manager.archive_path) / piece / DIR_EXTRAS / "UPPER.PDF"
    pdf_path.write_text("dat")
    
    manager.move_uppercase_pdfs_to_scores()
    
    expected_new = Path(manager.archive_path) / piece / DIR_SCORES / "UPPER.pdf"
    assert expected_new.exists()
    assert not pdf_path.exists()

def test_path_exists(manager, tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("")
    assert manager.path_exists(str(f)) is True
    assert manager.path_exists(str(tmp_path / "missing.txt")) is False

def test_extract_original_filename():
    assert ArchiveFileManager.extract_original_filename("123e4567-e89b_myscore.pdf") == "myscore.pdf"
    assert ArchiveFileManager.extract_original_filename("/temp/folder/123e4567-e89b_myscore.pdf") == "myscore.pdf"
    assert ArchiveFileManager.extract_original_filename("123e4567-e89b_my_original_score_file.pdf") == "my_original_score_file.pdf"
    assert ArchiveFileManager.extract_original_filename("myscore.pdf") == "myscore.pdf"

def test_format_temp_filename():
    assert ArchiveFileManager.format_temp_filename("123e4567-e89b", "myscore.pdf") == "123e4567-e89b_myscore.pdf"
    assert ArchiveFileManager.format_temp_filename("123e4567-e89b", "/user/local/downloads/myscore.pdf") == "123e4567-e89b_myscore.pdf"
