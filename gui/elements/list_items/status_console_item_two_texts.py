from PyQt6 import QtWidgets, QtCore, QtGui
from classes.constants.constants import TRASH_IMG_PATH

#Item in the status console
# item_id: id to delete the item from a list
# remove_widget: function to remove the widget from the layout
# remove_from_list: function to remove the item from the list. (Used for the logic list to print)
class StatusConsleItemWithTwoTexts(QtWidgets.QFrame):
    def __init__(self, piece_name:str, instrument:str, copies:str|int, item_id:int|str, remove_widget, remove_from_list,parent=None) -> None:
        super().__init__(parent)

        self.item_id = item_id

        self.piece_lbl = QtWidgets.QLabel(piece_name)
        self.instrument_lbl = QtWidgets.QLabel(instrument)
        self.piece_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.piece_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.instrument_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.instrument_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.instrument_lbl.setFont(bold_font)

        piece_layout = QtWidgets.QVBoxLayout()
        piece_layout.setSpacing(0)
        piece_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        piece_layout.setContentsMargins(0,0,0,0)
        piece_layout.addWidget(self.piece_lbl)
        piece_layout.addWidget(self.instrument_lbl)


        self.copies_lbl = QtWidgets.QLabel(str(copies))
        self.copies_lbl.setContentsMargins(0,0,3,0)

        self.delete_btn = QtWidgets.QPushButton()
        self.delete_btn.setIcon(QtGui.QIcon(TRASH_IMG_PATH))
        self.delete_btn.setFixedSize(20, 25)
        self.delete_btn.setStyleSheet("background-color: #ff5555")
        self.delete_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)
        layout.addLayout(piece_layout)
        layout.addWidget(self.copies_lbl)
        layout.addWidget(self.delete_btn)
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)
        
        # Connect delete button
        #Remove the item from the StatusConsole and from the list of pdfs
        self.delete_btn.clicked.connect(lambda: remove_widget(self) or remove_from_list(self.item_id))
