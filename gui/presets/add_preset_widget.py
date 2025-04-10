from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSlot, QEvent
from gui.status_console import StatusConsole
from gui.list_items.infinite_comboboxes_item import InfiniteComboBoxesItem
from gui.presets.abstract_modifying_preset_widget import AbstractModifyingPresetWidget


class AddPresetWidget(AbstractModifyingPresetWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    

    def confirm(self):
        pass