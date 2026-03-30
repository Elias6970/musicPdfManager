from sqlmodel import Session
from backend.app.models.presets.instruments_preset import InstrumentsPreset
from backend.app.models.presets.resolution_preset import SolvedInstrument, SolvedPreset, UnresolvedInstrumentResponse
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJob
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.services.archive_services import get_archive_path
from backend.app.services.pieces_services import get_scores
from backend.app.custom_order.instrument_sorter import InstrumentSorter

def _add_to_solution(solvedPreset: SolvedPreset, archive_id: int, piece_std_name: str, instrument: str, file_name: str, copies: int, by_instrument: bool):
    """
    Add a solved instrument to the solution of a preset print job, organizing it either by pieces or by instruments.
    
    Args:
        solvedPreset (SolvedPreset): The solved preset object to update with the new instrument.
        archive_id (int): The ID of the archive containing the piece.
        piece_std_name (str): The standardized name of the piece.
        instrument (str): The instrument name.
        file_name (str): The original file name of the instrument part.
        copies (int): The number of copies to print for this instrument.
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


def _preprocess_preset_print_job(session: Session, 
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
    file_manager = ArchiveFileManager(get_archive_path(session, job.archive_id))
    
    #Always sort the instruments in the same order to ensure consistency in the output
    sorted_instruments = InstrumentSorter.sort_instruments(list(preset.instruments.keys()))
    
    for piece in job.pieces:        
        scores = get_scores(piece.std_name, file_manager, extension=False)

        for instrument in sorted_instruments:
            solved_file = None
            #Direct assign
            if instrument in scores:
                solved_file = instrument+".pdf"
            
            #Other options
            for other_option in preset.instruments[instrument].other_options: 
                if other_option in scores:
                    solved_file = other_option+".pdf"
        
            
            if not solved_file:
                #Check if it is in solved_fails
                solved_file = job.solved_fails.get(piece.std_name, {}).get(instrument) #Return None if not found

            if solved_file:
                _add_to_solution(solved, job.archive_id, piece.std_name, instrument, solved_file, preset.instruments[instrument].copies, by_instruments)
            else: #Not found
                unresolved.append(UnresolvedInstrumentResponse(archive_id=job.archive_id, 
                                                                piece_std_name=piece.std_name, 
                                                                missing_instrument=instrument, 
                                                                options=scores))
    
    return solved, unresolved