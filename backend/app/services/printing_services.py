from sqlmodel import Session

from backend.app.models.printers.jobs.simple_print_job import SimplePrintJob
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.services.archive_services import get_archive_path
from backend.app.settings import get_server_settings
import os, fitz

def process_simple_print_job(session: Session, job: SimplePrintJob) -> bytes:
    """
    It merges the specified number of copies of each file in the print job into a single PDF and returns it as bytes.
    
    Args:
        session (Session): The database session.
        job (SimplePrintJob): The print job containing the files to merge and their copy counts.
        
    Returns:
        bytes: The merged PDF file as a bytes object.
        
    Raises:
        FileNotFoundError: If any of the files in the print job are not found on the disk.
    """
    result_pdf = fitz.open()
    
    for file_element in job.files:
        archive_folder = get_archive_path(session, file_element.archive_id)
        piece_folder = ArchiveFileManager.parse_name_to_file_manager(file_element.file_name)
        file_path = os.path.join(archive_folder, piece_folder, file_element.file_name)
        
        if os.path.exists(file_path):
            with fitz.open(file_path) as doc:
                for _ in range(file_element.copies):
                    result_pdf.insert_pdf(doc)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
                    
    pdf_bytes = result_pdf.write()
    result_pdf.close()
    
    return pdf_bytes

          