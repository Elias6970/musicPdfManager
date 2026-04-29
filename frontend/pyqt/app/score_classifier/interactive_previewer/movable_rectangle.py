from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
from frontend.pyqt.app.score_classifier.interactive_previewer.rotation_handler import RotationHandler
import numpy as np

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
        self.printed_width = 1.0
        self.printed_height = 1.0
    


    def set_zoom(self,original_pixmap_width:float,printed_pixmap_width:float, printed_pixmap_height:float):
        """
        Set the zoom factor for the rectangle, which is used to convert between the printed pixmap coordinates and the original pixmap coordinates.
        Zoom is the relation between the original pixmap and the printed in the InteractivePreviewer
        Zoom = Original.width/Printed.width (we use width and not both because we are preserving the aspect ratio)
        """
        self.zoom = original_pixmap_width / printed_pixmap_width
        self.printed_width = printed_pixmap_width
        self.printed_height = printed_pixmap_height

   

    def get_rectangle(self) -> QRectF:
        """
        Get the rectangle selected inside the scene. 
        The coordinates are in the scene, not affected by the zoom.
        """
        pos = (self.rect().topLeft() + self.pos())
        width = self.rect().width()
        height = self.rect().height()
        return QRectF(pos,QSizeF(width,height))


    def get_corners(self) -> list[tuple[float,float]]:
        """
        Get the coordinates of the corners of the rectangle in percentage relative to the original pixmap size, taking into account the rotation and zoom.
        :return: List of 4 tuples with the coordinates of the corners. The order is topLeft, topRight, bottomRight, bottomLeft
        """
        rectangle = self.get_rectangle()
        local_corners = [
            rectangle.topLeft(),
            rectangle.topRight(),
            rectangle.bottomRight(),
            rectangle.bottomLeft(),
        ]
        rotated_corners = []
        
        center_x = (rectangle.topLeft().x() + rectangle.bottomRight().x()) / 2
        center_y = (rectangle.topLeft().y() + rectangle.bottomRight().y()) / 2
        rotation_rad = np.deg2rad(self.rotation())
        cos = np.cos(rotation_rad)
        sin = np.sin(rotation_rad)

        rotation_matrix = np.array([
            [cos,-sin],
            [sin,cos]
        ])
        for i in local_corners:
            translated = np.array([i.x()-center_x,i.y()-center_y])
            rotated = rotation_matrix @ translated
            x_val = (float(rotated[0]+center_x) * self.zoom) / (self.printed_width * self.zoom)
            y_val = (float(rotated[1]+center_y) * self.zoom) / (self.printed_height * self.zoom)
            rotated_corners.append((x_val, y_val))

        return rotated_corners


    def set_rotation_handler(self,rect:QPointF):
        ellipse_width = 23
        ellipse_height = 23
        new_x = rect.x() + (self.rect().width() / 2) - (ellipse_width / 2)
        new_y = rect.y() + self.rect().height() + 10

        self.rotation_handler.setRect(QRectF(new_x,new_y,ellipse_width,ellipse_height))


