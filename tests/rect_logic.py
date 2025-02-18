from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, QRect, QSize
import fitz

# Class that manages the cropping of the image
class ImageCropperManager():
    #pixamp_size: QSize, pdf_page_size:fitz
    def __init__(self,pixmap_size:QSize,pdf_page_size:fitz.Rect) -> None:
        self.pdf_page_size = pdf_page_size

        self.zoom = pixmap_size.width() / self.pdf_page_size.width
        

    #Save the cropped pdf
    def save_cropped_pdf(self,rect:QRect,pdf:fitz.Document,pdf_page:int,output_path:str): 
        x0 = rect.x() / self.zoom
        y0 = rect.y() / self.zoom
        x1 = (rect.x() + rect.width()) / self.zoom
        y1 = (rect.y() + rect.height()) / self.zoom


        
        crop_rect = fitz.Rect(x0, y0, x1, y1)
        
        # Apply cropping to the page
        pdf[pdf_page].set_cropbox(crop_rect)

        # Save the cropped PDF
        pdf.save(output_path)
