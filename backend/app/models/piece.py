from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from backend.app.models.author import Author
    from backend.app.models.type import Type
    from backend.app.models.archive import Archive

class PieceBase(SQLModel):
    cod: int
    name: str
    handwrited: bool
    parted: bool
    digitalized: bool
    
    @property
    def std_name(self) -> str:
        """Dynamically concatenated cod and name."""
        return f"{self.cod}-{self.name}"
    
class PieceCreate(PieceBase):
    author_id: Optional[int] = None
    type_id: Optional[int] = None
    archive_id: int

class PiecePublic(PieceBase):
    id: int

class Piece(PieceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    version: Optional[int] = Field(default=1)
    
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")
    type_id: Optional[int] = Field(default=None, foreign_key="type.id")
    archive_id: Optional[int] = Field(default=None, foreign_key="archive.id")
    
    author: Optional["Author"] = Relationship(back_populates="pieces")
    type: Optional["Type"] = Relationship(back_populates="pieces")
    archive: Optional["Archive"] = Relationship(back_populates="pieces")

