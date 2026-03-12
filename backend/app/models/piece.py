from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

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
    author_id: int
    type_id: int
    archive_id: int

class PiecePublic(PieceBase):
    id: int

class Piece(PieceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")
    type_id: Optional[int] = Field(default=None, foreign_key="type.id")
    archive_id: Optional[int] = Field(default=None, foreign_key="archive.id")
    
    author: Optional["Author"] = Relationship(back_populates="pieces")
    type: Optional["Type"] = Relationship(back_populates="pieces")
    archive: Optional["Archive"] = Relationship(back_populates="pieces")

