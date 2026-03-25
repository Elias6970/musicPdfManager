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
    preset_name: str
    user_id: int
    pieces: list[PrinteablePiece]
    config: PresetPrintJobConfig

