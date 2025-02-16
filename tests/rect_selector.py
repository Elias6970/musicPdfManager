import sys,math
from PyQt6.QtWidgets import QApplication, QGraphicsSceneMouseEvent, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsEllipseItem
from PyQt6.QtGui import QPixmap, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF



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
        self.rotation_handle = RotateHandle(self)
        


# Custom scene class to show the image
class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        

    def load_image(self,file_path):
        if file_path:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                print(f"Failed to load image from {file_path}")
                return
            self.image_item = QGraphicsPixmapItem(pixmap)
            self.addItem(self.image_item)
            self.setSceneRect(self.image_item.boundingRect())


# Class to show the image and handle the selection of rectangles
class ImageShower(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)
        self.img_scene = Scene()
        self.img_scene.load_image("C:\\Users\\Elias6970\\Desktop\\fotos verge esports\\logo-antiguo.jpeg")
        self.setScene(self.img_scene)
        
        self.is_selecting = False # Flag to know if the user is selecting a rectangle at the moment


    def mousePressEvent(self, event):
        if event and event.button() == Qt.MouseButton.LeftButton and self.img_scene.image_item:
                self.clean_rectangles()

                scene_pos = self.mapToScene(event.pos())
                self.start_pos = scene_pos
                

                self.rect_item = RotableRectangle(QRectF(scene_pos, scene_pos))
                self.img_scene.addItem(self.rect_item)
                self.is_selecting = True


    def mouseMoveEvent(self, event):
        if event and self.is_selecting and self.rect_item: 
                scene_pos = self.mapToScene(event.pos())
                self.rect_item.setRect(QRectF(self.start_pos, scene_pos).normalized())



    def mouseReleaseEvent(self, event):
        if event and event.button() == Qt.MouseButton.LeftButton and self.rect_item:
                scene_pos = self.mapToScene(event.pos())
                self.rect_item.setRect(QRectF(self.start_pos, scene_pos).normalized())
                self.is_selecting = False

    
    # Clean all the rectangles in the scene
    def clean_rectangles(self):
        for item in self.img_scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.img_scene.removeItem(item)







class ImageSelector(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Selector Board")
        self.setGeometry(100, 100, 800, 600)

        self.shower = ImageShower()
        self.setCentralWidget(self.shower)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSelector()
    window.show()
    sys.exit(app.exec())
