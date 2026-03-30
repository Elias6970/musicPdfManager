from backend.app.models.printers.elements.printeable_element import PrinteableElement

class PrinteablePiece(PrinteableElement):
    #It doesn't have archive_id because it is related to the PresetPrintJob.
    std_name: str
