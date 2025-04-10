from PyQt6 import QtWidgets,QtCore,QtGui
from classes.constants.constants import VERSION,APP_AUTHOR,APP_NAME,GITHUB

#Show a window with a description of the app
class About_us_window(QtWidgets.QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle(self.tr("About"))
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        container_layout = QtWidgets.QVBoxLayout()
        
        container_layout.setSpacing(3)

        #Font
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)

        #QLabels
        title = QtWidgets.QLabel(APP_NAME)
        title.setFont(font)
        
        subtitle = QtWidgets.QLabel(self.tr("Simply archive app to manage music pdfs for a music band" )) #traducir
        font.setPointSize(10)
        font.setBold(False)
        subtitle.setFont(font)

        subtitle2 = QtWidgets.QLabel(self.tr("Made for Asociación Musical Virgen del Remedio (Petrer, Spain)"))
        subtitle2.setFont(font)

        version = QtWidgets.QLabel(self.tr("Version: ") + VERSION)
        font.setPointSize(10)
        version.setFont(font)
        
        author = QtWidgets.QLabel(self.tr("Author: ") + APP_AUTHOR) #traducir
        author.setFont(font)
        
        github_page = QtWidgets.QLabel("<a href='{}'>{}</a>".format(GITHUB,GITHUB))
        github_page.setFont(font)

        container_layout.addWidget(title,alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        

        container_layout.addWidget(version,alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(author,alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(github_page,alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        container_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding))
        container_layout.addWidget(subtitle,alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(subtitle2,alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(container_layout)

        self.exec()

