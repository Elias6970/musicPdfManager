from sqlmodel import SQLModel, Field

class CatalogGenerationConfigBase(SQLModel):
    blank_rows: int = Field(default=50, ge=0, description="Number of blank rows to include at the end of the catalog.")
    language: str = Field(default="es_ES", description="Language code for the catalog generation, e.g., 'es_ES' for Spanish, 'en_US' for English and ca_VA for Valencià.")
    with_cover: bool = Field(default=True, description="Whether to include a cover page in the catalog.")
    cover_text_box_corners: list[tuple[float, float]] | None = Field(
        default = None,
        description="A list of 4 [x, y] coordinates percentages relative to the page dimensions representing the rotated bounding box for writing a text in the cover page. Order should be: Top-Left, Top-Right, Bottom-Right, Bottom-Left"
    )

class CatalogGenerationConfig(CatalogGenerationConfigBase):
    archive_id: int = Field(description="The ID of the archive for which the catalog will be generated.")

class CatalogGenerationConfigCreate(CatalogGenerationConfigBase):
    pass
    