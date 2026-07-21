from sqlmodel import JSON, Column, SQLModel, Field, Relationship, DateTime, func
from datetime import datetime


class ExportOnTheFlyElementBase(SQLModel):
    __tablename__ = "export_on_the_fly_elements"

    archive_id: int
    piece_id: int
    copies: int
    file_name: str
    page: int = Field(
        default=0,
        description="Page number to export starting from 0."
    )
    rotation: int | None = Field(
        default=None,
        description="Rotation angle in degrees. If None, no rotation is applied."
    )
    corners: list[tuple[float, float]] | None = Field(
        default = None,
        sa_column=Column(JSON, nullable=True),
        description="A list of 4 [x, y] relative coordinates (percentages) representing the rotated bounding box. Order should be: Top-Left, Top-Right, Bottom-Right, Bottom-Left"
    )


class ExportOnTheFlyElementCreate(ExportOnTheFlyElementBase):
    pass

class ExportOnTheFlyElement(ExportOnTheFlyElementBase, table=True):
    id: int = Field(default=None, primary_key=True)

    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    exportation_id: int = Field(default=None, foreign_key="export_on_the_fly.id")