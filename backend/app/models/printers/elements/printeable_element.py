from sqlmodel import SQLModel, Field

class PrinteableElement(SQLModel):
    copies: int = Field(default=1, ge=1)