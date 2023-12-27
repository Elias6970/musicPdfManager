from PyQt5 import QtWidgets,QtCore,QtGui
from classes.constants import VERSION,APP_AUTHOR,APP_NAME,GITHUB

#Show a window with a description of the app
class About_us_window(QtWidgets.QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("About")
        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()
        
        container_layout.setSpacing(3)

        #Font
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)

        #QLabels
        title = QtWidgets.QLabel(APP_NAME)
        title.setFont(font)
        
        subtitle = QtWidgets.QLabel("Simply archive app to manage music pdfs for a music band" ) #traducir
        font.setPointSize(10)
        font.setBold(False)
        subtitle.setFont(font)

        subtitle2 = QtWidgets.QLabel("Made for Asociación Musical Virgen del Remedio (Petrer, Spain)")
        subtitle2.setFont(font)

        version = QtWidgets.QLabel("Version: " + VERSION)
        font.setPointSize(10)
        version.setFont(font)
        
        author = QtWidgets.QLabel("Author: " + APP_AUTHOR) #traducir
        author.setFont(font)
        
        github_page = QtWidgets.QLabel("<a href='{}'>{}</a>".format(GITHUB,GITHUB))
        github_page.setFont(font)

        container_layout.addWidget(title,alignment=QtCore.Qt.AlignCenter) #type: ignore
        

        container_layout.addWidget(version,alignment=QtCore.Qt.AlignCenter) #type: ignore
        container_layout.addWidget(author,alignment=QtCore.Qt.AlignCenter) #type: ignore
        container_layout.addWidget(github_page,alignment=QtCore.Qt.AlignCenter) #type: ignore
        container_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        container_layout.addWidget(subtitle,alignment=QtCore.Qt.AlignCenter) #type: ignore
        container_layout.addWidget(subtitle2,alignment=QtCore.Qt.AlignCenter) #type: ignore
        
        self.setLayout(container_layout)

        self.exec_()