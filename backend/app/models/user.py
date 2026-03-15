from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field
from backend.app.models.role import Role

if TYPE_CHECKING:
    from backend.app.models.user_archive_link import UserArchiveLink

class UserBase(SQLModel):
    name: str
    email: str
    role_id: int | None = Field(default=None, foreign_key="role.id")

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password_hash: str = Field()
    role: Role | None = Relationship(back_populates="users")
    archive_links: list["UserArchiveLink"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int