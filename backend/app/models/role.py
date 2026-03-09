from sqlmodel import SQLModel, Field

class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    