from PyQt6.QtWidgets import QGraphicsView, QGraphicsRectItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QRectF, QPointF, QPoint
from classes.crop_rectangle import CropRectangle
from gui.interactive_previewer.movable_rectangle import MovableRectangle
from gui.interactive_previewer.rotation_handler import RotationHandler
from gui.interactive_previewer.scene import Scene
import fitz,math




#Preview in which you can select a rectangle
class InteractivePreviewer(QGraphicsView):
    min_rect_width = 50
    min_rect_height = 50


    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        self.qpixmap = QPixmap()
        self.rectangle = MovableRectangle()

        self.img_scene = Scene(self)
        self.setScene(self.img_scene)

        self.is_creating_rect = False # Flag to know if the user is holding the button to create a rectangle
        self.is_dragging = False # Flag to know if the user is moving the rectangle
        self.is_rotating = False
        self.moving_offset = QPointF() # Offset to move the rectangle
        self.rotating_offset = QPointF() # Offset to rotate the rectangle
        self.initial_rotation_angle = 0.0
        self.angle = 0.0


    # Load the image in the preview
    def load_img(self,qpixmap:QPixmap, pdf_rect:fitz.Rect):
        self.rectangle = MovableRectangle()
        self.qpixmap = qpixmap
        self.img_scene.load_image(qpixmap,self.size())


    def mousePressEvent(self, event):
            if event and self.img_scene.image_item:
                scene_pos = self.mapToScene(event.pos())
                item_clicked = self.img_scene.itemAt(scene_pos, self.transform())
                
                if event.button() == Qt.MouseButton.LeftButton:
                    #Move the rectangle
                    if isinstance(item_clicked, MovableRectangle):
                        if not self.is_creating_rect and not self.is_rotating:
                            self.is_dragging = True
                            self.moving_offset = scene_pos - self.rectangle.pos()
                    # Rotate the rectangle (click the circle)
                    elif isinstance(item_clicked, RotationHandler):
                        if not self.is_creating_rect and not self.is_dragging:
                            self.is_rotating = True
                            self.rotating_offset = scene_pos

                    # Create a rectangle
                    else:
                        if not self.is_rotating and not self.is_dragging and self.is_pos_inside_image(event.pos()):
                            self.clean_rectangles()

                            self.start_pos = scene_pos
                            
                            self.rectangle = MovableRectangle(QRectF(scene_pos, scene_pos))
                            self.rectangle.set_zoom(self.qpixmap.width(),self.img_scene.qpixmap.width())
                            self.img_scene.addItem(self.rectangle)
                            self.is_creating_rect = True


    def mouseMoveEvent(self, event):
        if event and self.rectangle:
            #Move the rectangle
            if self.is_dragging and self.is_pos_inside_image(event.pos()):
                if not self.is_pos_inside_image(event.pos()):
                    return
                scene_pos = self.mapToScene(event.pos())
                new_pos = scene_pos - self.moving_offset
                self.rectangle.setPos(new_pos)
            
            #Rotating rectangle
            elif self.is_rotating:
                scene_pos = self.mapToScene(event.pos())  

                # Calculate the angle change
                delta_x = scene_pos.x() - self.rotating_offset.x()
                #delta_y = scene_pos.y() - self.rotating_offset.y()
                self.angle = self.initial_rotation_angle + math.degrees(-delta_x/240) # Adjust divisor for sensitivity

                self.rectangle.setTransformOriginPoint(self.start_pos.x() + self.rectangle.rect().width()/2,self.start_pos.y() + self.rectangle.rect().height()/2)
                self.rectangle.setRotation(self.angle)
                
            #Create the rectangle
            elif self.is_creating_rect and self.is_pos_inside_image(event.pos()):
                #print("Pos:", event.pos())
                scene_pos = self.mapToScene(event.pos())
                self.rectangle.setRect(QRectF(self.start_pos, scene_pos).normalized())

            


    def mouseReleaseEvent(self, event):
        if event and self.rectangle:
            scene_pos = self.mapToScene(event.pos())
            item_clicked = self.img_scene.itemAt(scene_pos, self.transform())
            
            if event.button() == Qt.MouseButton.LeftButton:
                #Move the rectangle
                if isinstance(item_clicked, MovableRectangle) and self.is_dragging:
                    pass
                
                elif isinstance(item_clicked, RotationHandler) and self.is_rotating:
                    pass

                #Create the rectangle
                elif self.is_creating_rect and self.is_pos_inside_image(event.pos()):
                        self.rectangle.setRect(QRectF(self.start_pos, scene_pos).normalized())
                        self.rectangle.set_rotation_handler(self.rectangle.rect().topLeft())
                        
                        self.rect_is_minimum_size()
                    #Mensaje de alerta
            
            self.is_creating_rect = False
            self.is_dragging = False
            self.is_rotating = False
            self.initial_rotation_angle = self.angle

    
    # Clean all the rectangles in the scene
    def clean_rectangles(self):
        for item in self.img_scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.img_scene.removeItem(item)



    #Return the rectangle selected to be scaled to the pdf size
    def get_rectangle_selection(self) -> CropRectangle:
        return CropRectangle(self.rectangle.get_rectangle(),self.rectangle.rotation())
    

    #If the rectangle is too small delete it
    #Minimum size in the beginning of the class
    def rect_is_minimum_size(self):
        rect = self.get_rectangle_selection().rectangle
        if rect.width() < InteractivePreviewer.min_rect_width or rect.height() < InteractivePreviewer.min_rect_height:
            self.clean_rectangles()
    

    def is_pos_inside_image(self,pos:QPoint) -> bool:
        """Check if the position is inside the image in the scene."""
        if not self.img_scene.image_item:
            return False
        
        scene_initial_pos = self.mapFromScene(0,0)
        scene_rect = QRectF(self.img_scene.image_item.boundingRect())
        scene_rect.moveTo(scene_initial_pos.x(), scene_initial_pos.y())

        return scene_rect.contains(QPointF(pos))