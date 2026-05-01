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
