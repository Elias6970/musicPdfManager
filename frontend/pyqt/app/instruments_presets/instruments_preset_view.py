from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from frontend.pyqt.app.elements.status_console import StatusConsole
from frontend.pyqt.app.elements.list_items.infinite_comboboxes_item import InfiniteComboBoxesItem

class InstrumentsPresetView(QDialog):
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()
    change_detected = pyqtSignal()

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.instruments_names = []
        
        self.setMinimumSize(600, 400)
        self.setWindowTitle(self.tr(title))

        self.preset_name = QLineEdit()
        self.preset_name.setPlaceholderText(self.tr("New preset name"))

        self.status_console = StatusConsole()
        self.items: list[InfiniteComboBoxesItem] = []

        self.btn_confirm = QPushButton(self.tr("Confirm"))
        
        self.btn_confirm.clicked.connect(self.confirmed.emit)

        _btns_layout = QHBoxLayout()
        _btns_layout.addWidget(self.btn_confirm)

        _layout = QVBoxLayout()
        _layout.addWidget(self.preset_name)
        _layout.addWidget(self.status_console)
        _layout.addLayout(_btns_layout)
        self.setLayout(_layout)


    def set_instruments_options(self, instrument_names: list[str]):
        self.instruments_names = instrument_names


    def add_item(self, preset_instrument: list[tuple[str, str]], copies: int = 1, add_empty_at_end: bool = False):
        """Add an InfiniteComboBoxesItem to the layout. It fills the item with the given data"""
        item = InfiniteComboBoxesItem(instrument_names=self.instruments_names, 
                                      copies=copies, 
                                      initial_combos=0,
                                      parent=self)
        item.changed.connect(self.change_detected.emit)
        if preset_instrument != None:
            for i, (instrument, number) in enumerate(preset_instrument):
                item.add_instrument_combo(instrument, number)
        
        if add_empty_at_end:
            item.add_instrument_combo()
        
        self.items.append(item)
        self.status_console.add_item(item)


    def add_emtpy_item(self):
        """Add an empty item to the layout."""
        item = InfiniteComboBoxesItem(instrument_names=self.instruments_names, parent=self)
        item.changed.connect(self.change_detected.emit)
        self.items.append(item)
        self.status_console.add_item(item)


    def get_data(self) -> list[tuple[int, list[tuple[str, str]]]]:
        """
        Return all the non-empty data from the form.
        Each element in the outer list represents one InfiniteComboBoxesItem as (copies, [(instrument1, number1), (instrument2, number2), ...]).
        """
        all_data = []
        for item in self.items:
            if not item.is_empty():
                all_data.append(item.get_data())
        return all_data

    def get_name(self) -> str:
        return self.preset_name.text()
