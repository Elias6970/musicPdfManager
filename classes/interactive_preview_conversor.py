import fitz
from PyQt6.QtGui import QPixmap, QImage

class InterctivePreviewConversor:

    #Conver the first page from a pdf to a QPixmap
    @staticmethod
    def pdf_to_qpixmap(pdf_path:str) -> QPixmap:
        file = fitz.open(pdf_path)
        page_pixmap = file.load_page(0).get_pixmap(dpi=200) #type:ignore 

        img_data = page_pixmap.tobytes("png")  # Convert to PNG bytes

        # Create a QImage from the bytes data
        img = QImage()
        img.loadFromData(img_data)

        # Create QPixmap from QImage
        return QPixmap.fromImage(img)
        