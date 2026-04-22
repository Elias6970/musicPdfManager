import fitz
import cv2
import numpy as np
from typing import List, Tuple

RENDER_DPI = 300

def _extract_and_warp_rect(pixmap: fitz.Pixmap, corners: List[Tuple[float, float]], scale: float = 1.0) -> tuple[bytes, int, int]:
    """
    Extracts a polygon (4 points) from a fitz.Pixmap and warps it to be an upright rectangle.
    Can raise ValueError if encoding fails.

    :param pixmap: fitz.Pixmap (input image)
    :param corners: List of 4 [x, y] coordinates
    :param scale: scale factor applied when rendering the pixmap (dpi/72)
    :return: (Warped image as JPG bytes, warped width, warped height)
    """
    # Convert fitz.Pixmap to NumPy array (RGBA or grayscale)
    img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.h, pixmap.w, pixmap.n)
    if pixmap.n == 4:
        # Convert RGBA to BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        
    # Ensure points are float32 and apply zoom scale
    rect = np.array(corners, dtype="float32") * scale

    # Compute the new width and height of the upright rectangle
    width_a = np.linalg.norm(rect[0] - rect[1])
    width_b = np.linalg.norm(rect[2] - rect[3])
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(rect[0] - rect[3])
    height_b = np.linalg.norm(rect[1] - rect[2])
    max_height = int(max(height_a, height_b))

    # Define destination points for warping (upright rectangle)
    dst_rect = np.array([
        [0, 0], [max_width - 1, 0],
        [max_width - 1, max_height - 1], [0, max_height - 1]
    ], dtype="float32")

    # Compute perspective transformation matrix and apply warp
    matrix = cv2.getPerspectiveTransform(rect, dst_rect)
    warped_img = cv2.warpPerspective(img, matrix, (max_width, max_height))
    
    # Encode the new image back to JPG
    rgb_image = cv2.cvtColor(warped_img, cv2.COLOR_BGR2RGB)
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
    success, encoded_image = cv2.imencode('.jpg', rgb_image, encode_params)
    if not success:
        raise ValueError("Image encoding failed.")

    return encoded_image.tobytes(), max_width, max_height


def crop_page_from_corners(page: fitz.Page, corners: List[Tuple[float, float]], landscape: bool = True) -> fitz.Page:
    """
    Takes a specific page, crops out a specific polygon (corners),
    and returns a new single-page Document containing the extracted crop warped upright.
     :param page: The fitz.Page object to crop.
     :param corners: List of 4 [x, y] coordinates representing the corners of the polygon to crop. Order should be: Top-Left, Top-Right, Bottom-Right, Bottom-Left
     :param landscape: Whether the output page should be in landscape orientation (default True). If False, output will be portrait.
     :return: A new fitz.Page containing the cropped and warped page.
    """
    if landscape:
        a4_width, a4_height = 842, 595 # A4 size in points (landscape)
    else:
        a4_width, a4_height = 595, 842 # A4 size in points (portrait)

    # Render the page at higher DPI
    zoom = RENDER_DPI / 72  
    render_matrix = fitz.Matrix(zoom, zoom)
    original_pixmap = page.get_pixmap(matrix=render_matrix, alpha=False)


    # Extract and warp with OpenCV
    jpg_data, img_width, img_height = _extract_and_warp_rect(original_pixmap, corners, scale=zoom)

    # Scale the warped image while maintaining aspect ratio to fit within an A4 page, minus a 10pt margin
    scale_factor = min(a4_width / img_width, a4_height / img_height)
    new_width = (img_width * scale_factor) - 10
    new_height = (img_height * scale_factor) - 10

    # Center image
    x_offset = (a4_width - new_width) / 2
    y_offset = (a4_height - new_height) / 2

    # Construct the final out-PDF
    out_pdf = fitz.open()
    out_page = out_pdf.new_page(width=a4_width, height=a4_height)
    out_page.insert_image(
        fitz.Rect(x_offset, y_offset, x_offset + new_width, y_offset + new_height),
        stream=jpg_data
    )
    
    return out_page
