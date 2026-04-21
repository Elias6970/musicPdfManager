import fitz

def rotate_page(pdf_bytes: bytes, degrees: int, page_number: int = 0) -> bytes:
    """
    Rotates a specific page of a PDF by a given number of degrees and returns the updated PDF bytes.
    Note: PDF page rotation must typically be a multiple of 90 degrees (90, 180, 270).

    :param pdf_bytes: The original PDF file in bytes.
    :param degrees: The angle to rotate the page (added to current rotation).
    :param page_number: The 0-based index of the page to rotate.
    :return: The bytes of the modified PDF.
    """
    # Open the PDF from memory
    doc = fitz.open("pdf", pdf_bytes)
    
    try:
        page = doc[page_number]
        # Calculate the new absolute rotation
        # PyMuPDF expects the rotation to be one of 0, 90, 180, 270
        new_rotation = (page.rotation + degrees) % 360
        page.set_rotation(new_rotation)
        
        # Save the updated document back to bytes
        out_bytes = doc.write()
    finally:
        # Prevent memory leaks by properly closing the document
        doc.close()
        
    return out_bytes
