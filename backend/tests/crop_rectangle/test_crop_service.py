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
    doc = fitz.open("pdf", pdf_bytes)
    page = doc[0]
    corners = [(0.1, 0.1), (0.4, 0.1), (0.4, 0.3), (0.1, 0.3)]
    
    result_page = crop_page_from_corners(page, corners, landscape=True)
    
    assert isinstance(result_page, fitz.Page)
    # Landscape A4 size
    assert int(result_page.rect.width) == 842
    assert int(result_page.rect.height) == 595
    doc.close()
    result_page.parent.close()

def test_crop_page_from_corners_success_portrait():
    pdf_bytes = create_dummy_pdf_bytes()
    doc = fitz.open("pdf", pdf_bytes)
    page = doc[0]
    corners = [(0.1, 0.1), (0.4, 0.1), (0.4, 0.3), (0.1, 0.3)]
    
    result_page = crop_page_from_corners(page, corners, landscape=False)
    
    assert isinstance(result_page, fitz.Page)
    # Portrait A4 size
    assert int(result_page.rect.width) == 595
    assert int(result_page.rect.height) == 842
    doc.close()
    result_page.parent.close()