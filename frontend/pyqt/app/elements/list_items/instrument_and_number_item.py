from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import pyqtSignal

class InstrumentAndNumberItem(QtWidgets.QFrame):
    changed = pyqtSignal(object)
    
    def __init__(self, instrument_names: list[str], instrument:str|None=None, number:str|int|None=None, parent=None):
        super().__init__(parent)
        self.max_number = 5

        self.instrument = QtWidgets.QComboBox()
        self.instrument.addItem("")
        self.instrument.addItems(instrument_names)
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
        if instrument != None and instrument in instrument_names:
            self.instrument.setCurrentText(instrument)
        if number != None and (str(number).strip() == '' or int(number) <= self.max_number):
            self.number.setCurrentText(str(number))

        self.instrument.currentIndexChanged.connect(self._emit_changed)
        self.number.currentIndexChanged.connect(self._emit_changed)

    def _emit_changed(self):
        self.changed.emit(self)

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
        Return a tuple with the instrument and number. Number can be '' if not selected
        Example: ("oboe","2")
        """
        return (self.instrument.currentText(),self.number.currentText())

