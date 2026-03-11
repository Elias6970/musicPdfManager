from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from backend.app.models.piece import Piece

class TypeBase(SQLModel):
    name: str = Field(index=True)

class TypeCreate(TypeBase):
    pass

class TypePublic(TypeBase):
    id: int

class Type(TypeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    pieces: List["Piece"] = Relationship(back_populates="type")