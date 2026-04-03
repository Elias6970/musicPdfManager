import fitz
import datetime

# 1 mm roughly equals 2.83465 points (72 / 25.4)
MM2PT = 72 / 25.4
A4_W_PT, A4_H_PT = 595.276, 841.890

def _get_string_width(text: str, fontname: str, fontsize: int) -> float:
    return fitz.get_text_length(text, fontname=fontname, fontsize=fontsize)

def _fit_text_in_width(text: str, fontname: str, fontsize: int, max_width: float) -> str:
    """Truncates text with ellipsis if it exceeds the max width."""
    text_width = _get_string_width(text, fontname, fontsize)
    if text_width <= max_width:
        return text
    ellipsis_width = _get_string_width("...", fontname, fontsize)
    available_width = max_width - ellipsis_width
    fitted_text = ""
    for char in text:
        if _get_string_width(fitted_text + char, fontname, fontsize) <= available_width:
            fitted_text += char
        else:
            break
    return fitted_text + "..."

def create_index(elements: list[str], title: str = "Índice", subtitle: str = "") -> fitz.Document:
    """Creates a A4 landscape index PDF document mirroring presets_printer behavior using PyMuPDF."""
    doc = fitz.Document()
    page_width, page_height = A4_H_PT, A4_W_PT  # Landscape A4
    
    if not subtitle:
        subtitle = f"AM Virgen del Remedio {datetime.datetime.now().strftime('%d-%m-%Y')}"

    title_font_name = "hebo"
    subtitle_font_name = "heit"
    font_name = "helv"
    
    title_font_size = 40
    subtitle_font_size = 10
    
    left_margin = 20 * MM2PT
    bottom_margin = 15 * MM2PT
    title_space = 25 * MM2PT
    
    usable_width = page_width - 2 * left_margin
    usable_height = page_height - 2 * bottom_margin - title_space
    
    success = False
    best_font_size = 18
    best_columns = 1
    
    font_size = 18
    min_font_size = 9
    max_columns = 3
    
    while font_size >= min_font_size:
        line_height = font_size * 1.2
        for num_columns in range(1, max_columns + 1):
            rows_per_column = int(usable_height // line_height)
            total_capacity = rows_per_column * num_columns
            if len(elements) <= total_capacity:
                best_font_size = font_size
                best_columns = num_columns
                success = True
                break
        if success:
            break
        font_size -= 1
        
    if not success:
        raise ValueError("Demasiados elementos para colocarlos en el índice dentro del espacio disponible.")

    page = doc.new_page(width=page_width, height=page_height)
    
    # Draw Title (centered horizontally)
    title_width = _get_string_width(title, title_font_name, title_font_size)
    title_x = (page_width - title_width) / 2
    title_y = title_font_size * 1.2 + 5
    page.insert_text((title_x, title_y), title, fontsize=title_font_size, fontname=title_font_name)
    
    # Draw Subtitle
    subtitle_width = _get_string_width(subtitle, subtitle_font_name, subtitle_font_size)
    subtitle_x = (page_width - subtitle_width) / 2
    subtitle_y = title_y + (subtitle_font_size * 1.5) + 5
    page.insert_text((subtitle_x, subtitle_y), subtitle, fontsize=subtitle_font_size, fontname=subtitle_font_name)
        
    # Draw Elements
    line_height = best_font_size * 1.2
    rows_per_column = int(usable_height // line_height)
    column_width = usable_width / best_columns
    
    for idx, texto in enumerate(elements):
        col = idx // rows_per_column
        row = idx % rows_per_column
        x = left_margin + col * column_width
        
        # Base Y position calculated mirroring original reportlab bottom-up translation
        box_y = title_space + bottom_margin + (row * line_height)
        target_y = box_y + best_font_size # adjust to baseline
        
        text_idx = f"{idx+1}- {texto}"
        fitted_text = _fit_text_in_width(text_idx, font_name, best_font_size, column_width - 5)
        page.insert_text((x, target_y), fitted_text, fontsize=best_font_size, fontname=font_name)
        
    return doc

def create_cover_page(title: str) -> fitz.Document:
    """Creates a basic landscape cover page."""
    doc = fitz.Document()
    page = doc.new_page(width=A4_H_PT, height=A4_W_PT)
    
    tw = _get_string_width(title, "hebo", 40)
    page.insert_text(((A4_H_PT - tw) / 2, A4_W_PT / 2), title, fontsize=40, fontname="hebo")
    
    return doc

def add_blank_page(pdf_doc: fitz.Document):
    """Appends a blank landscape A4 page to the document."""
    pdf_doc.new_page(pno=0,width=A4_H_PT, height=A4_W_PT)

def add_cover_page(pdf_doc: fitz.Document, title: str):
    """Inserts a cover page at the beginning of the PDF document."""
    cover_doc = create_cover_page(title)
    pdf_doc.insert_pdf(cover_doc, from_page=0, to_page=cover_doc.page_count - 1, start_at=0)

def add_index_page(pdf_doc: fitz.Document, elements: list[str], title: str = "Índice", subtitle: str = ""):
    """Creates an index page and inserts it at the beginning of the PDF document."""
    index_doc = create_index(elements, title, subtitle)
    pdf_doc.insert_pdf(index_doc, from_page=0, to_page=index_doc.page_count - 1, start_at=0)

def add_piece_number(doc: fitz.Document, page_number: int | str):
    """Adds a sequentially numbered overlay identically to PresetsPrinter."""
    if len(doc) == 0:
        return
    
    font_size = 30
    font_name = "cobo"

    orig_page = doc[0]
    orig_page.remove_rotation() # Ensure page is unrotated before processing
    rect = orig_page.rect
    orig_width, orig_height = rect.width, rect.height
    
    margin = 15
    scale_w = (orig_width - margin) / orig_width
    scale_h = (orig_height - margin) / orig_height
    scale_factor = min(scale_w, scale_h)
    
    new_width = orig_width * scale_factor
    new_height = orig_height * scale_factor
    
    temp_doc = fitz.Document()
    temp_doc.insert_pdf(doc, from_page=0, to_page=0)
    
    doc.delete_page(0)
    new_page = doc.new_page(pno=0, width=orig_width, height=orig_height)
    
    # White background
    new_page.draw_rect(new_page.rect, color=None, fill=(1,1,1))
    
    # Flush top, center horizontally
    dx = (orig_width - new_width) / 2
    dest_rect = fitz.Rect(dx, 0, dx + new_width, new_height)
    new_page.show_pdf_page(dest_rect, temp_doc, 0)

    # Put numbers right aligned
    num_str = str(page_number)
    is_single = int(num_str) < 10 if num_str.isdigit() else len(num_str) == 1
    
    offset = 11 if is_single else 7
    target_x = orig_width - offset
    
    num_width = _get_string_width(num_str, font_name, font_size)
    start_x = target_x - num_width
    
    bottom_y = orig_height - 7
    top_y = 32 # equivalent to height - 25 - 7 in reportlab translated to top align baseline

    # hebo font is bugged and it doesn't generate the name correctly
    new_page.insert_text((start_x, top_y), num_str, fontsize=font_size, fontname=font_name)
    new_page.insert_text((start_x, bottom_y), num_str, fontsize=font_size, fontname=font_name)
    
