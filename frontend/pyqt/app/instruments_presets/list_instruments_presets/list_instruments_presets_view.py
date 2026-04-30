from PyQt6 import QtWidgets, QtCore, QtGui
from frontend.pyqt.app.elements.status_console import StatusConsole
from frontend.pyqt.app.elements.list_items.status_console_item_with_two_buttons import StatusConsoleItemWithTwoButtons

class ListInstrumentsPresetsView(QtWidgets.QDialog):
    add_signal = QtCore.pyqtSignal()
    edit_item_signal = QtCore.pyqtSignal(str)
    delete_item_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.setWindowTitle(self.tr("Instruments Presets"))
        self.setMinimumSize(400, 300)

    def _setup_ui(self):
        # Add button with green background
        self.add_btn = QtWidgets.QPushButton("+")
        self.add_btn.setStyleSheet("QPushButton {background-color: #55ff55; color: black; font-weight: bold; font-size: 16px;}")
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.setToolTip(self.tr("Add new item"))
        
        # Connect the add button to the add_signal
        self.add_btn.clicked.connect(self.add_signal.emit)

        # Top layout for the button
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.add_btn)

        # Status console to hold the items
        self.status_console = StatusConsole()

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.status_console)

        self.setLayout(main_layout)

    def add_item(self, name: str, tooltip: str = "") -> None:
        """
        Creates an item and adds it to the StatusConsole, 
        connecting its signals to the view's signals.
        """
        item = StatusConsoleItemWithTwoButtons(name, tooltip)
        
        # Connect the signals from the item to the view's signals
        item.edit_signal.connect(self.edit_item_signal.emit)
        item.delete_signal.connect(self.delete_item_signal.emit)
        
        self.status_console.add_item(item)
