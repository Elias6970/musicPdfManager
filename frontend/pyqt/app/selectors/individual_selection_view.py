from PyQt6 import QtWidgets,QtGui,QtCore
from app.config.constants import REFRESH_IMG_PATH
from app.elements.score_search_bar import ScoreSearchBar
from app.elements.previwer.previewer import Preview
from app.elements.status_console import StatusConsole
from app.elements.list_items.status_console_item_two_texts import StatusConsoleItemWithTwoTexts

class IndividualSelectionView(QtWidgets.QWidget):
    MAX_COPIES = 20
    NO_SCORES_TEXT = "NO SCORES"
    instrument_changed = QtCore.pyqtSignal(str)
    instrument_navigation_requested = QtCore.pyqtSignal(int)
    quick_add_requested = QtCore.pyqtSignal(int)
    add_score_signal = QtCore.pyqtSignal(str,str,int)
    generate_pdf_signal = QtCore.pyqtSignal()
    refresh_requested = QtCore.pyqtSignal()
    only_digitalized_changed = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(IndividualSelectionView,self).__init__()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)


        container_layout = QtWidgets.QHBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        #This extra layout Align the left zone to the top 
        left_zone_layout = QtWidgets.QVBoxLayout()
        left_zone_layout.addWidget(self.create_left_zone())
        left_zone_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        container_layout.addLayout(left_zone_layout)
        container_layout.addWidget(self.create_preview())

        self.setLayout(container_layout)

        self._install_keyboard_event_filters(self)
        application = QtWidgets.QApplication.instance()
        if application is not None:
            application.installEventFilter(self)


        #self.setGeometry(100,80,200,200)




    #Create the zone with a combo box to the num of copies, add and create pdf buttons
    def create_add_zone(self):
        obj = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(50)
        self.num_copies.addItems([str(i+1) for i in range(self.MAX_COPIES)])
        
        self.btn_add_score = QtWidgets.QPushButton(self.tr("Add"))
        self.btn_create_pdf = QtWidgets.QPushButton(self.tr("Create Pdf"))

        self.btn_add_score.setEnabled(False)
        self.btn_create_pdf.setEnabled(False)

        self.btn_add_score.clicked.connect(self.pre_add_score)
        self.btn_create_pdf.clicked.connect(self.generate_pdf_signal.emit)

        layout.addWidget(self.num_copies)
        layout.addWidget(self.btn_add_score)
        layout.addWidget(self.btn_create_pdf)

        obj.setLayout(layout)
        return obj


    #Create two buttons in a horizontal layout
    def create_preview_buttons(self):
        obj = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        
        self.btn_mv_back_preview = QtWidgets.QPushButton("<")
        self.btn_mv_forward_preview = QtWidgets.QPushButton(">")

        hbox.addWidget(self.btn_mv_back_preview)
        hbox.addWidget(self.btn_mv_forward_preview)
        obj.setLayout(hbox)
        obj.setMaximumHeight(40)
        return obj


    #Create the up-left zone of the program(Two search bars, two labels and two buttons)
    def create_search_bars(self):
        search_bars = QtWidgets.QWidget()
        select_zone_layout = QtWidgets.QVBoxLayout()
        search_bar_layout = QtWidgets.QHBoxLayout()
        check_box_layout = QtWidgets.QHBoxLayout()
        #Space
        select_zone_layout.setContentsMargins(0,0,0,0)
        search_bar_layout.setContentsMargins(0,0,0,0)
        
        #Refresh button
        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.clicked.connect(self.refresh_requested.emit)

        try:
            self.refresh_button.setIcon(QtGui.QIcon(REFRESH_IMG_PATH))
        except Exception:
            pass

        #Search bar
        self.piece_search_bar = ScoreSearchBar()
        
        #Rest of widgets
        self.only_digitalized_cb = QtWidgets.QCheckBox()
        self.only_digitalized_cb.toggled.connect(self.only_digitalized_changed.emit)
        only_digitalized_lbl = QtWidgets.QLabel(self.tr("Only digitalized")) #traducir
        self.piece_lbl = QtWidgets.QLabel()
        self.part_combo_box = QtWidgets.QComboBox()
        
        #self.part_combo_box.currentIndexChanged.connect(lambda: self.update_preview(self.piece_search_bar.text(),self.part_combo_box.currentText()))
        self.part_combo_box.currentIndexChanged.connect(lambda: self.instrument_changed.emit(self.part_combo_box.currentText()))
        self.part_combo_box.setEnabled(False)
        
        self.add_create_buttons = self.create_add_zone()
        

        #Add the widgets to the layout
        search_bar_layout.addWidget(self.refresh_button)
        search_bar_layout.addWidget(self.piece_search_bar)
        
        check_box_layout.addWidget(self.only_digitalized_cb)
        check_box_layout.addWidget(only_digitalized_lbl)
        check_box_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        select_zone_layout.addLayout(search_bar_layout)
        select_zone_layout.addLayout(check_box_layout)
        select_zone_layout.addWidget(self.piece_lbl)
        select_zone_layout.addWidget(self.part_combo_box)
        select_zone_layout.addWidget(self.add_create_buttons)
        
        search_bars.setLayout(select_zone_layout)
    
        return search_bars    
    

    #Create the preview
    def create_preview(self):
        preview = QtWidgets.QWidget()
        preview_layout = QtWidgets.QVBoxLayout()

        preview_layout.setSpacing(0)
        preview_layout.setContentsMargins(30,0,0,0)

        self.preview = Preview(self)
        
        scroll_arrows = self.create_preview_buttons()
        preview_layout.addWidget(self.preview)
        preview_layout.addWidget(scroll_arrows)
        preview.setLayout(preview_layout)

        return preview


    #Create the layout of all the left zone(search bars+scroll area)
    def create_left_zone(self):
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout()
        self.status_console:StatusConsole = StatusConsole()
        
        left_layout.addWidget(self.create_search_bars())
        left_layout.addWidget(self.status_console)
        self.setMinimumHeight(550)
        left.setLayout(left_layout)
        left.setFixedWidth(300)

        return left

#####################################################################
#----------------------------APP LOGIC -----------------------------#
#####################################################################
    def pre_add_score(self):
        """Pre function to add score. It checks if the combo box is enabled before emitting the signal to add the score."""
        if self.part_combo_box.isEnabled():
            self.add_score_signal.emit(self.piece_lbl.text(),
                                       self.part_combo_box.currentText(),
                                       int(self.num_copies.currentText()))

    def eventFilter(self, a0, a1):
        """
        Event filter to handle key press events for navigation and quick add functionality.
        Buttons 1-9 will trigger the quick add signal with the corresponding number of copies.
        Up and Down arrow keys will trigger the instrument navigation signal.
        """
        if (not isinstance(a1, QtGui.QKeyEvent)
                or a1.type() != QtCore.QEvent.Type.KeyPress
                or a1.isAutoRepeat()):
            return super().eventFilter(a0, a1)

        event = a1
        focus_widget = QtWidgets.QApplication.focusWidget()
        if (focus_widget is None
                or (focus_widget is not self
                    and not self.isAncestorOf(focus_widget))):
            return super().eventFilter(a0, event)

        if not self.part_combo_box.isEnabled():
            return super().eventFilter(a0, event)

        if event.key() == QtCore.Qt.Key.Key_Up:
            self.instrument_navigation_requested.emit(-1)
            return True

        if event.key() == QtCore.Qt.Key.Key_Down:
            self.instrument_navigation_requested.emit(1)
            return True

        if (focus_widget is self.piece_search_bar
                or (focus_widget is not None
                    and self.piece_search_bar.isAncestorOf(focus_widget))):
            return super().eventFilter(a0, event)

        number_keys: dict[int, int] = {
            int(QtCore.Qt.Key.Key_1): 1,
            int(QtCore.Qt.Key.Key_2): 2,
            int(QtCore.Qt.Key.Key_3): 3,
            int(QtCore.Qt.Key.Key_4): 4,
            int(QtCore.Qt.Key.Key_5): 5,
            int(QtCore.Qt.Key.Key_6): 6,
            int(QtCore.Qt.Key.Key_7): 7,
            int(QtCore.Qt.Key.Key_8): 8,
            int(QtCore.Qt.Key.Key_9): 9,
        }
        copies = number_keys.get(int(event.key()))
        if copies is not None:
            self.quick_add_requested.emit(copies)
            return True

        return super().eventFilter(a0, event)



    def _install_keyboard_event_filters(self, widget: QtWidgets.QWidget):
        """Sets up event filters for the given widget and all its child widgets to handle keyboard events."""
        widget.installEventFilter(self)
        for child in widget.findChildren(QtWidgets.QWidget):
            child.installEventFilter(self)

    
    def move_instrument_selection(self, step: int):
        """
        Move the selection of the instruments combo box up or down by the given step.
        """
        current_index = self.part_combo_box.currentIndex()
        next_index = max(
            0,
            min(current_index + step, self.part_combo_box.count() - 1),
        )
        self.part_combo_box.setCurrentIndex(next_index)
    
    #Update the autocompleter list of the search bar
    def update_search_bar_autocompleter(self, pieces:list[str]):
        self.piece_search_bar.update_autocompleter_scores(pieces)

    def set_piece_lbl(self,text:str):
        self.piece_lbl.setText(text)

    def set_combo_box_instruments(self,instruments:list[str]):
        """
        Set the instruments in the combo box and enable it
        """
        self.part_combo_box.setEnabled(True)
        self.btn_add_score.setEnabled(True)
        self.part_combo_box.clear()
        self.part_combo_box.addItems(instruments)
        self.part_combo_box.setCurrentIndex(0)
    
    def disable_instruments_combo_box_no_scores(self):
        """
        Disable instrumets combo box while no scores
        """
        self.part_combo_box.setEnabled(False)
        self.btn_add_score.setEnabled(False)
        self.part_combo_box.insertItem(0,self.tr(self.NO_SCORES_TEXT))

    def clean_instruments_combo_box(self):
        self.part_combo_box.clear()
        self.part_combo_box.setEnabled(False)
        self.btn_add_score.setEnabled(False)


    def add_item_to_scroll(self, id:str, piece_name:str, instrument:str, copies:int, remove_from_list):
        """
        Add an item to the scroll area with the piece name, instrument and num of copies. 
        It also has a button to remove the item from the scroll and the list of added scores.
        """
        item = StatusConsoleItemWithTwoTexts(piece_name,
                             instrument,
                             copies,
                             id,
                                             self.remove_status_console_item,
                             remove_from_list)
        self._install_keyboard_event_filters(item)
        self.status_console.add_item(item)

    def remove_status_console_item(self, item):
        self.status_console.remove_item(item)
        QtCore.QTimer.singleShot(0, self.setFocus)

    #Display a window to select a location to save a pdf
    def dialog_window_select_new_pdf(self):
        file_dialog = QtWidgets.QFileDialog()
        
        file_dialog.setWindowTitle(self.tr("Select Folder and File Name")) #traducir
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)  # Set the dialog to save mode
        file_dialog.setDefaultSuffix(".pdf")

        if file_dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            return file_dialog.selectedFiles()[0]
        else:
            return ""


    #Refresh the list of pieces and delete the info in the printer  
    def refresh(self):
        self.status_console.clear()
        self.status_console.update()
        self.piece_search_bar.clear()
        self.piece_lbl.clear()
        self.num_copies.setCurrentIndex(0)
        self.part_combo_box.clear()
        self.part_combo_box.setEnabled(False)
        self.btn_add_score.setEnabled(False)
        self.btn_create_pdf.setEnabled(False)

        #Preview is cleared in the preview controller (called by refresh in the controller)


    def is_only_digitalized(self):
        return self.only_digitalized_cb.isChecked()

    #Change the preview image
    def change_preview_img(self, bytes_img:bytes|None=None):
        self.preview.set_image_from_bytes(bytes_img)

    def show_pdf_saved_message(self,msg:str):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(self.tr("PDF Saved"))  #traducir
        msg_box.setText(msg)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg_box.exec()