from typing import List, Tuple
from sqlmodel import SQLModel, Field

class SourcePage(SQLModel):
    """A model representing a single page to be extracted from a source PDF file."""
    file_name: str = Field(description="The name of the source PDF file from which the page will be extracted")
    page: int = Field(default=0, description="The 0-based index of the page to extract from the source PDF")
    rotation: int = Field(default=0, description="The rotation angle (in degrees) to apply to the extracted page clockwise. Should be a multiple of 90. It is applied before cropping")
    corners: List[Tuple[float, float]] | None = Field(
        default = None,
        description="A list of 4 [x, y] coordinates percentages relative to the page dimensions representing the rotated bounding box. Order should be: Top-Left, Top-Right, Bottom-Right, Bottom-Left"
    )