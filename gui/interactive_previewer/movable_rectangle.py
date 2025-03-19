from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
from gui.interactive_previewer.rotation_handler import RotationHandler

# Custom rectangle class
class MovableRectangle(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        self.setPen(QPen(Qt.GlobalColor.gray, 3, Qt.PenStyle.SolidLine))
        self.setBrush(QBrush(QColor(128, 128, 128, 128)))  # Gray color with 50% transparency
        
        self.rotation_handler = RotationHandler(self)

        self.zoom = 1
    

    # Zoom is the relation between the original pixmap and the printed in the InteractivePreviewer
    # Zoom = Original.width/Printed.width (we use width and not both because we are preserving the aspect ratio)
    def set_zoom(self,original_pixmap_width:float,printed_pixmap_width):
        self.zoom = original_pixmap_width / printed_pixmap_width

   
    #Return the rectangle selected for the original pixmap
    # It multiplies the position by the zoom
    def get_rectangle(self) -> QRectF:
        pos = (self.rect().topLeft() + self.pos()) * self.zoom
        width = self.rect().width() * self.zoom
        height = self.rect().height() * self.zoom
        return QRectF(pos,QSizeF(width,height))
    
    
    #Draw the rotation handler
    def set_rotation_handler(self,rect:QPointF):
        ellipse_width = 23
        ellipse_height = 23
        new_x = rect.x() + (self.rect().width() / 2) - (ellipse_width / 2)
        new_y = rect.y() + self.rect().height() + 10

        self.rotation_handler.setRect(QRectF(new_x,new_y,ellipse_width,ellipse_height))


