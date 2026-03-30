from sqlmodel import Session

from backend.app.models.presets.instruments_preset import InstrumentsPreset
from backend.app.models.presets.resolution_preset import SolvedInstrument, SolvedPreset, UnresolvedInstrumentResponse
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJob
from backend.app.models.printers.jobs.simple_print_job import SimplePrintJob
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.services.archive_services import get_archive_path
from backend.app.services.instruments_preset_service import get_preset
from backend.app.services.pieces_services import get_scores
from backend.app.settings import get_server_settings
from backend.app.constants.constants import DIR_SCORES
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

def _add_to_solution(solvedPreset: SolvedPreset, archive_id: int, piece_std_name: str, instrument: str, file_name: str, copies: int, by_instrument: bool):
    """
    Add a solved instrument to the solution of a preset print job, organizing it either by pieces or by instruments.
    
    Args:
        solvedPreset (SolvedPreset): The solved preset object to update with the new instrument.
        archive_id (int): The ID of the archive containing the piece.
        piece_std_name (str): The standardized name of the piece.
        instrument (str): The instrument name.
        file_name (str): The original file name of the instrument part.
        by_instrument (bool): If True, organize solution by instruments; if False, organize by pieces.
    """
    if by_instrument:
        key = instrument
        subkey = piece_std_name
    else:
        key = piece_std_name
        subkey = instrument

    if key not in solvedPreset.solution:
        solvedPreset.solution[key] = {subkey: SolvedInstrument(archive_id=archive_id, 
                                                                piece_std_name=piece_std_name, 
                                                                file=file_name, 
                                                                copies=copies)}
    else:
        solvedPreset.solution[key][subkey] = SolvedInstrument(archive_id=archive_id, 
                                                                piece_std_name=piece_std_name, 
                                                                file=file_name, 
                                                                copies=copies)


def _preprocess_preset_print_jon(session: Session, 
                                 job: PresetPrintJob, 
                                 preset: InstrumentsPreset,
                                 by_instruments: bool) -> tuple[SolvedPreset, list[UnresolvedInstrumentResponse]]:
    """
    Preprocesses a PresetPrintJob by expanding the pieces according to the specified preset, taking into account the number of copies and other options for each instrument.

    Args:
        session (Session): The database session.
        job (PresetPrintJob): The original print job containing the pieces to be printed.
        preset (InstrumentsPreset): The preset containing the configuration for each instrument.
        by_instruments (bool): Flag indicating how the solution should be organized. If True, the solution will be organized by instruments; if False, it will be organized by pieces.

    Returns:
        list[UnresolvedInstrumentResponse] | None: A list of unresolved instrument responses or None if no unresolved instruments are found.
    """
    solved: SolvedPreset = SolvedPreset()
    unresolved:list[UnresolvedInstrumentResponse] = []
    
    for piece in job.pieces:        
        file_manager = ArchiveFileManager(get_archive_path(session, job.archive_id))
        scores = get_scores(piece.std_name, file_manager, extension=False)

        for instrument in preset.instruments:
            solved_file = None
            #Direct assign
            if instrument in scores:
                solved_file = instrument+".pdf"
            
            #Other options
            for other_option in preset.instruments[instrument].other_options: 
                if other_option in scores:
                    solved_file = other_option+".pdf"
        
            
            #Check if it is in solved_fails
            solved_file = job.solved_fails.get(piece.std_name, {}).get(instrument)

            if solved_file:
                _add_to_solution(solved, job.archive_id, piece.std_name, instrument, solved_file, preset.instruments[instrument].copies, by_instruments)
            else: #Not found
                unresolved.append(UnresolvedInstrumentResponse(archive_id=job.archive_id, 
                                                                piece_std_name=piece.std_name, 
                                                                missing_instrument=instrument, 
                                                                options=scores))
    
    return solved, unresolved


def process_preset_print_job(session: Session, job: PresetPrintJob) -> bytes:
    """
    It processes a preset print job by merging the specified number of copies of each file in the print job into a single PDF and returns it as bytes.
    
    Args:
        session (Session): The database session.
        job (SimplePrintJob): The preset print job containing the files to merge and their copy counts.
        
    Returns:
        bytes: The merged PDF file as a bytes object.
        
    Raises:
        FileNotFoundError: If any of the files in the preset print job are not found on the disk.
    """
    preset = get_preset(session, job.user_id, job.preset_name)
    #Check all the paths
    solved, unresolved = _preprocess_preset_print_jon(session, job, preset, by_instruments=False)
    
    if unresolved != []:
        