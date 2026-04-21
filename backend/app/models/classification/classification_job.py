
from sqlmodel import SQLModel, Field
from backend.app.models.classification.classified_document import ClassifiedDocument

class ClassificationJob(SQLModel):
    """The main payload containing all instructions to generate multiple classified PDFs for a specific music piece."""
    piece_std_name: str = Field(description="The standardized name of the musical piece being processed")
    archive_id: int = Field(description="The unique identifier of the archive containing the piece")
    classifications: dict[str, ClassifiedDocument] = Field(default_factory=dict, description="A dictionary mapping the intended target PDF filenames (e.g., 'Flauta_1.pdf') to their respective structure (ClassifiedDocument) defining the pages to merge and configuration")
    files_classified: list[str] = Field(default_factory=list, description="A list of the PDF filenames that were used as a source for generating the classfied documents. They are going to be removed during the classification process")
