from sqlmodel import SQLModel
from typing import List
from backend.app.models.printers.elements.printeable_file import PrinteableFile

class SimplePrintJob(SQLModel):
    files: List[PrinteableFile]
