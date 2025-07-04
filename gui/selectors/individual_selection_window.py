from PyQt6 import QtWidgets,QtGui,QtCore
from classes.constants.constants import MAX_COPIES,REFRESH_IMG_PATH
from classes.files_management.archive import Archive
from classes.files_management.dir import Dir_Error
from classes.validate import Validate
from classes.printers.default_printer import DefaultPrinter
from classes.error import NoScoresException
from classes.preview_controller import Preview_controller
from classes.constants.constants import DIR_SCORES
from gui.error_window import Error_window
from gui.status_console import StatusConsole
from gui.score_search_bar import ScoreSearchBar
from gui.list_items.status_console_item_two_texts import StatusConsleItemWithTwoTexts
from gui.previewer import Preview

import os

class IndividualSelectionWindow(QtWidgets.QWidget):
    def __init__(self,archive:Archive):
        super(IndividualSelectionWindow,self).__init__()


        #Init the Archive 
        self.archive = archive
        self.printer = DefaultPrinter()

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


        #self.setGeometry(100,80,200,200)




    #Create the zone with a combo box to the num of copies, add and create pdf buttons
    def create_add_zone(self):
        obj = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()

        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(50)
        self.num_copies.addItems([str(i+1) for i in range(MAX_COPIES)])
        
        btn1 = QtWidgets.QPushButton(self.tr("Add")) #traducir
        btn2 = QtWidgets.QPushButton(self.tr("Create Pdf")) #traducir

        btn1.clicked.connect(self.add_score)
        btn2.clicked.connect(self.create_pdf)

        layout.addWidget(self.num_copies)
        layout.addWidget(btn1)
        layout.addWidget(btn2)

        obj.setLayout(layout)
        return obj


    #Create two buttons in a horizontal layout
    def create_preview_buttons(self):
        obj = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        
        self.btn_mv_back_preview = QtWidgets.QPushButton("<")
        self.btn_mv_forward_preview = QtWidgets.QPushButton(">")
        
        self.btn_mv_back_preview.clicked.connect(self.mv_back_preview)
        self.btn_mv_forward_preview.clicked.connect(self.mv_forward_preview)

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
        self.refresh_button.clicked.connect(self.refresh)

        try:
            self.refresh_button.setIcon(QtGui.QIcon(REFRESH_IMG_PATH))
        except Exception:
            pass

        #Search bar
        self.piece_search_bar = ScoreSearchBar(self.archive.pieces.get_parsed_names(),self.set_option_of_instruments)

        #Rest of widgets
        self.only_digitalized_cb = QtWidgets.QCheckBox()
        self.only_digitalized_cb.clicked.connect(self.only_digitalized)
        only_digitalized_lbl = QtWidgets.QLabel(self.tr("Only digitalized")) #traducir
        self.piece_lbl = QtWidgets.QLabel()
        self.part_combo_box = QtWidgets.QComboBox()
        
        self.part_combo_box.currentIndexChanged.connect(lambda: self.update_preview(self.piece_search_bar.text(),self.part_combo_box.currentText()))
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
        self.scroll:StatusConsole = StatusConsole()
        
        left_layout.addWidget(self.create_search_bars())
        left_layout.addWidget(self.scroll)
        self.setMinimumHeight(550)
        left.setLayout(left_layout)
        left.setFixedWidth(300)

        return left

#####################################################################
#----------------------------APP LOGIC -----------------------------#
#####################################################################

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self):
        self.archive.update_pieces()
        self.piece_search_bar.update_autocompleter_scores(self.archive.pieces.get_parsed_names())
    
    
    #Set the option of the instruments to the combo box
    def set_option_of_instruments(self,text):
        #Clear the old options
        for i in range(self.part_combo_box.count()):
                self.part_combo_box.removeItem(0)

        #set instruments
        piece = Validate.check_if_exist_dir(text,self.archive.pieces.get_parsed_names())
        if not isinstance(piece,Dir_Error):
            try:
                if piece.search_and_set_path():
                    print(piece.path)
                    print(piece.get_scores())
                    scores = piece.get_scores()
                    #Raise the error if the scores dir is empty
                    if not scores:
                        raise NoScoresException()
                    
                    self.part_combo_box.setEnabled(True)
                    self.part_combo_box.addItems(piece.get_scores())
                    self.piece_lbl.setText(piece.name)
                    self.printer.actual_piece = piece
            
            #if the piece is not in the digital archive
            except FileNotFoundError:
                self.part_combo_box.setEnabled(False)
                self.part_combo_box.insertItem(0,self.tr("NO DIGITALIZED")) #TRADUCIR
            except NoScoresException:
                self.part_combo_box.setEnabled(False)
                self.part_combo_box.insertItem(0,self.tr("NO SCORES")) #TRADUCIR



    #Add the score to the list of added scores an update it in the labels list
    def add_score(self):
        #Is throw if actual piece doesn't exist
        try:
            validation = Validate.validate_selection(self.printer.actual_piece.name,self.archive.pieces.get_parsed_names())
        except AttributeError:
            return
        
        if self.part_combo_box.isEnabled() and validation:

            path=os.path.join(self.printer.actual_piece.path,DIR_SCORES,self.part_combo_box.currentText())
            copies=int(self.num_copies.currentText())
            self.printer.add(path,copies)

            #Update the labels of the down scores
            self.scroll.add_item(StatusConsleItemWithTwoTexts(self.printer.actual_piece.name,
                                                  self.part_combo_box.currentText(),
                                                  int(self.num_copies.currentText()),
                                                  self.printer.items[-1].id,
                                                  self.scroll.remove_item,
                                                  self.printer.remove))
    

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


    #Create one pdf with all the selected pdfs merged
    def create_pdf(self):     
        try:
            if self.printer.items:
                pdf_path = self.dialog_window_select_new_pdf()
                self.printer.export(pdf_path)
        
        except Exception as e:
            Error_window.print_error(e)


    #Refresh the list of pieces and delete the info in the printer  
    def refresh(self):
        self.scroll.clear()
        self.scroll.update()
        self.piece_search_bar.clear()
        self.piece_lbl.clear()
        self.num_copies.setCurrentIndex(0)
        
        #Printer
        self.printer = DefaultPrinter()
        self.archive.update_pieces()
        #Preview
        self.preview.clear()


    #Controlls the pieces showed in the search bar
    def only_digitalized(self):
        if self.only_digitalized_cb.isChecked():
            self.piece_search_bar.update_autocompleter_scores(self.archive.pieces.get_digitalized_parsed_names())
        else:
            self.piece_search_bar.update_autocompleter_scores(self.archive.pieces.get_parsed_names())

    
    #Move to the previous preview page 
    def mv_back_preview(self):
        try:
            self.preview_controller.previous_page()
            self.check_mv_btns_enableability()
            self.change_preview_img()
        except Exception as e:
            pass
            
    #Move to the next preview page
    def mv_forward_preview(self):
        try:
            self.preview_controller.next_page()
            self.check_mv_btns_enableability()
            self.change_preview_img()
        except Exception:
            pass

    #Check if move preview buttons must be enabled or disabled
    def check_mv_btns_enableability(self):
        if self.preview_controller.is_in_first_page():
            self.btn_mv_back_preview.setEnabled(False)
        else:
            self.btn_mv_back_preview.setEnabled(True)
        if self.preview_controller.is_in_last_page():
            self.btn_mv_forward_preview.setEnabled(False)
        else:
            self.btn_mv_forward_preview.setEnabled(True)

    #Change the preview image
    def change_preview_img(self):
        self.preview.set_image(self.preview_controller.get_image())
    
    
    #Manage the preview controller
    def update_preview(self,piece_parsed_name:str,instrument:str) -> None:
        #Check if a piece and instrument is selected
        piece = Validate.check_if_exist_dir(self.piece_search_bar.text(),self.archive.pieces.get_parsed_names())
        if not isinstance(piece,Dir_Error):
            try:
                if not piece.get_scores():
                    raise NoScoresException()
                try:
                    if piece_parsed_name == self.preview_controller.piece_parsed_name:
                        self.preview_controller.instrument = instrument
                        self.preview_controller.update_path()
                    else:
                        self.preview_controller = Preview_controller(piece_parsed_name,instrument)
                except Exception:
                    self.preview_controller = Preview_controller(piece_parsed_name,instrument)

                self.change_preview_img()
            except NoScoresException:
                pass
            except FileNotFoundError:
                pass
            except Exception as e:
                print(type(e)," ",e)

    

