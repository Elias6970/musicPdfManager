from PyQt6 import QtWidgets, QtCore, QtGui


class StatusConsoleItemWithTwoTextsAndOneField(QtWidgets.QFrame):
    def __init__(self, piece_name:str, instrument:str, new_instr_options:list[str], parent=None) -> None:
        super().__init__(parent)


        self.piece_lbl = QtWidgets.QLabel(piece_name)
        self.preset_instrument_lbl = QtWidgets.QLabel(instrument)
        self.piece_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.piece_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.preset_instrument_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.preset_instrument_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.preset_instrument_lbl.setFont(bold_font)

        piece_layout = QtWidgets.QVBoxLayout()
        piece_layout.setSpacing(0)
        piece_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        piece_layout.setContentsMargins(0,0,0,0)
        piece_layout.addWidget(self.piece_lbl)
        piece_layout.addWidget(self.preset_instrument_lbl)


        arrow = QtWidgets.QLabel("->")
        arrow.setContentsMargins(0,0,3,0)

        self.score_selected = QtWidgets.QComboBox()
        self.score_selected.addItems(new_instr_options)
        self.score_selected.setCurrentIndex(-1)


        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)
        layout.addLayout(piece_layout)
        layout.addWidget(arrow)
        layout.addWidget(self.score_selected)

        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)



    def get_selection(self) -> tuple[str,str,str]|None:
        """
        Get all the text of the object.
        Return a tuple with (piece,preset_instrument,score_selected) or None if nothing selected
        """
        
        if self.score_selected.currentIndex() == -1:
            return None
        
        return (self.piece_lbl.text(),
                self.preset_instrument_lbl.text(),
                self.score_selected.currentText())