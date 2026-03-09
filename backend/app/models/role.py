from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING: # Avoid circular imports during type checking
    from backend.app.models.user import User

class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    users: list["User"] = Relationship(back_populates="role") # Use string literal to avoid circular import issues

    