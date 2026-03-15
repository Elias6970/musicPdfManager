import enum
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.archive import Archive
    
class ArchiveRole(str, enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class UserArchiveLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    archive_id: int = Field(foreign_key="archive.id", primary_key=True)
    role: ArchiveRole = Field(default=ArchiveRole.VIEWER)

    # Relationships to access the objects directly from the link
    user: "User" = Relationship(back_populates="archive_links")
    archive: "Archive" = Relationship(back_populates="user_links")