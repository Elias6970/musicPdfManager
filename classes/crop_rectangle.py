from PyQt6.QtCore import QRect, QSize
import fitz,tempfile,os

# Class to save a crop to a rectangle
class CropRectangle:
    empty_rectangle = QRect(0,0,0,0)

    def __init__(self,rect:QRect,pixmap_size:QSize,pdf_page_size:fitz.Rect) -> None:
        self.rect = rect
        self.pixmap_size = pixmap_size
        self.pdf_page_size = pdf_page_size

    #Get the rectangle to crop in the pdf
    #The rectangle is scaled to the pdf size
    def get(self) -> fitz.Rect:
        zoom = self.pixmap_size.width() / self.pdf_page_size.width
        
        x0 = self.rect.x() / zoom
        y0 = self.rect.y() / zoom
        x1 = (self.rect.x() + self.rect.width()) / zoom
        y1 = (self.rect.y() + self.rect.height()) / zoom
        
        return fitz.Rect(x0, y0, x1, y1)
    
    def is_empty(self) -> bool:
        return self.rect == self.empty_rectangle
    
    #Crop the pdf that gets by parameters with the rectangle that the obj has
    def crop(self,pdf_path:str,output_path:str) -> str:
        output_path2 = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        file = fitz.open(pdf_path)
        file[0].set_cropbox(self.get())
        file.save(output_path2)#,incremental=True,encryption=fitz.PDF_ENCRYPT_KEEP) #type: ignore
        file.close()
        return output_path2

