from sqlmodel import SQLModel

class UnresolvedInstrumentResponse(SQLModel):
    """
    Response model for an unresolved preset when an instrument is missing.
    """
    archive_id: int
    piece_std_name: str
    missing_instrument: str
    options: list[str]


class SolvedInstrument(SQLModel):
    """It represents"""
    archive_id: int
    piece_std_name: str
    file: str #Base name of the pdf file (with extension)
    copies: int = 1


class SolvedPreset(SQLModel):
    """
    Represents the solution of a preset for some pieces.
    Solution can be organized by pieces or by instruments, depending on the by_instruments flag in the _preprocess_preset_print_job function.
    If it is organized by pieces, the key of the dictionary is the piece_std_name and the value is another dictionary where the key is the instrument and the value is a SolvedInstrument with the information of the selected pdf.
    Example:
    {
    "piece_1": {
        "oboe_1": {
            "archive_id": 1,
            "piece_std_name": "piece_1",
            "file": "oboe_1.pdf"
        },
        "clarinet": {
            "archive_id": 1,
            "piece_std_name": "piece_1",
            "file": "clarinet_1.pdf"
        }
    }
    If it is organized by instruments, the key of the dictionary is the instrument and the value is another dictionary where the key is the piece_std_name and the value is a SolvedInstrument with the information of the selected pdf.
    Example:
    {
    "oboe_1": {
        "piece_1": {
            "archive_id": 1,
            "piece_std_name": "piece_1",
            "file": "oboe_1.pdf"
        },
        "piece_2": {
            "archive_id": 1,
            "piece_std_name": "piece_2",
            "file": "oboe_1.pdf"
        }
    }
    """
    solution: dict[str, dict[str, SolvedInstrument]] = {}