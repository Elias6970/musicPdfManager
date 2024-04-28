from PyQt5 import QtWidgets,QtGui


class Preview(QtWidgets.QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)


    def set_image(self,img_path):
        pixmap = QtGui.QPixmap(img_path)
        self.setPixmap(pixmap)
        #self.setScaledContents(True)

