import io
import os
import sys
from unittest.mock import patch, MagicMock
import pytest
import rarfile

from backend.app.services.massive_import.file_decompressor.strategies.rar_extractor import RarExtractor, get_unrar_path

@pytest.fixture
def mock_rarfile_class():
    with patch('backend.app.services.massive_import.file_decompressor.strategies.rar_extractor.rarfile.RarFile') as mock_class:
        yield mock_class

def test_extract_items_rar(mock_rarfile_class):
    mock_rar_instance = MagicMock()
    mock_rarfile_class.return_value.__enter__.return_value = mock_rar_instance
    
    # Create mock infos
    info1 = MagicMock(spec=rarfile.RarInfo)
    info1.filename = "score_1.pdf"
    info1.isdir.return_value = False
    
    info2 = MagicMock(spec=rarfile.RarInfo)
    info2.filename = "folder/score_2.pdf"
    info2.isdir.return_value = False
    
    info3 = MagicMock(spec=rarfile.RarInfo)
    info3.filename = "folder"
    info3.isdir.return_value = True
    
    mock_rar_instance.infolist.return_value = [info1, info2, info3]
    
    def mock_read(info):
        if info == info1:
            return b"content1"
        if info == info2:
            return b"content2"
        return b""
        
    mock_rar_instance.read.side_effect = mock_read
    
    extractor = RarExtractor()
    dummy_buffer = io.BytesIO(b"dummy_rar_data")
    
    results = list(extractor.extract_items(dummy_buffer))
    
    assert len(results) == 2
    assert ("score_1.pdf", b"content1") in results
    assert ("score_2.pdf", b"content2") in results

def test_get_unrar_path_env_var():
    with patch.dict(os.environ, {"UNRAR_PATH": "/mock/unrar"}):
        with patch('os.path.exists', return_value=True):
            assert get_unrar_path() == "/mock/unrar"

def test_get_unrar_path_shutil():
    with patch.dict(os.environ, {}, clear=True):
        with patch('sys.frozen', False, create=True):
            with patch('shutil.which', return_value="/usr/bin/unrar"):
                assert get_unrar_path() == "/usr/bin/unrar"


def test_extract_all_rar_preserves_directory_structure(mock_rarfile_class):
    mock_rar_instance = MagicMock()
    mock_rarfile_class.return_value.__enter__.return_value = mock_rar_instance

    info1 = MagicMock(spec=rarfile.RarInfo)
    info1.filename = "score_1.pdf"
    info1.isdir.return_value = False

    info2 = MagicMock(spec=rarfile.RarInfo)
    info2.filename = "folder/score_2.pdf"
    info2.isdir.return_value = False

    info3 = MagicMock(spec=rarfile.RarInfo)
    info3.filename = "folder/sub/score_3.pdf"
    info3.isdir.return_value = False

    info4 = MagicMock(spec=rarfile.RarInfo)
    info4.filename = "folder"
    info4.isdir.return_value = True

    mock_rar_instance.infolist.return_value = [info1, info2, info3, info4]

    def mock_read(info):
        if info == info1:
            return b"content1"
        if info == info2:
            return b"content2"
        if info == info3:
            return b"content3"
        return b""

    mock_rar_instance.read.side_effect = mock_read

    extractor = RarExtractor()
    dummy_buffer = io.BytesIO(b"dummy_rar_data")

    result = extractor.extract_all(dummy_buffer)

    assert result == {
        "score_1.pdf": b"content1",
        "folder/score_2.pdf": b"content2",
        "folder/sub/score_3.pdf": b"content3",
    }
    assert "folder" not in result
    assert mock_rar_instance.read.call_count == 3


def test_extract_all_rar_empty_archive_returns_empty_dict(mock_rarfile_class):
    mock_rar_instance = MagicMock()
    mock_rarfile_class.return_value.__enter__.return_value = mock_rar_instance
    mock_rar_instance.infolist.return_value = []

    extractor = RarExtractor()
    dummy_buffer = io.BytesIO(b"dummy_rar_data")

    result = extractor.extract_all(dummy_buffer)

    assert result == {}
    mock_rar_instance.read.assert_not_called()


def test_extract_all_ignores_non_rarinfo_entries(mock_rarfile_class):
    mock_rar_instance = MagicMock()
    mock_rarfile_class.return_value.__enter__.return_value = mock_rar_instance

    valid_info = MagicMock(spec=rarfile.RarInfo)
    valid_info.filename = "folder/score_2.pdf"
    valid_info.isdir.return_value = False

    invalid_info = object()

    mock_rar_instance.infolist.return_value = [invalid_info, valid_info]
    mock_rar_instance.read.return_value = b"content2"

    extractor = RarExtractor()
    dummy_buffer = io.BytesIO(b"dummy_rar_data")

    result = extractor.extract_all(dummy_buffer)

    assert result == {"folder/score_2.pdf": b"content2"}
    mock_rar_instance.read.assert_called_once_with(valid_info)