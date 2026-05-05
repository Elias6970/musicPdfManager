from sqlmodel import SQLModel, Field
from typing import Optional

class UserConfigBase(SQLModel):
    language: str


class UserConfig(UserConfigBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    presets_instruments_path: str
    presets_pieces_path: str
    dossier_cover_path: str

class UserConfigCreatePublic(UserConfigBase):
    pass

class UserConfigCreate(UserConfigBase):
    user_id: int


class UserConfigPublic(UserConfigBase):
    id: int
    user_id: int
    is_admin: bool