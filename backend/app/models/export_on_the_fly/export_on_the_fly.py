from sqlmodel import JSON, Column, SQLModel, Field, Relationship, DateTime, func

from backend.app.models.export_on_the_fly.export_on_the_fly_element import ExportOnTheFlyElement, ExportOnTheFlyElementCreate


class ExportOnTheFlyBase(SQLModel):
    __tablename__ = "export_on_the_fly"

    name: str = Field(
        description="Name of the exportation process, for identification purposes."
    )


class ExportOnTheFlyCreate(ExportOnTheFlyBase):
    user_id: int = Field(
        description="ID of the user who initiated the exportation process."
    )


class ExportOnTheFly(ExportOnTheFlyBase, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    
    elements: list["ExportOnTheFlyElement"] = Relationship(back_populates="exportation", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class ExportOnTheFlyRequest(SQLModel):
    name: str = Field(
        description="Name of the exportation process, for identification purposes."
    )
    elements: list["ExportOnTheFlyElementCreate"] = Field(
        description="List of elements to be exported on the fly."
    )