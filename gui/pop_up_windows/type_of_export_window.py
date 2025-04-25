from PyQt6 import QtWidgets,QtCore
from gui.error_window import ShowError
import enum

class TypeOfExport(enum.Enum):
    ALL_IN_ONE = 0
    BY_PIECES = 1
    BY_INSTRUMENTS = 2
    CANCELLED = 3 #When you close the window

"""
Pop up a window that shows a message with checkboxes
    is_by_istruments: tell if the split need to be by instruments.
                      If not, it need to be by pieces.

"""
class TypeOfExportWindow(QtWidgets.QDialog):
    def __init__(self,parent=None) -> None:
        super(TypeOfExportWindow,self).__init__(parent)

        self.type_of_export:TypeOfExport
        self.sort_alphabetically:bool = False
        self.ignore_preset_copies:bool = False

        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.setWindowTitle(self.tr("Exporting configuration"))

        _container_layout = QtWidgets.QVBoxLayout()

        #labels
        _warning_lbl = QtWidgets.QLabel(self.tr("How do you want to export the pdfs?"))
        
    
        #Type of export
        self._all_in_one_rb = QtWidgets.QRadioButton()
        self._all_in_one_rb.setText(self.tr("All in one."))
        self._all_in_one_rb.setToolTip(self.tr("Create one pdf with the instruments in the preset of all selected pieces.\nSorted by pieces (not by instruments)."))

        self._by_instruments_rb = QtWidgets.QRadioButton()
        self._by_instruments_rb.setText(self.tr("Splitted by instruments."))
        self._by_instruments_rb.setToolTip(self.tr("Create one pdf for each instrument in the preset.\nEach pdf has all the pieces in the list for one instrument.\nBy default the pdfs are created in the order that you added the pieces."))

        self._by_pieces_rb = QtWidgets.QRadioButton()
        self._by_pieces_rb.setText(self.tr("Splitted by pieces."))
        self._by_pieces_rb.setToolTip(self.tr("Create one pdf for each piece in the list.\nEach pdf has all the scores for the selected preset fro this piece.\n Each pdf has the instruments exported in the preset instrument order."))

        _export_types_group = QtWidgets.QButtonGroup()
        _export_types_group.addButton(self._all_in_one_rb)
        _export_types_group.addButton(self._by_instruments_rb)
        _export_types_group.addButton(self._by_pieces_rb)
        _export_types_group.buttonClicked.connect(self.manage_btns_enableability)


        self._sort_alphabetically_cb = QtWidgets.QCheckBox()
        self._sort_alphabetically_cb.setText(self.tr("Sort the pdfs alphabetically."))
        self._sort_alphabetically_cb.setToolTip(self.tr("Sort the pieces in each pdf alphabetically.\nOnly when exporting by instrument."))
        self._sort_alphabetically_cb.setEnabled(False)
        self._sort_alphabetically_cb.setStyleSheet("padding-left: 25px;")


        #Ignore preset copies
        self._ignore_preset_copies_cb = QtWidgets.QCheckBox()
        self._ignore_preset_copies_cb.setText(self.tr("Ignore preset's instrument copies."))
        self._ignore_preset_copies_cb.setToolTip(self.tr("Ignore the number of copies for each instrument in the preset and\ngenerate only one copy per instrument in the preset."))


        #Confirm button
        self._btn_confirm = QtWidgets.QPushButton(self.tr("Confirm")) #traducir
        self._btn_confirm.clicked.connect(self.confirm)

        _h_line = QtWidgets.QFrame()
        _h_line.setFrameShape(QtWidgets.QFrame.Shape.HLine)  # Set the frame shape to horizontal line
        _h_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # Optionally, add a shadow effect


        _container_layout.addWidget(_warning_lbl)
        _container_layout.addWidget(self._all_in_one_rb)
        _container_layout.addWidget(self._by_pieces_rb)
        _container_layout.addWidget(self._by_instruments_rb)
        _container_layout.addWidget(self._sort_alphabetically_cb)
        _container_layout.addWidget(_h_line)
        _container_layout.addWidget(self._ignore_preset_copies_cb)
        _container_layout.addWidget(self._btn_confirm)

        self.setLayout(_container_layout)

        self.exec()


    #Control the activation of the buttons
    def manage_btns_enableability(self):
        if self._by_instruments_rb.isChecked():
            self._sort_alphabetically_cb.setEnabled(True)
        else:
            self._sort_alphabetically_cb.setEnabled(False)
            self._sort_alphabetically_cb.setChecked(False)

    

    #Save the options in variables
    def confirm(self):
        if self._all_in_one_rb.isChecked():
            self.type_of_export = TypeOfExport.ALL_IN_ONE
        elif self._by_pieces_rb.isChecked():
            self.type_of_export = TypeOfExport.BY_PIECES
        elif self._by_instruments_rb.isChecked():
            self.type_of_export = TypeOfExport.BY_INSTRUMENTS
            self.sort_alphabetically = self._sort_alphabetically_cb.isChecked()
        else:
            ShowError.show_tooltip_error(self.tr("You need to select the type of export"),5000,self._btn_confirm)
            return #You need to select an option
        self.ignore_preset_copies = self._ignore_preset_copies_cb.isChecked()

        self.hide()
    

    def closeEvent(self, a0):
        self.type_of_export = TypeOfExport.CANCELLED
        self.hide()