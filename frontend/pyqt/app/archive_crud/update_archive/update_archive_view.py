from PyQt6 import QtWidgets, QtCore

class UpdateArchiveView(QtWidgets.QDialog):
    """View with a combobox for selecting and renaming an existing archive"""
    confirm_signal = QtCore.pyqtSignal()
    cancel_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Archive")
        self.setModal(True)
        self.resize(400, 250)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Combobox for selecting which archive to modify
        self.archive_select_label = QtWidgets.QLabel("Select Archive:", self)
        self.archive_combobox = QtWidgets.QComboBox(self)

        # Input for the new name
        self.name_label = QtWidgets.QLabel("New Archive Name:", self)
        self.name_input = QtWidgets.QLineEdit(self)

        # Buttons
        self.update_button = QtWidgets.QPushButton("Update", self)
        self.update_button.clicked.connect(self.confirm_signal.emit)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_signal.emit)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.update_button)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout.addWidget(self.archive_select_label)
        self.main_layout.addWidget(self.archive_combobox)
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.name_input)
        self.main_layout.addLayout(self.button_layout)
