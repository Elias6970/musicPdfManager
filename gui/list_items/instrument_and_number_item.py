from PyQt6 import QtWidgets, QtGui
from classes.constants.instruments_names import *

class InstrumentAndNumberItem(QtWidgets.QFrame):
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

    def __init__(self, instrument:str|None=None, number:str|int|None=None, parent=None):
        super().__init__(parent)
        self.max_number = 5

        self.instrument = QtWidgets.QComboBox()
        self.instrument.addItem("")
        self.instrument.addItems(InstrumentAndNumberItem.INSTRUMENT_NAMES)
        self.instrument.setCurrentIndex(-1)
        self.instrument.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.set_combobox_width_to_largest_item(self.instrument)
        

        self.number = QtWidgets.QComboBox()
        self.number.addItem("")
        self.number.addItems([str(i) for i in range(1,self.max_number+1)])
        self.number.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        self.number.setFixedWidth(40)

        _layout = QtWidgets.QHBoxLayout()
        _layout.addWidget(self.instrument)
        _layout.addWidget(self.number)

        self.setLayout(_layout)
        self.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setFixedWidth(self.instrument.width() + self.number.width() + 30)

        #Fill the comboboxes
        if instrument != None and instrument in InstrumentAndNumberItem.INSTRUMENT_NAMES:
            self.instrument.setCurrentText(instrument)
        if number != None and (number.strip() == '' or int(number) <= self.max_number):
            self.number.setCurrentText(str(number))

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

