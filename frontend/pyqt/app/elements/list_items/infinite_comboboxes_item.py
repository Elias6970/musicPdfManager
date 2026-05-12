from PyQt6 import QtWidgets,QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
from app.elements.list_items.instrument_and_number_item import InstrumentAndNumberItem

class InfiniteComboBoxesItem(QtWidgets.QFrame):
    changed = pyqtSignal(object)

    def __init__(self, instrument_names: list[str], copies: int = 1, initial_combos: int | None = None, parent=None) -> None:
        """
        Item for a list with generative comboboxes. When you edit the last combobox in the item it generates a new one.
        Params:
            - instrument_names: list of the names of the instruments to show in the comboboxes
            - copies: number of copies of the item
            - initial_combos: number of comboboxes that are generated when you create the object
        """
        super().__init__(parent)
        self.instrument_names = instrument_names
        self.default_instrument_combos = initial_combos if initial_combos is not None else 2
        
        self.max_copies = 20
        self.instruments:list[InstrumentAndNumberItem] = []

        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(48)
        self.num_copies.addItems([str(i+1) for i in range(self.max_copies)])
        if 1 <= copies <= self.max_copies:
            self.num_copies.setCurrentText(str(copies))
            
        _space_font = QtGui.QFont()
        _space_font.setPointSize(20)
        _space = QtWidgets.QLabel("|")
        _space.setContentsMargins(10,0,5,0)
        _space.setFont(_space_font)
        _space.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignTop)


        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5,3,5,3)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.num_copies)
        layout.addWidget(_space)
        
        
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setLayout(layout)

        #Add two first line edits
        for i in range(self.default_instrument_combos):
            self.add_instrument_combo()

    def _create_arrow(self):
        """Create and return an arrow label to put between the comboboxes"""
        _arrow_font = QtGui.QFont()
        _arrow_font.setPointSize(12)
        _arrow = QtWidgets.QLabel("  ->  ")
        _arrow.setFont(_arrow_font)
        _arrow.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
        return _arrow

    #Add a line edit to the layout
    #The line edit add a new lineEdit if you write in the last one
    def add_instrument_combo(self,instrument:str|None=None,number:str|int|None=None):
        l1 = InstrumentAndNumberItem(self.instrument_names, instrument,number)
        l1.changed.connect(self._on_item_changed)

        _layout = self.layout()
        if _layout == None:
            return
        
        if len(self.instruments) > 0:
            _layout.addWidget(self._create_arrow())

        #Delete the streach and add it at the end of the layout
        for i in reversed(range(_layout.count())):
            item = _layout.itemAt(i)
            if item and item.spacerItem():
                _layout.takeAt(i)
                break
        _layout.addWidget(l1)
        _layout.addStretch() # type:ignore -> It works, idk why pylance don't detect it
        
        self.instruments.append(l1)

    def _on_item_changed(self, item: InstrumentAndNumberItem):
        """
        Called when any of the InstrumentAndNumberItem's comboboxes change. 
        If the changed item is the last one, it adds a new one.
        """
        if len(self.instruments) > 0 and item == self.instruments[-1]:
            self.add_instrument_combo()
        self.changed.emit(self)

    def is_empty(self) -> bool:
        """Return true if all the QCombobox instruments are empty"""
        for i in self.instruments:
            if not i.is_empty():
                return False
        return True

    def get_data(self) -> tuple[int, list[tuple[str, str]]]:
        """Return a list of non-empty instrument and number tuples for this item.
        Returns:
            A tuple with the number of copies and a list of tuples (instrument, number) for each non-empty instrument combo.
        """
        data = []
        for i in self.instruments:
            if not i.is_empty():
                data.append(i.get_instrument_and_number())

        return (int(self.num_copies.currentText()), data)
