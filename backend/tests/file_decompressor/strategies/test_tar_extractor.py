import io
import tarfile
import pytest
from backend.app.massive_import.file_decompressor.strategies.tar_extractor import TarExtractor

def create_mock_tar(file_structure: dict) -> io.BytesIO:
    """
    Helper function to create an in-memory TAR file.
    Keys are file paths, values are byte contents.
    If a value is None, it is treated as a directory.
    """
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
        for filepath, content in file_structure.items():
            if content is None:
                # Directory
                tinfo = tarfile.TarInfo(filepath.rstrip('/'))
                tinfo.type = tarfile.DIRTYPE
                tar.addfile(tinfo)
            else:
                tinfo = tarfile.TarInfo(filepath)
                tinfo.size = len(content)
                tar.addfile(tinfo, io.BytesIO(content))
    tar_buffer.seek(0)
    return tar_buffer

def test_extract_items_with_flat_files():
    mock_tar = create_mock_tar({
        "score_1.pdf": b"dummy_pdf_content",
        "notes.txt": b"12345"
    })
    
    extractor = TarExtractor()
    results = list(extractor.extract_items(mock_tar))
    
    assert len(results) == 2
    assert ("score_1.pdf", b"dummy_pdf_content") in results
    assert ("notes.txt", b"12345") in results

def test_extract_items_with_nested_files():
    mock_tar = create_mock_tar({
        "folder_a/score_2.pdf": b"nested_pdf_content",
        "folder_b/subfolder/image.png": b"image_content"
    })
    
    extractor = TarExtractor()
    results = list(extractor.extract_items(mock_tar))
    
    assert len(results) == 2
    assert ("score_2.pdf", b"nested_pdf_content") in results
    assert ("image.png", b"image_content") in results

def test_extract_items_ignores_directories():
    mock_tar = create_mock_tar({
        "empty_folder": None,
        "folder_with_file/": None,
        "folder_with_file/file.txt": b"content"
    })
    
    extractor = TarExtractor()
    results = list(extractor.extract_items(mock_tar))
    
    assert len(results) == 1
    assert results[0] == ("file.txt", b"content")

def test_extract_items_empty_tar():
    mock_tar = create_mock_tar({})
    
    extractor = TarExtractor()
    results = list(extractor.extract_items(mock_tar))
    
    assert len(results) == 0
