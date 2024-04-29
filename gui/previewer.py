from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class Preview(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setMinimumHeight(550)
        self.setStyleSheet("border: 1px solid black;")
        self.setAlignment(Qt.AlignCenter) #type: ignore


    def set_image(self,img_path):
        pixmap = QPixmap(img_path)
        self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio,Qt.SmoothTransformation)) #type: ignore



