from unittest.mock import MagicMock
import pytest

from backend.app.services.preview_services import generate_preview_bytes
from backend.app.models.preview import PreviewRequest


@pytest.fixture
def mock_request():
    return PreviewRequest(
        archive_id=1,
        piece_std_name="test_piece",
        file="violin_1.pdf",
        page_number=0,
        dpi=150
    )


@pytest.fixture
def mock_dependencies(monkeypatch):
    monkeypatch.setattr("backend.app.services.preview_services.get_archive_path", lambda s, a: "/mocked/archive")
    monkeypatch.setattr(
        "backend.app.services.preview_services.ArchiveFileManager.parse_name_to_file_manager",
        lambda n: "test_piece_parsed"
    )
    mock_exists = MagicMock(return_value=True)
    monkeypatch.setattr("os.path.exists", mock_exists)
    return mock_exists


@pytest.fixture
def mock_fitz_doc(monkeypatch):
    mock_doc = MagicMock()
    mock_doc.page_count = 5
    mock_page = MagicMock()
    mock_pix = MagicMock()
    mock_pix.tobytes.return_value = b"mocked_image_bytes"
    mock_page.get_pixmap.return_value = mock_pix
    mock_doc.load_page.return_value = mock_page
    
    # Mock fitz.open
    mock_fitz_open = MagicMock(return_value=mock_doc)
    monkeypatch.setattr("backend.app.services.preview_services.fitz.open", mock_fitz_open)
    return mock_fitz_open, mock_doc


def test_generate_preview_bytes_success(mock_dependencies, mock_fitz_doc, mock_request):
    mock_fitz_open, mock_doc = mock_fitz_doc
    mock_session = MagicMock()

    img_bytes, total_pages = generate_preview_bytes(mock_session, mock_request)

    assert img_bytes == b"mocked_image_bytes"
    assert total_pages == 5
    mock_doc.load_page.assert_called_once_with(0)
    mock_doc.close.assert_called_once()


def test_generate_preview_bytes_file_not_found(mock_dependencies, mock_request):
    mock_dependencies.return_value = False
    mock_session = MagicMock()

    with pytest.raises(FileNotFoundError, match="PDF file not found in the archive"):
        generate_preview_bytes(mock_session, mock_request)


def test_generate_preview_bytes_pdf_open_fails(mock_dependencies, monkeypatch, mock_request):
    mock_fitz_open = MagicMock(side_effect=Exception("Corrupted"))
    monkeypatch.setattr("backend.app.services.preview_services.fitz.open", mock_fitz_open)
    mock_session = MagicMock()

    with pytest.raises(ValueError, match="Could not open PDF file: Corrupted"):
        generate_preview_bytes(mock_session, mock_request)


def test_generate_preview_bytes_page_out_of_bounds_negative(mock_dependencies, mock_fitz_doc, mock_request):
    _, mock_doc = mock_fitz_doc
    mock_request.page_number = -1
    mock_session = MagicMock()

    with pytest.raises(IndexError, match="out of bounds"):
        generate_preview_bytes(mock_session, mock_request)
        
    mock_doc.close.assert_called_once()


def test_generate_preview_bytes_page_out_of_bounds_exceeds(mock_dependencies, mock_fitz_doc, mock_request):
    _, mock_doc = mock_fitz_doc
    mock_request.page_number = 5  # page_count is 5, so valid are 0-4
    mock_session = MagicMock()

    with pytest.raises(IndexError, match="out of bounds"):
        generate_preview_bytes(mock_session, mock_request)
        
    mock_doc.close.assert_called_once()


def test_generate_preview_bytes_render_fails(mock_dependencies, mock_fitz_doc, mock_request):
    _, mock_doc = mock_fitz_doc
    mock_doc.load_page.side_effect = Exception("Render crash")
    mock_session = MagicMock()

    with pytest.raises(RuntimeError, match="Error rendering PDF page: Render crash"):
        generate_preview_bytes(mock_session, mock_request)
        
    mock_doc.close.assert_called_once()
