from PyQt6 import QtWidgets, QtCore


class CreateArchiveView(QtWidgets.QDialog):
    """Generic view for creating and updating an archive"""
    confirm_signal = QtCore.pyqtSignal()
    cancel_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Archive")
        self.setModal(True)
        self.resize(400, 200)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.name_label = QtWidgets.QLabel("Archive Name:", self)
        self.name_input = QtWidgets.QLineEdit(self)

        self.create_button = QtWidgets.QPushButton("Create", self)
        self.create_button.clicked.connect(self.confirm_signal.emit)
        self.cancel_button = QtWidgets.QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_signal.emit)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.create_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addLayout(self.button_layout)