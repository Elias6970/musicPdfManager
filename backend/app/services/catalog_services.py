import fitz
from typing import List
from sqlmodel import Session
from datetime import datetime

from backend.app.models.piece import Piece
from backend.app.crud.piece_crud import get_pieces
from backend.app.models.catalog_generation_config import CatalogGenerationConfigBase

def generate_pdf_catalog_for_archive(session:Session, config: CatalogGenerationConfigBase) -> bytes:
    pieces = get_pieces(session, config.archive_id)
    return generate_pdf_catalog(pieces, config)

def generate_pdf_catalog(pieces: List[Piece], config: CatalogGenerationConfigBase) -> bytes:
    """
    Generates a PDF containing a table of pieces sorted alphabetically by name.
    Args:
        pieces (List[Piece]): List of Piece objects to include in the catalog.
        config (CatalogGenerationConfigBase): Configuration for catalog generation, including language and number of blank rows.
    Returns:
        bytes: The generated PDF as a byte string.
    Raises:
        ValueError: If an unsupported language code is provided in the config.
    """
    doc = fitz.open()

    PAGE_WIDTH = 842   # A4 landscape width
    PAGE_HEIGHT = 595  # A4 landscape height
    MARGIN_LEFT = 50
    MARGIN_RIGHT = 50
    MARGIN_TOP = 30
    MARGIN_BOTTOM = 30
    LINE_HEIGHT = 16

    TEXT_FONT_SIZE = 12
    DATE_FONT_SIZE = 9
    HEADER_FONT_SIZE = 12
    PAGE_NUMBER_FONT_SIZE = 12

    # Vertical line X positions
    # Cols: Cod (40), Name (331 (to be centered)), Author (219), Type (remaining)
    v_lines = [
        MARGIN_LEFT, 
        MARGIN_LEFT + 40, 
        MARGIN_LEFT + 371, 
        MARGIN_LEFT + 590, 
        PAGE_WIDTH - MARGIN_RIGHT
    ]
    # Text X positions for each column
    col_x = [v_lines[0], v_lines[1], v_lines[2], v_lines[3]]
    padding = 5

    page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    y = MARGIN_TOP

    # Sort pieces alphabetically by name
    sorted_pieces = sorted(pieces, key=lambda p: (p.name or "").lower())
    current_date = datetime.now().strftime("%d/%m/%Y")

    if config.language == "en_US":
        headers = ["Code", "Name", "Author", "Type"]
    elif config.language == "ca_VA":
        headers = ["Codi", "Nom", "Autor", "Tipus"]
    elif config.language == "es_ES":
        headers = ["Cod", "Nombre", "Autor", "Tipo"]
    else:
        raise ValueError(f"Unsupported language code: {config.language}")

    def draw_headers(p, curr_y):
        # Draw top center date in italics ('heit')
        # We estimate ~60 points for the string width to center it roughly
        p.insert_text((PAGE_WIDTH / 2 - 30, curr_y), current_date, fontname="heit", fontsize=DATE_FONT_SIZE)
        curr_y += 15

        # Draw background rectangle for headers with gray fill
        rect = fitz.Rect(v_lines[0], curr_y, v_lines[-1], curr_y + LINE_HEIGHT)
        p.draw_rect(rect, color=(0, 0, 0), fill=(0.85, 0.85, 0.85))
        
        # Center the text baseline vertically inside the line height
        text_y = curr_y + 12
        for h, x in zip(headers, col_x):
            p.insert_text((x + padding, text_y), h, fontname="hebo", fontsize=HEADER_FONT_SIZE)
        
        curr_y += LINE_HEIGHT
        
        # Draw vertical lines for the header row
        for vx in v_lines:
            p.draw_line(fitz.Point(vx, curr_y - LINE_HEIGHT), fitz.Point(vx, curr_y))
            
        return curr_y

    y = draw_headers(page, y)

    for piece in sorted_pieces:
        # Check if we need to paginate (y exceeds bottom margin)
        if y > PAGE_HEIGHT - MARGIN_BOTTOM - LINE_HEIGHT:
            page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
            y = MARGIN_TOP
            y = draw_headers(page, y)

        cod_str = str(piece.cod)
        name_str = str(piece.name or "")
        author_str = getattr(getattr(piece, "author", None), "name", "") or ""
        type_str = getattr(getattr(piece, "type", None), "name", "") or ""

        # Limit lengths to fit columns properly in landscape
        name_str = (name_str[:60] + "..") if len(name_str) > 60 else name_str
        author_str = (author_str[:40] + "..") if len(author_str) > 40 else author_str
        type_str = (type_str[:25] + "..") if len(type_str) > 25 else type_str

        # Center the text baseline vertically inside the line height
        text_y = y + 12
        page.insert_text((col_x[0] + padding, text_y), cod_str, fontname="helv", fontsize=TEXT_FONT_SIZE)
        page.insert_text((col_x[1] + padding, text_y), name_str, fontname="helv", fontsize=TEXT_FONT_SIZE)
        page.insert_text((col_x[2] + padding, text_y), author_str, fontname="helv", fontsize=TEXT_FONT_SIZE)
        page.insert_text((col_x[3] + padding, text_y), type_str, fontname="helv", fontsize=TEXT_FONT_SIZE)

        y += LINE_HEIGHT

        # Draw bottom horizontal line for the row
        page.draw_line(fitz.Point(v_lines[0], y), fitz.Point(v_lines[-1], y))
        
        # Draw vertical lines for the row
        for vx in v_lines:
            page.draw_line(fitz.Point(vx, y - LINE_HEIGHT), fitz.Point(vx, y))

    # Add blank rows at the end
    for _ in range(config.blank_rows):
        # Check if we need to paginate for the blank row
        if y > PAGE_HEIGHT - MARGIN_BOTTOM - LINE_HEIGHT:
            page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
            y = MARGIN_TOP
            y = draw_headers(page, y)

        y += LINE_HEIGHT

        # Draw bottom horizontal line for the blank row
        page.draw_line(fitz.Point(v_lines[0], y), fitz.Point(v_lines[-1], y))
        
        # Draw vertical lines for the blank row
        for vx in v_lines:
            page.draw_line(fitz.Point(vx, y - LINE_HEIGHT), fitz.Point(vx, y))

    # Add page numbers at the bottom right
    for index, pg in enumerate(doc):
        page_text = f"{index + 1}"
        # Position at bottom right
        text_x = PAGE_WIDTH - MARGIN_RIGHT
        text_y = PAGE_HEIGHT - 20
        pg.insert_text((text_x, text_y), page_text, fontname="helv", fontsize=PAGE_NUMBER_FONT_SIZE)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
