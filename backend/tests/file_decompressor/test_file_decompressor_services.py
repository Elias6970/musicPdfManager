import io
import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.massive_import.file_decompressor.file_decompressor_services import (
    get_strategy,
    extract_nested_archives_in_memory,
    STRATEGIES
)

def test_get_strategy():
    # Valid extensions
    assert get_strategy("test.zip") == STRATEGIES['.zip']
    assert get_strategy("test.RAR") == STRATEGIES['.rar']
    assert get_strategy("file.tar") == STRATEGIES['.tar']
    assert get_strategy("file.tar.gz") == STRATEGIES['.tar.gz']
    assert get_strategy("file.tgz") == STRATEGIES['.tgz']
    
    # Invalid extensions
    assert get_strategy("test.txt") is None
    assert get_strategy("no_extension") is None

def test_extract_not_archive_bytesio():
    data = io.BytesIO(b"dummy content")
    results = list(extract_nested_archives_in_memory(data, "test.txt"))
    assert len(results) == 1
    assert results[0] == ("test.txt", b"dummy content")

def test_extract_not_archive_file_path(tmp_path):
    filepath = tmp_path / "test.txt"
    filepath.write_bytes(b"dummy file content")
    
    results = list(extract_nested_archives_in_memory(str(filepath), str(filepath)))
    assert len(results) == 1
    assert results[0] == (str(filepath), b"dummy file content")

@patch('backend.app.massive_import.file_decompressor.file_decompressor_services.get_strategy')
def test_extract_archive_success(mock_get_strategy):
    mock_strategy = MagicMock()
    mock_strategy.extract_items.return_value = [("file1.txt", b"content1"), ("file2.txt", b"content2")]
    
    # Return mock_strategy only for .zip, None otherwise (to stop recursion)
    mock_get_strategy.side_effect = lambda filename: mock_strategy if filename.endswith('.zip') else None

    data = io.BytesIO(b"dummy zip data")
    results = list(extract_nested_archives_in_memory(data, "test.zip"))
    
    assert len(results) == 2
    assert ("file1.txt", b"content1") in results
    assert ("file2.txt", b"content2") in results

@patch('backend.app.massive_import.file_decompressor.file_decompressor_services.get_strategy')
def test_extract_archive_from_file_path(mock_get_strategy, tmp_path):
    mock_strategy = MagicMock()
    mock_strategy.extract_items.return_value = [("file.txt", b"content")]
    mock_get_strategy.side_effect = lambda filename: mock_strategy if filename.endswith('.zip') else None

    filepath = tmp_path / "test.zip"
    filepath.write_bytes(b"dummy zip data on disk")

    results = list(extract_nested_archives_in_memory(str(filepath), str(filepath)))
    
    assert len(results) == 1
    assert results[0] == ("file.txt", b"content")
    mock_strategy.extract_items.assert_called_once()
    
    # Verify it was converted to BytesIO
    args, _ = mock_strategy.extract_items.call_args
    assert isinstance(args[0], io.BytesIO)
    assert args[0].getvalue() == b"dummy zip data on disk"
    
@patch('backend.app.massive_import.file_decompressor.file_decompressor_services.get_strategy')
def test_extract_nested_archive(mock_get_strategy):
    outer_strategy = MagicMock()
    inner_strategy = MagicMock()
    
    outer_strategy.extract_items.return_value = [("inner.rar", b"inner rar data"), ("normal.txt", b"normal")]
    inner_strategy.extract_items.return_value = [("deep.pdf", b"deep")]
    
    def strategy_side_effect(filename):
        if filename == "outer.zip": return outer_strategy
        if filename == "inner.rar": return inner_strategy
        return None
        
    mock_get_strategy.side_effect = strategy_side_effect
    
    data = io.BytesIO(b"dummy outer zip")
    results = list(extract_nested_archives_in_memory(data, "outer.zip"))
    
    assert len(results) == 2
    # Since deep.pdf comes from inner.rar which in turn is from outer.zip
    assert ("deep.pdf", b"deep") in results
    assert ("normal.txt", b"normal") in results
    
@patch('backend.app.massive_import.file_decompressor.file_decompressor_services.get_strategy')
def test_extract_nested_archive_max_depth(mock_get_strategy, capsys):
    mock_strategy = MagicMock()
    # Constantly yields another zip
    mock_strategy.extract_items.return_value = [("next.zip", b"next data")]
    mock_get_strategy.return_value = mock_strategy
    
    data = io.BytesIO(b"data")
    # Setting max_depth to 1 so that it hits the failsafe quickly
    results = list(extract_nested_archives_in_memory(data, "start.zip", current_depth=0, max_depth=1))
    
    assert len(results) == 1
    assert results[0] == ("next.zip", b"next data")
    
    captured = capsys.readouterr()
    assert "Warning: Max depth (1) reached at 'next.zip'" in captured.out

@patch('backend.app.massive_import.file_decompressor.file_decompressor_services.get_strategy')
def test_extract_exception_handling(mock_get_strategy, capsys):
    mock_strategy = MagicMock()
    mock_strategy.extract_items.side_effect = Exception("Corrupt archive")
    mock_get_strategy.return_value = mock_strategy
    
    data = io.BytesIO(b"bad data")
    results = list(extract_nested_archives_in_memory(data, "bad.zip"))
    
    assert len(results) == 0
    captured = capsys.readouterr()
    assert "Warning: Failed to process archive 'bad.zip': Corrupt archive" in captured.out
