from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize


#Scene that shows the image in the GraphicsView
class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    #Load the image in the scene
    def load_image(self,qpixmap:QPixmap,graphics_view_size:QSize):
        self.clear()
        self.qpixmap = qpixmap.scaled(graphics_view_size.width(),graphics_view_size.height(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.image_item = QGraphicsPixmapItem(self.qpixmap)
        self.addItem(self.image_item)
        self.setSceneRect(self.image_item.boundingRect())