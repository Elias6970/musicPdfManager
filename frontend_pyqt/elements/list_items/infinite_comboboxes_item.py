from PyQt6 import QtWidgets,QtCore, QtGui
from frontend_pyqt.elements.list_items.instrument_and_number_item import InstrumentAndNumberItem

class InfiniteComboBoxesItem(QtWidgets.QFrame):

    def __init__(self,every_change_func,initial_combos:int|None=None,parent=None) -> None:
        """Item for a list with generative comboboxes. When you edit the last combobox in the item it generates a new one.
            :param change_func: function called when any combobox change.
            :param initial_combos: number of comboboxes that are generated when you create the object"""


        super().__init__(parent)
        if initial_combos == None:
            self.default_instrument_combos = 2
        else:
            self.default_instrument_combos = initial_combos
        
        self.max_copies = 20
        self.instruments:list[InstrumentAndNumberItem] = []
        self.every_change_func = every_change_func #Function that is called when the text of the line edit changes

        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(48)
        self.num_copies.addItems([str(i+1) for i in range(self.max_copies)])
        
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


    #Add a line edit to the layout
    #The line edit add a new lineEdit if you write in the last one
    def add_instrument_combo(self,instrument:str|None=None,number:str|int|None=None):
        l1 = InstrumentAndNumberItem(instrument,number)
        l1.instrument.currentIndexChanged.connect(lambda: ((self.add_instrument_combo() if self.instruments.index(l1) == len(self.instruments) - 1 else None), self.every_change_func(self)))

        if len(self.instruments) > 0:
            _arrow_font = QtGui.QFont()
            _arrow_font.setPointSize(12)
            _arrow = QtWidgets.QLabel("  ->  ")
            _arrow.setFont(_arrow_font)
            _arrow.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
            self.layout().addWidget(_arrow)
        

        #Delete the streach and add it at the end of the layout
        for i in reversed(range(self.layout().count())):
            item = self.layout().itemAt(i)
            if item.spacerItem():
                self.layout().takeAt(i)
                break
        self.layout().addWidget(l1)
        self.layout().addStretch()
        
        self.instruments.append(l1)


    def is_empty(self) -> bool:
        """Return true if any QCombobox instrument is selected"""
        for i in self.instruments:
            if not i.is_empty():
                return False
        return True
