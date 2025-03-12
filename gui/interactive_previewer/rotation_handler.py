from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
from PyQt6.QtGui import QPen, QBrush, QColor



class RotationHandler(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setPen(QPen(Qt.GlobalColor.green, 3, Qt.PenStyle.SolidLine))
        self.setBrush(QBrush(QColor(0,255,0)))  # Gray color with 50% transparency
