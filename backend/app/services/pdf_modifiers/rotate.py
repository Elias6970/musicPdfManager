import fitz

def rotate_page(page: fitz.Page, degrees: int):
    """
    Rotates a specific page of a PDF by a given number of degrees.
    Note: PDF page rotation must typically be a multiple of 90 degrees (90, 180, 270).

    :param page: The fitz.Page object to rotate.
    :param degrees: The angle to rotate the page (added to current rotation).
    """

    # Calculate the new absolute rotation
    # PyMuPDF expects the rotation to be one of 0, 90, 180, 270
    new_rotation = (page.rotation + degrees) % 360
    page.set_rotation(new_rotation)