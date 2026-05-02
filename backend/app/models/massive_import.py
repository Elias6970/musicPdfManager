from sqlmodel import SQLModel, Field

class MassiveImportResponse(SQLModel):
    full_added_pieces: list[str] = Field(default_factory=list, description="List of pieces std_names that were fully added with their files.")
    pieces_without_files: list[str] = Field(default_factory=list, description="List of pieces std_names that were added without files.")
    not_added_pieces: list[dict[str, str]] = Field(default_factory=list, description="List of pieces that were not added, with their std_name and the error that occurred during the import.")