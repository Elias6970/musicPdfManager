from sqlmodel import SQLModel, Field
from backend.app.models.classification.source_page import SourcePage

class ClassifiedDocumentConfig(SQLModel):
    """Configuration handling file naming collisions if the target PDF already exists."""
    overwrite: bool = Field(default=False, description="If true, overwrites the target destination file if it already exists")
    rename: str | None = Field(default=None, description="If a string is provided, saves the newly created PDF with that name to avoid overwriting the existing one")

class ClassifiedDocument(SQLModel):
    """Represents a new PDF file to be created by merging multiple extracted pages."""
    config: ClassifiedDocumentConfig = Field(default_factory=ClassifiedDocumentConfig, description="The collision resolution configuration for this specific output file")
    pages: list[SourcePage] = Field(default_factory=list, description="An ordered list of pages extracted from various source PDFs that will be merged into this new PDF")
