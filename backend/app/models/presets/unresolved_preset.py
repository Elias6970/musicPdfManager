from sqlmodel import SQLModel

class UnresolvedPresetResponse(SQLModel):
    """
    Response model for an unresolved preset when an instrument is missing.
    """
    piece_std_name: str
    missing_instrument: str
    options: list[str]
