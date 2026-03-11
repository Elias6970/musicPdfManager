from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from backend.app.models.piece import Piece
    from backend.app.models.user_archive_link import UserArchiveLink


class ArchiveBase(SQLModel):
    name: str

class ArchiveCreate(ArchiveBase):
    pass

class ArchivePublic(ArchiveBase):
    id: int

class Archive(ArchiveBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    pieces: List["Piece"] = Relationship(back_populates="archive")
    user_links: List["UserArchiveLink"] = Relationship(back_populates="archive")