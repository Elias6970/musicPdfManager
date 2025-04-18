from PyQt6 import QtWidgets,QtCore,QtGui
from classes.constants.constants import EDIT_IMG_PATH, TRASH_IMG_PATH

#Item in a list with two buttons and one lbl
#   name: name of the item. It's the identifier. Need to be unique
#   tool_tip: tooltip for the item
#   edit_func: function that is called when you press edit button. Recive the preset_name as parameter
#   delete_func: function that is called when you press delete button. Recive the preset_name as parameter
class StatusConsleItemWithTwoButtons(QtWidgets.QFrame):
    def __init__(self, name:str, tool_tip:str, edit_func, delete_func,parent=None) -> None:
        super().__init__(parent)

        self.name = name

        self.name_lbl = QtWidgets.QLabel(name)
        self.name_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.name_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.name_lbl.setContentsMargins(7,0,0,0)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.name_lbl.setFont(bold_font)
        self.name_lbl.setToolTip(tool_tip)
        


        self.edit_btn = QtWidgets.QPushButton()
        self.edit_btn.setIcon(QtGui.QIcon(EDIT_IMG_PATH))
        self.edit_btn.setFixedSize(20, 25)
        self.edit_btn.setToolTip(self.tr("Edit this preset."))
        self.edit_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setIcon(QtGui.QIcon(TRASH_IMG_PATH))
        self.delete_btn.setToolTip(self.tr("Delete this preset."))
        self.delete_btn.setFixedSize(20, 25)
        self.delete_btn.setStyleSheet("QPushButton {background-color: #ff5555;}")
        self.delete_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)
        layout.addWidget(self.name_lbl)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)
        
        # Connect delete button
        #Remove the item from the StatusConsole and from the list of pdfs
        self.edit_btn.clicked.connect(lambda: edit_func(name))
        self.delete_btn.clicked.connect(lambda: delete_func(name))
    