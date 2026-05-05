from PyQt6 import QtWidgets,QtCore
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError
from frontend.pyqt.app.models.generated_models import ExportStrategyType
import enum


class GroupStrategyType(enum.Enum):
    by_instrument = "by instrument"
    by_piece = "by piece"

class TypeOfExportView(QtWidgets.QDialog):
    """
    This window is used to select the type of export for the PDF generation.
    It has the following options:

    """
    confirmed = QtCore.pyqtSignal()
    def __init__(self,parent=None) -> None:
        super(TypeOfExportView,self).__init__(parent)

        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.setWindowTitle(self.tr("Exporting configuration"))

        self.export_strategy:ExportStrategyType
        self.is_by_instruments:bool = False
        self.sort_alphabetically:bool = False
        self.ignore_preset_copies:bool = False
        self.add_piece_numbers:bool = False
        self.add_cover_page:bool = False
        self.cover_title:str = ""
        self.add_index:bool = False
        self.index_title:str = ""
        self.index_subtitle:str = ""
        self.add_blank_page_after_index:bool = False
                
        # Group strategy options
        _group_strategy_lbl = QtWidgets.QLabel(self.tr("Group strategy:"))

        self._group_strategy_combo = QtWidgets.QComboBox()
        self._group_strategy_combo.addItem(self.tr(GroupStrategyType.by_instrument.value))
        self._group_strategy_combo.addItem(self.tr(GroupStrategyType.by_piece.value))
        self._group_strategy_combo.setToolTip(self.tr("Select the strategy to group the pieces in the pdfs.\nBy instrument: Each pdf will have all the pieces for each instrument in the preset.\nBy piece: Each pdf will have all the instruments for each piece in the preset."))
        self._group_strategy_combo.setCurrentIndex(0)
        
        #Export strategy options
        _export_strategy_lbl = QtWidgets.QLabel(self.tr("Export strategy:"))

        self._all_in_one_rb = QtWidgets.QRadioButton()
        self._all_in_one_rb.setText(self.tr("All in one."))
        self._all_in_one_rb.setToolTip(self.tr("Create one pdf with all the instruments for the selected pieces.\nThe sorting order is defined by group strategy."))

        self._by_group_rb = QtWidgets.QRadioButton()
        self._by_group_rb.setText(self.tr("Merged by group."))
        self._by_group_rb.setToolTip(self.tr("Create one pdf for each group in the preset(The group is defined in group strategy).\nEach pdf has all the pieces in the list for one group.\nBy default, the pdfs are created in the order in which they are added."))

        self._splitted_rb = QtWidgets.QRadioButton()
        self._splitted_rb.setText(self.tr("Splitted by group."))
        self._splitted_rb.setToolTip(self.tr("Any pdf is merged. The pieces are exported following the group strategy using folderes but merging nothing."))

        self._sort_alphabetically_cb = QtWidgets.QCheckBox()
        self._sort_alphabetically_cb.setText(self.tr("Sort the pdfs alphabetically."))
        self._sort_alphabetically_cb.setToolTip(self.tr("Sort the pieces in each pdf alphabetically."))

        self._ignore_preset_copies_cb = QtWidgets.QCheckBox()
        self._ignore_preset_copies_cb.setText(self.tr("Ignore preset's instrument copies."))
        self._ignore_preset_copies_cb.setToolTip(self.tr("Ignore the number of copies for each instrument in the preset and\ngenerate only one copy per instrument in the preset."))

        self._add_cover_page_cb = QtWidgets.QCheckBox()
        self._add_cover_page_cb.stateChanged.connect(self.manage_cover_page_enableability)
        self._add_cover_page_cb.setText(self.tr("Add cover page to each pdf."))
        self._add_cover_page_cb.setToolTip(self.tr("Add a cover page to each pdf with the name of the instrument \nand an optional text for the name"))
        
        self._cover_title_le = QtWidgets.QLineEdit()
        self._cover_title_le.setPlaceholderText(self.tr("Cover title"))
        self._cover_title_le.setEnabled(False)
        self._cover_title_le.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._cover_title_le.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self._cover_title_le.setStyleSheet("margin-left: 25px;")

        self._add_index_cb = QtWidgets.QCheckBox()
        self._add_index_cb.stateChanged.connect(self.manage_index_enableability)
        self._add_index_cb.setText(self.tr("Add index to each pdf."))
        self._add_index_cb.setToolTip(self.tr("Add an index page at the beginning of each pdf with the list of pieces included."))

        self._index_title_le = QtWidgets.QLineEdit()
        self._index_title_le.setPlaceholderText(self.tr("Index title"))
        self._index_title_le.setEnabled(False)
        self._index_title_le.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._index_title_le.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self._index_title_le.setStyleSheet("margin-left: 25px;")

        self._index_subtitle_le = QtWidgets.QLineEdit()
        self._index_subtitle_le.setPlaceholderText(self.tr("Index subtitle"))
        self._index_subtitle_le.setEnabled(False)
        self._index_subtitle_le.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._index_subtitle_le.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self._index_subtitle_le.setStyleSheet("margin-left: 25px;")

        self._add_blank_page_after_index_cb = QtWidgets.QCheckBox()
        self._add_blank_page_after_index_cb.setText(self.tr("Add blank page after index."))
        self._add_blank_page_after_index_cb.setToolTip(self.tr("Add a blank page after the index page in each pdf."))
        self._add_blank_page_after_index_cb.setEnabled(False)
        self._add_blank_page_after_index_cb.setStyleSheet("padding-left: 25px;")

        self._add_piece_numbers_cb = QtWidgets.QCheckBox()
        self._add_piece_numbers_cb.setText(self.tr("Add number to each piece."))
        self._add_piece_numbers_cb.setToolTip(self.tr("Add a number in the bottom-right corner to \neach piece like the page number."))


        #Confirm button
        self._btn_confirm = QtWidgets.QPushButton(self.tr("Confirm")) #traducir
        self._btn_confirm.clicked.connect(self.confirm)

        _v_line = QtWidgets.QFrame()
        _v_line.setFrameShape(QtWidgets.QFrame.Shape.VLine)  # Set the frame shape to horizontal line
        _v_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)  # Optionally, add a shadow effect

        
        _container_layout = QtWidgets.QVBoxLayout()
        _central_zone_layout = QtWidgets.QHBoxLayout()
        _left_zone_layout = QtWidgets.QVBoxLayout()
        _right_zone_layout = QtWidgets.QVBoxLayout()

        _left_zone_layout.addWidget(_group_strategy_lbl)
        _left_zone_layout.addWidget(self._group_strategy_combo)
        _left_zone_layout.addWidget(_export_strategy_lbl)
        _left_zone_layout.addWidget(self._all_in_one_rb)
        _left_zone_layout.addWidget(self._by_group_rb)
        _left_zone_layout.addWidget(self._splitted_rb)
        
        _right_zone_layout.addWidget(self._sort_alphabetically_cb)
        _right_zone_layout.addWidget(self._ignore_preset_copies_cb)
        _right_zone_layout.addWidget(self._add_cover_page_cb)
        _right_zone_layout.addWidget(self._cover_title_le)
        _right_zone_layout.addWidget(self._add_index_cb)
        _right_zone_layout.addWidget(self._index_title_le)
        _right_zone_layout.addWidget(self._index_subtitle_le)
        _right_zone_layout.addWidget(self._add_blank_page_after_index_cb)
        _right_zone_layout.addWidget(self._add_piece_numbers_cb)

        _central_zone_layout.addLayout(_left_zone_layout)
        _central_zone_layout.addWidget(_v_line)
        _central_zone_layout.addLayout(_right_zone_layout)

        _container_layout.addLayout(_central_zone_layout)
        _container_layout.addWidget(self._btn_confirm)

        self.setLayout(_container_layout)


    def manage_cover_page_enableability(self):
        is_checked = self._add_cover_page_cb.isChecked()
        self._cover_title_le.setEnabled(is_checked)
        self._cover_title_le.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not is_checked)
        self._cover_title_le.setCursor(QtCore.Qt.CursorShape.IBeamCursor if is_checked else QtCore.Qt.CursorShape.ArrowCursor)

    def manage_index_enableability(self):
        is_checked = self._add_index_cb.isChecked()
        self._add_blank_page_after_index_cb.setEnabled(is_checked)
        if not is_checked:
            self._add_blank_page_after_index_cb.setChecked(False)
        self._index_title_le.setEnabled(is_checked)
        self._index_subtitle_le.setEnabled(is_checked)
        
        self._index_title_le.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not is_checked)
        self._index_subtitle_le.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, not is_checked)
        
        cursor = QtCore.Qt.CursorShape.IBeamCursor if is_checked else QtCore.Qt.CursorShape.ArrowCursor
        self._index_title_le.setCursor(cursor)
        self._index_subtitle_le.setCursor(cursor)
    
    #Save the options in variables
    def confirm(self):
        if self._all_in_one_rb.isChecked():
            self.export_strategy = ExportStrategyType.all_in_one
        elif self._by_group_rb.isChecked():
            self.export_strategy = ExportStrategyType.by_element
        elif self._splitted_rb.isChecked():
            self.export_strategy = ExportStrategyType.splitted
        else:
            ShowError.show_tooltip_error(self.tr("You need to select the export strategy"),5000,self._btn_confirm)
            return #You need to select an option
        
        if self._group_strategy_combo.currentText() == self.tr(GroupStrategyType.by_instrument.value):
            self.is_by_instruments = True
            print("Exporting by instrument")
        elif self._group_strategy_combo.currentText() == self.tr(GroupStrategyType.by_piece.value):
            self.is_by_instruments = False
        else:
            ShowError.show_tooltip_error(self.tr("You need to select the group strategy"),5000,self._group_strategy_combo)
            return #You need to select an option
        
            
        self.ignore_preset_copies = self._ignore_preset_copies_cb.isChecked()
        self.sort_alphabetically = self._sort_alphabetically_cb.isChecked()
        self.add_cover_page = self._add_cover_page_cb.isChecked()
        self.cover_title = self._cover_title_le.text()
        self.add_index = self._add_index_cb.isChecked()
        self.index_title = self._index_title_le.text()
        self.index_subtitle = self._index_subtitle_le.text()
        self.add_blank_page_after_index = self._add_blank_page_after_index_cb.isChecked()
        self.add_piece_numbers = self._add_piece_numbers_cb.isChecked()

        self.confirmed.emit()

        self.accept()
    

    def closeEvent(self, a0):
        self.hide()