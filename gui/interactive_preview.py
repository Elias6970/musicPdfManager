from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, QSize
from classes.interactive_preview_conversor import  InterctivePreviewConversor
from classes.crop_rectangle import CropRectangle
import fitz
# Custom rectangle class
class MovableRectangle(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        self.setPen(QPen(Qt.GlobalColor.gray, 3, Qt.PenStyle.SolidLine))
        self.setBrush(QBrush(QColor(128, 128, 128, 128)))  # Gray color with 50% transparency



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



#Preview in which you can select a rectangle
class InteractivePreview(QGraphicsView):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.pdf_rect = fitz.Rect()
        self.rectangle = MovableRectangle()

        self.img_scene = Scene(self)
        self.setScene(self.img_scene)

        self.is_creating_rect = False # Flag to know if the user is holding the button to create a rectangle
        self.is_dragging = False # Flag to know if the user is moving the rectangle
        self.moving_offset = QPointF() # Offset to move the rectangle

    # Load the image in the preview
    def load_img(self,qpixmap:QPixmap, pdf_rect:fitz.Rect):
        self.rectangle = MovableRectangle()
        self.pdf_rect = pdf_rect
        self.img_scene.load_image(qpixmap,self.size())

    def mousePressEvent(self, event):
            if event and self.img_scene.image_item:
                scene_pos = self.mapToScene(event.pos())
                item_clicked = self.img_scene.itemAt(scene_pos, self.transform())
                
                if event.button() == Qt.MouseButton.LeftButton:
                    #Move the rectangle
                    if isinstance(item_clicked, MovableRectangle):
                        self.is_dragging = True
                        self.moving_offset = scene_pos - self.rectangle.pos()
                    
                    # Create a rectangle
                    else:
                        self.clean_rectangles()

                        self.start_pos = scene_pos
                        
                        self.rectangle = MovableRectangle(QRectF(scene_pos, scene_pos))
                        self.img_scene.addItem(self.rectangle)
                        self.is_creating_rect = True


    def mouseMoveEvent(self, event):
        if event and self.rectangle: 
            #Move the rectangle
            if self.is_dragging:
                scene_pos = self.mapToScene(event.pos())
                new_pos = scene_pos - self.moving_offset
                self.rectangle.setPos(new_pos)

            #Create the rectangle
            elif self.is_creating_rect:
                scene_pos = self.mapToScene(event.pos())
                self.rectangle.setRect(QRectF(self.start_pos, scene_pos).normalized())



    def mouseReleaseEvent(self, event):
        if event and self.rectangle:
            scene_pos = self.mapToScene(event.pos())
            item_clicked = self.img_scene.itemAt(scene_pos, self.transform())
            
            if event.button() == Qt.MouseButton.LeftButton:
                #Move the rectangle
                if isinstance(item_clicked, MovableRectangle):
                    pass
                #Create the rectangle
                else:
                    self.rectangle.setRect(QRectF(self.start_pos, scene_pos).normalized())
            
            self.is_creating_rect = False
            self.is_dragging = False
    
    # Clean all the rectangles in the scene
    def clean_rectangles(self):
        for item in self.img_scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.img_scene.removeItem(item)

    #Return the rectangle selected
    def get_rectangle(self) -> QRectF:
        return QRectF(self.rectangle.rect().topLeft() + self.rectangle.pos(),QSizeF(self.rectangle.rect().width(),self.rectangle.rect().height()))


    #Return the rectangle selected to be scaled to the pdf size
    def get_rectangle_selection(self) -> CropRectangle:
        return CropRectangle(self.get_rectangle().toRect(),
                                self.img_scene.qpixmap.size(),
                                self.pdf_rect)