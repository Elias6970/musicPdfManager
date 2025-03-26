from PyQt6 import QtWidgets,QtCore

"""
Pop up a window that shows a message with checkboxes
    is_by_istruments: tell if the split need to be by instruments.
                      If not, it need to be by pieces.

"""
class TypeOfExportWindow(QtWidgets.QDialog):
    def __init__(self,parent) -> None:
        super(TypeOfExportWindow,self).__init__(parent)

        self.is_by_instruments = True 

        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        _container_layout = QtWidgets.QVBoxLayout()

        #labels
        _warning_lbl = QtWidgets.QLabel(self.tr("How do you want to create the pdfs?"))
        
        #Two options
        self._by_instruments_cb = QtWidgets.QCheckBox()
        self._by_instruments_cb.setText(self.tr("Splitted by instruments"))
        self._by_instruments_cb.setToolTip(self.tr("Create one pdf for each instrument in the preset. Each pdf has all the pieces in the list for one instrument."))
        self._by_instruments_cb.setChecked(True)
        self._by_instruments_cb.clicked.connect(self.set_by_instruments)

        self._by_pieces_cb = QtWidgets.QCheckBox()
        self._by_pieces_cb.setText(self.tr("Splitted by pieces"))
        self._by_pieces_cb.setToolTip(self.tr("Create one pdf for each piece in the list. Each pdf has all the scores for the selected preset fro this piece."))
        self._by_pieces_cb.setChecked(False)
        self._by_pieces_cb.clicked.connect(self.set_by_pieces)
        self._by_instruments_cb.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid black;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: black;
            }
        """)
        #Confirm button
        _confirm_btn = QtWidgets.QPushButton(self.tr("Confirm")) #traducir
        _confirm_btn.clicked.connect(self.hide)

        
        
        _container_layout.addWidget(_warning_lbl)
        _container_layout.addWidget(self._by_instruments_cb)
        _container_layout.addWidget(self._by_pieces_cb)
        _container_layout.addWidget(_confirm_btn)

        self.setLayout(_container_layout)

        self.exec()


    #Change the 
    def set_by_instruments(self):
        self._by_instruments_cb.setChecked(True)
        self._by_pieces_cb.setChecked(False)
        self.is_by_instruments = True

    def set_by_pieces(self):
        self._by_instruments_cb.setChecked(False)
        self._by_pieces_cb.setChecked(True)
        self.is_by_instruments = False


