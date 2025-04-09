import os,pypdf
from classes.printers.printeable_file import PrinteableFile
from classes.printers.printer import Printer

#This class represents a printer saving a list of pdfs to print
class DefualtPrinter(Printer):
    def __init__(self) -> None:
        super().__init__()
        self.items:list[PrinteableFile] = []
        
    def add(self,path:str,copies:int) -> int:
        p = PrinteableFile(path,copies)
        super().add(p)
        
        return p.id

    def remove(self,id:int) -> bool:
        return super().remove(id)

    def export(self,path:str) -> None:
        merged_pdf = pypdf.PdfWriter()
        for i in self.items:
            if isinstance(i,PrinteableFile) and os.path.exists(i.path):
                for j in range(i.copies): #Add the pdf the times that is selected in copies
                    merged_pdf.append(i.path)
        
        merged_pdf.write(path)
        merged_pdf.close()
