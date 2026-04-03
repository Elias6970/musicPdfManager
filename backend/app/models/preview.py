from pydantic import BaseModel, Field

class PreviewRequest(BaseModel):
    archive_id: int = Field(..., description="ID of the archive containing the piece")
    piece_std_name: str = Field(..., description="Standard name of the piece")
    file: str = Field(..., description="Name of the PDF instrument file (eg. '1-Flute.pdf')")
    page_number: int = Field(default=0, description="0-indexed page number to preview")
    dpi: int = Field(default=150, description="Resolution of the generated image (DPI)")
