from backend.app.models.printers.elements.printeable_element import PrinteableElement

class PrinteableFile(PrinteableElement):
    archive_id: int
    piece_std_name: str
    file_name: str