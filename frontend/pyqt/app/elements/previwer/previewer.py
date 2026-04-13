from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class Preview(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setMinimumSize(550,400)
        self.setStyleSheet("border: 1px solid black; padding: 10px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def set_image(self,img_path):
        pixmap = QPixmap(img_path)
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

    def set_image_from_bytes(self,img_bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(img_bytes)
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

    def show_loading(self):
        self.clear()
        self.setText("Loading page...")
        
    def show_error(self, error_msg: str):
        self.clear()
        self.setText(f"Error loading preview:\n{error_msg}")

