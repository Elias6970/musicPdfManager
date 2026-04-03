from sqlmodel import SQLModel, Field


class PiecesPreset(SQLModel):
    """
    Saves a fixed amount of pieces, associated with an instruments preset.
    Example preset:
    {
        "name": "My Pieces Preset",
        "instruments_preset_name": "My Instruments Preset",
        "user_id": 123,
        "pieces": ["piece1", "piece2", "piece3"]
    }
    """
    name: str = Field(..., description="The name of the pieces preset")
    instruments_preset_name: str = Field(..., description="The name of the instruments preset associated with this pieces preset")
    user_id: int = Field(..., description="The ID of the user who owns this preset and the instruments preset")
    pieces: list[str] = Field(..., description="A list of piece std names included in this preset")