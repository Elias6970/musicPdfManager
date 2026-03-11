from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from backend.app.models.piece import Piece

class AuthorBase(SQLModel):
    name: str = Field(index=True)

class AuthorCreate(AuthorBase):
    pass

class AuthorPublic(AuthorBase):
    id: int

class Author(AuthorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    pieces: List["Piece"] = Relationship(back_populates="author")