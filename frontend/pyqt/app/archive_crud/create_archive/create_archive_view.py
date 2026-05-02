from PyQt6 import QtWidgets, QtCore


class CreateArchiveView(QtWidgets.QDialog):
    """Generic view for creating and updating an archive"""
    confirm_signal = QtCore.pyqtSignal()
    cancel_signal = QtCore.pyqtSignal()
    import_archive_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Archive")
        self.setModal(True)
        self.resize(400, 200)

        self._layout = QtWidgets.QVBoxLayout(self)

        self.name_label = QtWidgets.QLabel("Archive Name:", self)
        self.name_input = QtWidgets.QLineEdit(self)

        self.create_button = QtWidgets.QPushButton("Create", self)
        self.create_button.clicked.connect(self.confirm_signal.emit)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.create_button)
        
        self._layout.addWidget(self.name_label)
        self._layout.addWidget(self.name_input)
        self._layout.addStretch()
        self._layout.addLayout(self.button_layout)