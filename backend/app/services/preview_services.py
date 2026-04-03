import os
import fitz
from sqlmodel import Session
from backend.app.models.archive import Archive
from backend.app.models.preview import PreviewRequest
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.constants.constants import DIR_SCORES
from backend.app.services.archive_services import get_archive_path

def generate_preview_bytes(session: Session, request: PreviewRequest) -> tuple[bytes, int]:
    """
    Generates a PNG image of a specific PDF page in memory using PyMuPDF (fitz)
    Returns a tuple of (image_bytes, total_pages)
    """
        
    # 2. Reconstruct the absolute path to the instrument PDF
    archive_path = get_archive_path(session, request.archive_id)
    piece_name = ArchiveFileManager.parse_name_to_file_manager(request.piece_std_name)
    
    pdf_path = os.path.join(archive_path, piece_name, DIR_SCORES, request.file)
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found in the archive")
        
    # 3. Read the PDF and render the requested page to bytes
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Could not open PDF file: {str(e)}")
        
    try:
        if request.page_number < 0 or request.page_number >= doc.page_count:
            raise IndexError(f"Page number {request.page_number} out of bounds. PDF has {doc.page_count} pages.")
            
        page = doc.load_page(request.page_number)
        pix = page.get_pixmap(dpi=request.dpi)
        img_bytes = pix.tobytes("png")
        
        return img_bytes, doc.page_count
    
    except IndexError:
         raise # Re-raise already constructed IndexErrors
    except Exception as e:
        raise RuntimeError(f"Error rendering PDF page: {str(e)}")
    finally:
        doc.close()
