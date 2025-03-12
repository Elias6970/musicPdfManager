from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, QSize
from classes.interactive_preview_conversor import  InterctivePreviewConversor
from classes.crop_rectangle import CropRectangle
import fitz



#Scene that shows the image in the GraphicsView
class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    #Load the image in the scene
    def load_image(self,qpixmap:QPixmap,graphics_view_size:QSize):
        self.qpixmap = qpixmap.scaled(graphics_view_size.width(), qpixmap.width(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.image_item = QGraphicsPixmapItem(self.qpixmap)
        self.addItem(self.image_item)
        self.setSceneRect(self.image_item.boundingRect())