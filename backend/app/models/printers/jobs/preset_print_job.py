from pydantic import BaseModel
from backend.app.models.printers.elements.printeable_piece import PrinteablePiece
from enum import Enum

class ExportStrategyType(str, Enum):
    ALL_IN_ONE = "all_in_one"
    SPLITTED = "splitted"
    BY_ELEMENT = "by_element"

class PresetPrintJobConfig(BaseModel):
    export_strategy: ExportStrategyType = ExportStrategyType.BY_ELEMENT
    group_by_instrument: bool = False # If not, it is grouped by piece
    
    sorted_export: bool = False
    ignore_preset_copies: bool = False
    add_piece_number: bool = False
    
    add_cover_page: bool = False
    cover_title: str = "Music Pdf Manager"

    add_index: bool = False
    index_title: str = "Índice"
    index_subtitle: str = ""
    add_blank_page_after_index: bool = False

class PresetPrintJob(BaseModel):
    """
    Represents a preset print job configuration for batch printing multiple pieces.

    Attributes:
        preset_name (str): Name identifier for this print preset.
        user_id (int): ID of the user who owns this preset.
        archive_id (int): ID of the archive containing the pieces to be printed.
        pieces (list[PrinteablePiece]): List of pieces to be printed (All the pieces belong to same archive_id).
        config (PresetPrintJobConfig): Print configuration settings for this job.
        solved_fails (dict[str, dict[str, str]]): Mapping of piece names to instrument resolution mappings,
            where missing instruments are mapped to their replacement instruments. Defaults to empty dict.
            Example:
            {
                "piece_1": {
                    "oboe_1": "oboe_2",
                    "clarinet": "clarinet_1"
                },
                "piece_2": {
                    "oboe_1": "oboe_2"
                }
            }
    """
    preset_name: str
    user_id: int
    archive_id: int
    pieces: list[PrinteablePiece]
    config: PresetPrintJobConfig
    solved_fails: dict[str, dict[str, str]] = {}

class PresetPrintJobPublic(BaseModel):
    """
    Public version of PresetPrintJob that excludes user_id.
    This can be used for sharing the job with the client.
    """
    preset_name: str
    archive_id: int
    pieces: list[PrinteablePiece]
    config: PresetPrintJobConfig
    solved_fails: dict[str, dict[str, str]] = {}