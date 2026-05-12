from PyQt6.QtWidgets import QGraphicsView, QGraphicsRectItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QRectF, QPointF, QPoint
from app.score_classifier.interactive_previewer.movable_rectangle import MovableRectangle
from app.score_classifier.interactive_previewer.rotation_handler import RotationHandler
from app.score_classifier.interactive_previewer.scene import Scene
import math


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
    def load_img(self,qpixmap:QPixmap):
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
                            self.rectangle.set_zoom(self.qpixmap.width(),self.img_scene.qpixmap.width(), self.img_scene.qpixmap.height())
                            self.img_scene.addItem(self.rectangle)
                            self.is_creating_rect = True


    def mouseMoveEvent(self, event):
        if event and self.rectangle:
            #Move the rectangle
            scene_pos = self.mapToScene(event.pos())
            if self.is_dragging:
                new_pos = scene_pos - self.moving_offset
                
                if self.img_scene.image_item:
                    scene_rect = self.img_scene.image_item.sceneBoundingRect()
                    
                    # Temporarily set position to get true mapping with rotation
                    self.rectangle.setPos(new_pos)
                    poly = self.rectangle.mapToScene(self.rectangle.rect())
                    poly_rect = poly.boundingRect()
                    
                    # Compute needed translation if the rotated borders exceed the scene
                    dx, dy = 0.0, 0.0
                    if poly_rect.left() < scene_rect.left():
                        dx = scene_rect.left() - poly_rect.left()
                    elif poly_rect.right() > scene_rect.right():
                        dx = scene_rect.right() - poly_rect.right()
                        
                    if poly_rect.top() < scene_rect.top():
                        dy = scene_rect.top() - poly_rect.top()
                    elif poly_rect.bottom() > scene_rect.bottom():
                        dy = scene_rect.bottom() - poly_rect.bottom()
                        
                    # Apply correction offsets
                    new_pos = QPointF(new_pos.x() + dx, new_pos.y() + dy)

                self.rectangle.setPos(new_pos)
            
            #Rotating rectangle
            elif self.is_rotating:
                scene_pos = self.mapToScene(event.pos())  

                # Calculate the angle change
                delta_x = scene_pos.x() - self.rotating_offset.x()
                new_angle = self.initial_rotation_angle + math.degrees(-delta_x/240) # Adjust divisor for sensitivity

                self.rectangle.setTransformOriginPoint(self.rectangle.rect().x() + self.rectangle.rect().width()/2,self.rectangle.rect().y() + self.rectangle.rect().height()/2)
                
                # Apply new rotation
                self.rectangle.setRotation(new_angle)
                
                if self.is_rect_inside_image():
                    self.angle = new_angle
                else:
                    # Revert to last valid angle if it goes outside bounds
                    self.rectangle.setRotation(self.angle)
                
            #Create the rectangle
            elif self.is_creating_rect:
                scene_pos = self.mapToScene(event.pos())
                if self.img_scene.image_item:
                    scene_rect = self.img_scene.image_item.sceneBoundingRect()
                    clamped_x = max(scene_rect.left(), min(scene_pos.x(), scene_rect.right()))
                    clamped_y = max(scene_rect.top(), min(scene_pos.y(), scene_rect.bottom()))
                    scene_pos = QPointF(clamped_x, clamped_y)
                    
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
                elif self.is_creating_rect:
                    if self.img_scene.image_item:
                        scene_rect = self.img_scene.image_item.sceneBoundingRect()
                        clamped_x = max(scene_rect.left(), min(scene_pos.x(), scene_rect.right()))
                        clamped_y = max(scene_rect.top(), min(scene_pos.y(), scene_rect.bottom()))
                        scene_pos = QPointF(clamped_x, clamped_y)

                    self.rectangle.setRect(QRectF(self.start_pos, scene_pos).normalized())
                    self.rectangle.set_rotation_handler(self.rectangle.rect().topLeft())

                    self.rect_is_minimum_size()
                    #Mensaje de alerta
            
            self.is_creating_rect = False
            self.is_dragging = False
            self.is_rotating = False
            self.initial_rotation_angle = self.angle

    
    def clean_rectangles(self):
        """Remove all the rectangles in the scene."""
        for item in self.img_scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.img_scene.removeItem(item)

    
    def get_rectangle_corners(self) -> list[tuple[float,float]]:
        """
        Return the 4 corners of the rectangle applying the rotation and zoom, in the original pixmap reference frame. 
        The order of the corners is topLeft, topRight, bottomRight, bottomLeft
        """
        return self.rectangle.get_corners()


    def rect_is_minimum_size(self):
        """Check if the rectangle is bigger than the minimum size, if not it deletes it"""
        rect = self.rectangle.get_rectangle()
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

    def is_rect_inside_image(self) -> bool:
        """Check if the fully rotated rectangle fits entirely inside the image."""
        if not self.img_scene.image_item:
            return False
            
        scene_rect = self.img_scene.image_item.sceneBoundingRect()
        
        # Map the local rectangle to the scene, getting a QPolygonF with the rotated corners
        polygon = self.rectangle.mapToScene(self.rectangle.rect())
        
        # Check if all polygon vertices are inside the image's scene bounding rect
        for i in range(polygon.count()):
            if not scene_rect.contains(polygon.at(i)):
                return False
                
        return True