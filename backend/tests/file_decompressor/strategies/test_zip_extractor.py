import io
import zipfile
import pytest
from backend.app.massive_import.file_decompressor.strategies.zip_extractor import ZipExtractor

def create_mock_zip(file_structure: dict) -> io.BytesIO:
    """
    Helper function to create an in-memory ZIP file.
    Keys are file paths, values are byte contents.
    If a value is None, it is treated as a directory.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filepath, content in file_structure.items():
            if content is None:
                # Create a directory entry
                zinfo = zipfile.ZipInfo(filepath.rstrip('/') + '/')
                zip_file.writestr(zinfo, b'')
            else:
                zip_file.writestr(filepath, content)
    zip_buffer.seek(0)
    return zip_buffer

def test_extract_items_with_flat_files():
    mock_zip = create_mock_zip({
        "score_1.pdf": b"dummy_pdf_content",
        "notes.txt": b"12345"
    })
    
    extractor = ZipExtractor()
    results = list(extractor.extract_items(mock_zip))
    
    assert len(results) == 2
    assert ("score_1.pdf", b"dummy_pdf_content") in results
    assert ("notes.txt", b"12345") in results

def test_extract_items_with_nested_files():
    mock_zip = create_mock_zip({
        "folder_a/score_2.pdf": b"nested_pdf_content",
        "folder_b/subfolder/image.png": b"image_content"
    })
    
    extractor = ZipExtractor()
    results = list(extractor.extract_items(mock_zip))
    
    assert len(results) == 2
    # Should strip directory paths and yield only the base name
    assert ("score_2.pdf", b"nested_pdf_content") in results
    assert ("image.png", b"image_content") in results

def test_extract_items_ignores_directories():
    mock_zip = create_mock_zip({
        "empty_folder": None,
        "folder_with_file": None,
        "folder_with_file/file.txt": b"content"
    })
    
    extractor = ZipExtractor()
    results = list(extractor.extract_items(mock_zip))
    
    assert len(results) == 1
    # Only the file should be yielded, directories are skipped
    assert results[0] == ("file.txt", b"content")

def test_extract_items_empty_zip():
    mock_zip = create_mock_zip({})
    
    extractor = ZipExtractor()
    results = list(extractor.extract_items(mock_zip))
    
    assert len(results) == 0

def test_extract_all_preserves_directory_structure():
    mock_zip = create_mock_zip({
        "score_1.pdf": b"content1",
        "folder/score_2.pdf": b"content2",
        "folder/sub/score_3.pdf": b"content3",
        "folder/": None,
    })

    extractor = ZipExtractor()
    result = extractor.extract_all(mock_zip)

    assert result == {
        "score_1.pdf": b"content1",
        "folder/score_2.pdf": b"content2",
        "folder/sub/score_3.pdf": b"content3",
    }
    assert "folder/" not in result


def test_extract_all_empty_zip_returns_empty_dict():
    mock_zip = create_mock_zip({})

    extractor = ZipExtractor()
    result = extractor.extract_all(mock_zip)

    assert result == {}


def test_extract_all_ignores_directory_only_archive():
    mock_zip = create_mock_zip({
        "empty_folder/": None,
        "nested/": None,
        "nested/sub/": None,
    })

    extractor = ZipExtractor()
    result = extractor.extract_all(mock_zip)

    assert result == {}


def test_extract_all_with_mixed_entries_includes_only_files():
    mock_zip = create_mock_zip({
        "a/file1.txt": b"f1",
        "a/b/": None,
        "a/b/file2.pdf": b"f2",
        "root.png": b"img",
    })

    extractor = ZipExtractor()
    result = extractor.extract_all(mock_zip)

    assert result == {
        "a/file1.txt": b"f1",
        "a/b/file2.pdf": b"f2",
        "root.png": b"img",
    }


def test_extract_all_keeps_same_basename_in_different_directories():
    mock_zip = create_mock_zip({
        "set_a/score.pdf": b"a",
        "set_b/score.pdf": b"b",
    })

    extractor = ZipExtractor()
    result = extractor.extract_all(mock_zip)

    assert result == {
        "set_a/score.pdf": b"a",
        "set_b/score.pdf": b"b",
    }