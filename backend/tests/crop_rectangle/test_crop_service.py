import fitz
import cv2
import pytest
import numpy as np
from unittest.mock import patch

from backend.app.services.pdf_modifiers.crop import (
    crop_page_from_corners,
    _extract_and_warp_rect,
)

def create_dummy_pdf_bytes() -> bytes:
    doc = fitz.open()
    page = doc.new_page(width=500, height=500)
    page.draw_rect(fitz.Rect(10, 10, 490, 490), color=(1, 0, 0), fill=(0, 1, 0))
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def get_dummy_pixmap() -> fitz.Pixmap:
    doc = fitz.open("pdf", create_dummy_pdf_bytes())
    pixmap = doc[0].get_pixmap()
    doc.close()
    return pixmap

def test_extract_and_warp_rect_success():
    pixmap = get_dummy_pixmap()
    corners = [(10.0, 10.0), (100.0, 10.0), (100.0, 100.0), (10.0, 100.0)]
    
    jpg_bytes, width, height = _extract_and_warp_rect(pixmap, corners, scale=1.0)
    
    assert isinstance(jpg_bytes, bytes)
    assert len(jpg_bytes) > 0
    assert width == 90
    assert height == 90

@patch("cv2.imencode")
def test_extract_and_warp_rect_encoding_failure(mock_imencode):
    mock_imencode.return_value = (False, None)
    pixmap = get_dummy_pixmap()
    corners = [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0)]
    
    with pytest.raises(ValueError, match="Image encoding failed."):
        _extract_and_warp_rect(pixmap, corners)

def test_extract_and_warp_rect_invalid_corners():
    pixmap = get_dummy_pixmap()
    # Providing fewer than 4 corners will cause an IndexError/ValueError in opencv math
    invalid_corners = [(0.0, 0.0), (50.0, 0.0)]
    
    with pytest.raises((IndexError, cv2.error)):
        _extract_and_warp_rect(pixmap, invalid_corners)

def test_crop_page_from_corners_success_landscape():
    pdf_bytes = create_dummy_pdf_bytes()
    corners = [(50.0, 50.0), (200.0, 50.0), (200.0, 150.0), (50.0, 150.0)]
    
    result_bytes = crop_page_from_corners(pdf_bytes, corners, page_number=0, landscape=True)
    
    assert isinstance(result_bytes, bytes)
    doc = fitz.open("pdf", result_bytes)
    assert doc.page_count == 1
    page = doc[0]
    # Landscape A4 size
    assert int(page.rect.width) == 842
    assert int(page.rect.height) == 595
    doc.close()

def test_crop_page_from_corners_success_portrait():
    pdf_bytes = create_dummy_pdf_bytes()
    corners = [(50.0, 50.0), (200.0, 50.0), (200.0, 150.0), (50.0, 150.0)]
    
    result_bytes = crop_page_from_corners(pdf_bytes, corners, page_number=0, landscape=False)
    
    doc = fitz.open("pdf", result_bytes)
    page = doc[0]
    # Portrait A4 size
    assert int(page.rect.width) == 595
    assert int(page.rect.height) == 842
    doc.close()

def test_crop_page_from_corners_invalid_pdf():
    garbage_bytes = b"Not a real PDF file"
    corners = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    
    with pytest.raises(fitz.FileDataError):
        crop_page_from_corners(garbage_bytes, corners)

def test_crop_page_from_corners_invalid_page_number():
    pdf_bytes = create_dummy_pdf_bytes()
    corners = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    
    with pytest.raises(IndexError):
        # The dummy PDF only has 1 page (index 0)
        crop_page_from_corners(pdf_bytes, corners, page_number=5)