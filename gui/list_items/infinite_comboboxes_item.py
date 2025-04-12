from PyQt6 import QtWidgets,QtCore, QtGui
from classes.constants.instruments_names import *

class InstrumentAndNumber(QtWidgets.QFrame):
    INSTRUMENT_NAMES = [
        GUION,
        OBOE,
        DULZAINA,
        CORNO_INGLES,
        FLAUTA,
        FLAUTIN,
        REQUINTO,
        CLARINETE,
        CLARINETE_PRAL,
        CLARINETE_BAJO,
        SAXOFON_SOPRANO,
        SAXOFON,
        SAXOFON_TENOR,
        SAXOFON_BARITONO,
        FAGOT,
        TROMPA,
        FLISCORNO,
        TROMPETA,
        TROMBON,
        TROMBON_BAJO,
        BOMBARDINO,
        BAJO,
        TUBA,
        PLATOS,
        BOMBO,
        CAJA,
        TIMBALES,
        GONG,
        PERCUSION,
        MARIMBA,
        XILOFONO,
        LIRA,
        VIBRAFONO,
        GUITARRA,
        CHELLO,
        CONTRABAJO,
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self.instrument = QtWidgets.QComboBox()
        self.instrument.addItem("")
        self.instrument.addItems(InstrumentAndNumber.INSTRUMENT_NAMES)
        self.instrument.setCurrentIndex(-1)
        self.instrument.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.set_combobox_width_to_largest_item(self.instrument)
        
        self.number = QtWidgets.QComboBox()
        self.number.addItem("")
        self.number.addItems([str(i) for i in range(1,6)])
        self.number.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        self.number.setFixedWidth(40)

        _layout = QtWidgets.QHBoxLayout()
        _layout.addWidget(self.instrument)
        _layout.addWidget(self.number)

        self.setLayout(_layout)
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setFixedWidth(self.instrument.width() + self.number.width() + 30)

    def is_empty(self):
        """Only is empty if the instrument is not selected"""
        return self.instrument.currentIndex() == -1
    
    
    def set_combobox_width_to_largest_item(self, combo: QtWidgets.QComboBox):
        font_metrics = QtGui.QFontMetrics(combo.font())
        max_width = 0

        for i in range(combo.count()):
            text = combo.itemText(i)
            text_width = font_metrics.horizontalAdvance(text)
            max_width = max(max_width, text_width)

        # Add extra space for the dropdown arrow and padding
        combo.setFixedWidth(max_width + 40)
    

    def get_instrument_and_number(self) -> tuple[str,str]:
        """
        Return a tuple with the instrument and number. Number can be 
        Example: ("oboe","2")
        """

        return (self.instrument.currentText(),self.number.currentText())



class InfiniteComboBoxesItem(QtWidgets.QFrame):

    def __init__(self,every_change_func,parent=None) -> None:
        super().__init__(parent)
        self.default_instrument_combos = 2
        self.max_copies = 20
        self.instruments:list[InstrumentAndNumber] = []
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
    def add_instrument_combo(self):
        l1 = InstrumentAndNumber()
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
