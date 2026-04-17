from PyQt6 import QtWidgets, QtCore, QtGui
from frontend.pyqt.app.config.constants import REFRESH_IMG_PATH
from frontend.pyqt.app.pop_up_windows.error.error_window import Error_window, ShowError
from frontend.pyqt.app.elements.status_console import StatusConsole
from frontend.pyqt.app.elements.score_search_bar import ScoreSearchBar
from frontend.pyqt.app.elements.list_items.status_console_item_two_texts import StatusConsoleItemWithTwoTexts
from frontend.pyqt.app.elements.previwer.previewer import Preview

from backend.app.files_management.dir import Dir_Error
from backend.app.validate import Validate
from backend.app.presets.pieces_preset.pieces_preset import PiecesPreset

class MultipleSelectionView(QtWidgets.QWidget):
    MAX_COPIES = 20
    instrument_changed = QtCore.pyqtSignal(str)
    add_piece_signal = QtCore.pyqtSignal(str,str,int)
    generate_pdf_signal = QtCore.pyqtSignal()
    refresh_requested = QtCore.pyqtSignal()
    only_digitalized_changed = QtCore.pyqtSignal(bool)
    instruments_preset_changed = QtCore.pyqtSignal(str)
    save_pieces_preset_signal = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        
        # #Init the Archive 
        # self.archive = archive
        # self.printer = PresetsPrinter()
        # self.preset_manager = PresetManager() #Mange the instruments presets
        # self.preset_manager.load()
        # self.piece_preset_manager = PiecesPresetManager() #Manage the pieces presets
        # self.piece_preset_manager.load()

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

        #self.set_presets()

        #self.setGeometry(100,80,200,200)




    #Create the zone with a combo box to the num of copies, add and create pdf buttons
    def create_add_zone(self):
        obj = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        
        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(50)
        self.num_copies.addItems([str(i+1) for i in range(MultipleSelectionView.MAX_COPIES)])
        self.num_copies.setToolTip(self.tr("Number of copies"))
        
        self.btn_add_piece = QtWidgets.QPushButton(self.tr("Add")) #traducir
        self.btn_create_pdf = QtWidgets.QPushButton(self.tr("Create Pdf")) #traducir

        self.btn_add_piece.clicked.connect(lambda: self.add_piece_signal.emit(
            self.piece_search_bar.text(),
            self.presets_combo_box.currentText(),
            int(self.num_copies.currentText())
        ))
        self.btn_add_piece.setEnabled(False)
        
        self.btn_create_pdf.clicked.connect(self.generate_pdf_signal.emit)
        self.btn_create_pdf.setEnabled(False)

        layout.addWidget(self.num_copies)
        layout.addWidget(self.btn_add_piece)
        layout.addWidget(self.btn_create_pdf)

        obj.setLayout(layout)
        return obj


    #Create a vertial layout with a instruments search bar and
    # two buttons in a horizontal layout
    def create_preview_buttons(self):
        obj = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()
        
        self.instruments_combo_box = QtWidgets.QComboBox()
        self.instruments_combo_box.setMaximumHeight(20)
        self.instruments_combo_box.currentTextChanged.connect(lambda: self.instrument_changed.emit(self.instruments_combo_box.currentText()))
        self.instruments_combo_box.setEnabled(False)

        self.btn_mv_back_preview = QtWidgets.QPushButton("<")
        self.btn_mv_forward_preview = QtWidgets.QPushButton(">")
        
        hbox.addWidget(self.btn_mv_back_preview)
        hbox.addWidget(self.btn_mv_forward_preview)

        vbox.addWidget(self.instruments_combo_box)
        vbox.addLayout(hbox)

        obj.setLayout(vbox)
        obj.setMaximumHeight(70)
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
        self.only_digitalized_cb.clicked.connect(self.only_digitalized_changed.emit) #TODO
        only_digitalized_lbl = QtWidgets.QLabel(self.tr("Only digitalized"))
        self.piece_lbl = QtWidgets.QLabel()


        presets_lbl = QtWidgets.QLabel(self.tr("Preset")+":")
        presets_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        presets_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        self.presets_combo_box = QtWidgets.QComboBox()
        self.presets_combo_box.setToolTip(self.tr("Select the preset"))
        self.presets_combo_box.setPlaceholderText(" ")
        self.presets_combo_box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.presets_combo_box.currentTextChanged.connect(self.instruments_preset_changed.emit)

        self.hbox_presets = QtWidgets.QHBoxLayout()
        self.hbox_presets.addWidget(presets_lbl)
        self.hbox_presets.addWidget(self.presets_combo_box)



        self.add_create_buttons = self.create_add_zone()
        

        #Add the widgets to the layout
        search_bar_layout.addWidget(self.refresh_button)
        search_bar_layout.addWidget(self.piece_search_bar)
        
        check_box_layout.addWidget(self.only_digitalized_cb)
        check_box_layout.addWidget(only_digitalized_lbl)
        check_box_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        select_zone_layout.addLayout(self.hbox_presets)
        select_zone_layout.addSpacing(10)
        select_zone_layout.addLayout(search_bar_layout)
        select_zone_layout.addLayout(check_box_layout)
        select_zone_layout.addWidget(self.piece_lbl)
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



    def set_piece_lbl(self,text:str):
        self.piece_lbl.setText(text)


    def clean_instruments_combo_box(self):
        self.instruments_combo_box.clear()
        self.instruments_combo_box.setEnabled(False)
        self.btn_add_piece.setEnabled(False)



    def is_only_digitalized(self):
        return self.only_digitalized_cb.isChecked()

    
    def set_combo_box_instruments(self,instruments:list[str]):
        """
        Set the instruments in the combo box and enable it
        """
        self.instruments_combo_box.setEnabled(True)
        self.instruments_combo_box.clear()
        self.instruments_combo_box.addItems(instruments)
        self.instruments_combo_box.setCurrentIndex(0)

        if self.presets_combo_box.currentIndex() != -1:
            self.btn_add_piece.setEnabled(True)

    def set_instrument_preset_in_combo_box(self, preset_name:str):
        """
        Set the instrument preset in the combo box and enable it
        """
        combobox_id = self.presets_combo_box.findText(preset_name)
        if combobox_id != -1:
            self.presets_combo_box.setCurrentIndex(combobox_id)
            self.presets_combo_box.setEnabled(True)
        else:
            ShowError.show_tooltip_error(self.tr(f"Preset {preset_name} not found in the list"),5000,self.presets_combo_box)
            self.presets_combo_box.setCurrentIndex(-1)
            self.presets_combo_box.setEnabled(False)


    def disable_instruments_combo_box_no_scores(self):
        """
        Disable instrumets combo box while no scores
        """
        self.instruments_combo_box.setEnabled(False)
        self.btn_add_piece.setEnabled(False)
        self.instruments_combo_box.insertItem(0,self.tr("NO SCORES"))
    
    def set_combo_box_presets(self, presets:list[str]):
        """
        Set the presets in the combo box and enable it
        """
        self.presets_combo_box.setEnabled(True)
        self.presets_combo_box.clear()
        self.presets_combo_box.addItems(presets)
        self.presets_combo_box.setCurrentIndex(-1)

    def disable_presets_combo_box_no_presets(self):
        """
        Disable presets combo box while no presets
        """
        self.presets_combo_box.setEnabled(False)
        self.presets_combo_box.insertItem(0,self.tr("NO PRESETS"))

    def add_item_to_status_console(self, id:str, piece_name:str, preset_name:str, copies:int, remove_from_list):
        """
        Add an item to the scroll area with the piece name, preset_name and num of copies. 
        It also has a button to remove the item from the scroll and the list of added scores.
        """
        self.status_console.add_item(StatusConsoleItemWithTwoTexts(piece_name,
                                            preset_name,
                                            copies,
                                            id,
                                            self.status_console.remove_item,
                                            remove_from_list))

    #Display a window to select a location to save a pdf
    def dialog_window_select_exporting_path(self):
        return QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("Select Folder to export"))

  
    def refresh(self):
        """
        Refresh all the view elements to the initial state
        """
        self.presets_combo_box.clear()
        self.piece_search_bar.clear()
        self.status_console.clear()
        self.instruments_combo_box.clear()
        self.num_copies.setCurrentIndex(0)
        #The preview is cleaned in the preview controller

    def show_message(self, title:str, msg:str):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
        #Update the autocompleter list of the search bar
    def update_search_bar_autocompleter(self, pieces:list[str]):
        self.piece_search_bar.update_autocompleter_scores(pieces)
    

    def show_get_piece_preset_name(self):
        """
        Show a dialog to get the name of the pieces preset to save, and trigger the save signal.
        If the user cancels the dialog nothing happens
        """
        preset_name, ok =QtWidgets.QInputDialog.getText(self, self.tr("Save pieces preset"), self.tr("Preset name:"))
        if ok and preset_name:
            self.save_pieces_preset_signal.emit(preset_name)
    
###########################OLDDDDDDDDDDDDDD@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@J