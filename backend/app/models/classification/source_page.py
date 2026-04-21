from sqlmodel import SQLModel, Field

class SourcePage(SQLModel):
    """A model representing a single page to be extracted from a source PDF file."""
    file_name: str = Field(description="The name of the source PDF file from which the page will be extracted")
    page: int = Field(default=0, description="The 0-based index of the page to extract from the source PDF")
