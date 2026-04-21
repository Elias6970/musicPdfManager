from PyQt6 import QtWidgets, QtCore

class DeleteArchiveView(QtWidgets.QDialog):
    """View with a combobox for selecting and deleting an existing archive"""
    confirm_signal = QtCore.pyqtSignal()
    cancel_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Archive")
        self.setModal(True)
        self.resize(400, 150)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Combobox for selecting which archive to delete
        self.archive_select_label = QtWidgets.QLabel(self.tr("Select Archive to Delete:"), self)
        self.archive_combobox = QtWidgets.QComboBox(self)

        # Buttons
        self.delete_button = QtWidgets.QPushButton(self.tr("Delete"), self)
        # Style it as a destructive action
        self.delete_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.delete_button.clicked.connect(self.confirm_signal.emit)
        
        self.cancel_button = QtWidgets.QPushButton(self.tr("Cancel"), self)
        self.cancel_button.clicked.connect(self.cancel_signal.emit)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout.addWidget(self.archive_select_label)
        self.main_layout.addWidget(self.archive_combobox)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.button_layout)
