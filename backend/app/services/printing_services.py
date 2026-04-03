from sqlmodel import Session

from backend.app.error import UnresolvedInstrumentsException
from backend.app.models.printers.jobs.preset_print_job import ExportStrategyType, PresetPrintJob
from backend.app.models.printers.jobs.simple_print_job import SimplePrintJob
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.services.archive_services import get_archive_path
from backend.app.services.export_strategies.all_in_one import AllInOneExporter
from backend.app.services.export_strategies.base_strategy import PresetExportStrategy
from backend.app.services.export_strategies.by_element import ByElementExporter
from backend.app.services.export_strategies.splitted import SplittedExporter
from backend.app.services.instruments_preset_service import get_preset
from backend.app.settings import get_server_settings
from backend.app.constants.constants import DIR_SCORES
from backend.app.utils.name_manager import NameManager
from backend.app.services.preset_preprocessing_services import _preprocess_preset_print_job
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
        piece_folder = ArchiveFileManager.parse_name_to_file_manager(file_element.piece_std_name)
        file_name = ArchiveFileManager.extract_original_filename(file_element.file_name)
        file_path = os.path.join(archive_folder, piece_folder, DIR_SCORES,file_name)
        
        if os.path.exists(file_path):
            with fitz.open(file_path) as doc:
                for _ in range(file_element.copies):
                    result_pdf.insert_pdf(doc)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
                    
    pdf_bytes = result_pdf.write()
    result_pdf.close()
    
    return pdf_bytes


def process_preset_print_job(session: Session, job: PresetPrintJob) -> bytes:
    """
    It processes a preset print job by merging the specified number of copies of each file in the print job into a single PDF and returns it as bytes.
    
    Args:
        session (Session): The database session.
        job (SimplePrintJob): The preset print job containing the files to merge and their copy counts.
        
    Returns:
        bytes: The merged PDF file as a bytes object.
        
    Raises:
        UnresolvedInstrumentsException: If any of the instruments in the preset print job are unresolved.
    """
    preset = get_preset(session, job.user_id, job.preset_name)

    #Sort the pieces list
    if job.config.sorted_export:
         print("Sorting pieces...")
         job.pieces.sort(key=lambda x: NameManager.get_name(x.std_name).lower())
         print(job.pieces)
         
    #Check all the files to found the unresolved instruments of the preset
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    if unresolved:
        raise UnresolvedInstrumentsException(unresolved)
    
    export_strategies:dict[str, PresetExportStrategy] = {
        ExportStrategyType.ALL_IN_ONE: AllInOneExporter(),
        ExportStrategyType.SPLITTED: SplittedExporter(),
        ExportStrategyType.BY_ELEMENT: ByElementExporter()
    }
    strategy = export_strategies[job.config.export_strategy] #Raise error if not found, but it should be always found because of the Enum

    return strategy.export(session, solved, job.config)