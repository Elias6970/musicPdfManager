from pydantic import BaseModel

class UnresolvedPresetResponse(BaseModel):
    """
    Response model for an unresolved preset when an instrument is missing.
    """
    piece_std_name: str
    missing_instrument: str
    options: list[str]
