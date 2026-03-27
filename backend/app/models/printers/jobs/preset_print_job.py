from pydantic import BaseModel
from backend.app.models.printers.elements.printeable_piece import PrinteablePiece

class PresetPrintJobConfig(BaseModel):
    sorted_export: bool = False
    ignore_preset_copies: bool = False
    add_piece_number: bool = False
    add_cover_page: bool = False
    add_index: bool = False
    add_blank_page_after_index: bool = False
    merge_pdfs: bool = False

class PresetPrintJob(BaseModel):
    """
    Represents a preset print job configuration for batch printing multiple pieces.

    Attributes:
        preset_name (str): Name identifier for this print preset.
        user_id (int): ID of the user who owns this preset.
        pieces (list[PrinteablePiece]): List of pieces to be printed.
        config (PresetPrintJobConfig): Print configuration settings for this job.
        solved_fails (dict[str, dict[str, str]]): Mapping of piece names to instrument resolution mappings,
            where missing instruments are mapped to their replacement instruments. Defaults to empty dict.
    """
    preset_name: str
    user_id: int
    pieces: list[PrinteablePiece]
    config: PresetPrintJobConfig
    solved_fails: dict[str, dict[str, str]] = {}

