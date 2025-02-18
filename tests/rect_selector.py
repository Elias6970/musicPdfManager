import sys,math,os,fitz,tempfile
from PyQt6.QtWidgets import QApplication, QGraphicsSceneMouseEvent, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsEllipseItem
from PyQt6.QtGui import QPixmap, QPen, QBrush, QColor, QImage
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF
from rect_logic import *


# Custom ellipse class to represent the rotation handle
class RotateHandle(QGraphicsEllipseItem):
    def __init__(self,parent = None):
        super().__init__(0,0,20,20, parent)

        self.setBrush(QBrush(Qt.GlobalColor.green))
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setData(0, "rotation")  # Special identifier for rotation handle



# Custom rectangle class
class RotableRectangle(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        self.setPen(QPen(Qt.GlobalColor.gray, 3, Qt.PenStyle.SolidLine))
        self.setBrush(QBrush(QColor(128, 128, 128, 128)))  # Gray color with 50% transparency


        # Rotation handle
        #self.rotation_handle = RotateHandle(self)
        


# Custom scene class to show the image
class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        

    def load_image(self,file_path,size):
        if file_path:
            self.pixmap = QPixmap(file_path)
            if self.pixmap.isNull():
                print(f"Failed to load image from {file_path}")
                return
            #self.image_item = QGraphicsPixmapItem(self.pixmap)
            self.pixmap = self.pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            self.image_item = QGraphicsPixmapItem(self.pixmap)
            self.addItem(self.image_item)
            self.setSceneRect(self.image_item.boundingRect())

            


# Class to show the image and handle the selection of rectangles
class ImageShower(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)

        path =  os.path.join(tempfile.gettempdir(), os.urandom(24,).hex()+".png")
        self.file = fitz.open("D:\\22\\programacion\\archivo\\projecto\\tests\\pdf_test\\gf.pdf")
        self.page = self.file.load_page(0).get_pixmap(dpi=200) #type:ignore 
        self.page.save(path)

        self.img_scene = Scene()
        #self.img_scene.load_image("C:\\Users\\Elias6970\\Desktop\\fotos verge esports\\logo-antiguo.jpeg")
        self.img_scene.load_image(path,self.size())

        self.setScene(self.img_scene)
        
        self.page_rect = self.file[0].rect


        # Flag to know if the user is holding the button to create a rectangle
        self.is_creating_rect = False 

        self.is_dragging = False # Flag to know if the user is moving the rectangle
        self.moving_offset = QPointF() # Offset to move the rectangle

        self.cropper = ImageCropperManager(self.img_scene.pixmap.size(),self.page_rect)

    def mousePressEvent(self, event):
        if event and self.img_scene.image_item:
            scene_pos = self.mapToScene(event.pos())
            item_clicked = self.img_scene.itemAt(scene_pos, self.transform())
            
            if event.button() == Qt.MouseButton.LeftButton:
                if isinstance(item_clicked, RotableRectangle):
                    self.is_dragging = True
                    self.moving_offset = scene_pos - self.rect_item.pos()
                else:
                    self.clean_rectangles()

                    self.start_pos = scene_pos
                    
                    self.rect_item = RotableRectangle(QRectF(scene_pos, scene_pos))
                    self.img_scene.addItem(self.rect_item)
                    self.is_creating_rect = True
            
            elif event.button() == Qt.MouseButton.MiddleButton:
                self.cropper.save_cropped_pdf(self.get_rectangle().toRect(),self.file,0,"crop.pdf")
                print(f"Cropped PDF saved as 'crop.pdf'")
            
            """#Depreciated:Crop as image
            elif event.button() == Qt.MouseButton.RightButton:
                rect = self.get_rectangle().toRect()
                cropped_pixmap = self.img_scene.pixmap.copy(rect)  # Crop the image using QPixmap.copy()

                # Save the cropped image
                cropped_pixmap.save("cropped_image.jpg")  # Save as file"""
            

    def mouseMoveEvent(self, event):
        if event and self.rect_item: 
            if self.is_creating_rect:
                scene_pos = self.mapToScene(event.pos())
                self.rect_item.setRect(QRectF(self.start_pos, scene_pos).normalized())
            
            elif self.is_dragging:
                scene_pos = self.mapToScene(event.pos())
                new_pos = scene_pos - self.moving_offset
                self.rect_item.setPos(new_pos)


    def mouseReleaseEvent(self, event):
        if event and self.rect_item:
            scene_pos = self.mapToScene(event.pos())
            item_clicked = self.img_scene.itemAt(scene_pos, self.transform())
            
            if event.button() == Qt.MouseButton.LeftButton:
                if isinstance(item_clicked, RotableRectangle):
                    pass
                else:
                    self.rect_item.setRect(QRectF(self.start_pos, scene_pos).normalized())
            
            self.is_creating_rect = False
            self.is_dragging = False
    

    # Clean all the rectangles in the scene
    def clean_rectangles(self):
        for item in self.img_scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.img_scene.removeItem(item)

    #Return the rectangle selected
    def get_rectangle(self) -> QRectF:
        return QRectF(self.rect_item.rect().topLeft() + self.rect_item.pos(),QSizeF(self.rect_item.rect().width(),self.rect_item.rect().height()))




class ImageSelector(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Selector Board")
        self.setGeometry(400, 250, 800, 600)

        self.shower = ImageShower()
        self.setCentralWidget(self.shower)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSelector()
    window.show()
    sys.exit(app.exec())
