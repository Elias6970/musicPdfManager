from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING: # Avoid circular imports during type checking
    from backend.app.models.user import User
class RoleBase(SQLModel):
    name: str

class Role(RoleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    users: list["User"] = Relationship(back_populates="role") # Use string literal to avoid circular import issues

class RoleCreate(RoleBase):
    pass

class RolePublic(RoleBase):
    id: int| None = None