from PyQt6 import QtWidgets,QtGui,QtCore
from backend.app.constants.constants import MAX_COPIES
from backend.app.custom_order.instrument_sorter import InstrumentSorter
from backend.app.files_management.archive import Archive
from backend.app.files_management.dir import Dir
from backend.app.files_management.dir import Dir_Error
from backend.app.presets.preset_resolver_states import PresetResolverStates
from backend.app.validate import Validate
from backend.app.printers.presets_printer import PresetsPrinter
from backend.app.presets.preset import Preset
from backend.app.error import NoScoresException, MoreScoresThanPresetsException
from backend.app.preview_controller import Preview_controller
from backend.app.presets.preset_manager import PresetManager
from backend.app.presets.pieces_preset.pieces_preset_manager import PiecesPresetManager
from backend.app.presets.pieces_preset.pieces_preset import PiecesPreset
from frontend_pyqt.config.constants import REFRESH_IMG_PATH
from frontend_pyqt.pop_up_windows.error_window import Error_window, ShowError
from frontend_pyqt.pop_up_windows.type_of_export_window import TypeOfExportWindow, TypeOfExport
from frontend_pyqt.presets.resolve_not_matched_presets import ResolveNotMatchedPresets
from frontend_pyqt.pop_up_windows.yes_no_window import YesNoWindow
from frontend_pyqt.elements.status_console import StatusConsole
from frontend_pyqt.elements.score_search_bar import ScoreSearchBar
from frontend_pyqt.elements.list_items.status_console_item_two_texts import StatusConsoleItemWithTwoTexts
from frontend_pyqt.elements.previewer import Preview
import os

class MultipleSelectionWindow(QtWidgets.QWidget):
    def __init__(self,archive:Archive):
        super(MultipleSelectionWindow,self).__init__()


        #Init the Archive 
        self.archive = archive
        self.printer = PresetsPrinter()
        self.preset_manager = PresetManager() #Mange the instruments presets
        self.preset_manager.load()
        self.piece_preset_manager = PiecesPresetManager() #Manage the pieces presets
        self.piece_preset_manager.load()

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

        self.set_presets()

        #self.setGeometry(100,80,200,200)




    #Create the zone with a combo box to the num of copies, add and create pdf buttons
    def create_add_zone(self):
        obj = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        
        self.num_copies = QtWidgets.QComboBox()
        self.num_copies.setFixedWidth(50)
        self.num_copies.addItems([str(i+1) for i in range(MAX_COPIES)])
        self.num_copies.setToolTip(self.tr("Number of copies"))
        
        self.btn_add = QtWidgets.QPushButton(self.tr("Add")) #traducir
        self.btn_confirm = QtWidgets.QPushButton(self.tr("Create Pdf")) #traducir

        self.btn_add.clicked.connect(self.add_score_frontend_pyqt)
        self.btn_confirm.clicked.connect(self.create_pdf)

        layout.addWidget(self.num_copies)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_confirm)

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
        self.instruments_combo_box.currentTextChanged.connect(lambda: self.update_preview(self.piece_search_bar.text(),self.instruments_combo_box.currentText()))
        self.instruments_combo_box.setEnabled(False)

        self.btn_mv_back_preview = QtWidgets.QPushButton("<")
        self.btn_mv_forward_preview = QtWidgets.QPushButton(">")
        
        self.btn_mv_back_preview.clicked.connect(self.mv_back_preview)
        self.btn_mv_forward_preview.clicked.connect(self.mv_forward_preview)

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
        self.refresh_button.clicked.connect(self.refresh)

        try:
            self.refresh_button.setIcon(QtGui.QIcon(REFRESH_IMG_PATH))
        except Exception:
            pass

        #Search bar
        self.piece_search_bar = ScoreSearchBar(self.archive.pieces.get_parsed_names(),self.set_options_of_instruments)

        #Rest of widgets
        self.only_digitalized_cb = QtWidgets.QCheckBox()
        self.only_digitalized_cb.clicked.connect(self.only_digitalized)
        only_digitalized_lbl = QtWidgets.QLabel(self.tr("Only digitalized")) #traducir
        self.piece_lbl = QtWidgets.QLabel()


        presets_lbl = QtWidgets.QLabel(self.tr("Preset")+":")
        presets_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        presets_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        self.presets_combo_box = QtWidgets.QComboBox()
        self.presets_combo_box.setToolTip(self.tr("Select the preset"))
        self.presets_combo_box.setPlaceholderText(" ")
        self.presets_combo_box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)

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
    
    #Set the options of the presets in the combo box
    def set_presets(self, keep_current_index:bool = False):
        #Clear the old options
        index = self.presets_combo_box.currentIndex()

        for i in range(self.presets_combo_box.count()):
                self.presets_combo_box.removeItem(0)
        
        self.presets_combo_box.setEnabled(True)
        for i,value in enumerate(self.preset_manager.presets):
            self.presets_combo_box.addItem(value.name)
            preview_text = value.name + " preview:\n" + value.print()
            self.presets_combo_box.setItemData(i,preview_text,QtCore.Qt.ItemDataRole.ToolTipRole)
        #self.presets_combo_box.addItems(self.preset_manager.get_names())

        if keep_current_index:
            #If the index is valid, set it
            if index < self.presets_combo_box.count():
                self.presets_combo_box.setCurrentIndex(index)
            
    

    #Set the option of the instruments to the combo box
    def set_options_of_instruments(self,text):
        #Clear the old options
        for i in range(self.instruments_combo_box.count()):
                self.instruments_combo_box.removeItem(0)

        #set instruments
        piece_dir = Validate.check_if_piece_in_list(text,self.archive.pieces.get_parsed_names())
        if not isinstance(piece_dir,Dir_Error):
            try:
                if piece_dir.search_and_set_path():
                    scores = piece_dir.get_scores()
                    #Raise the error if the scores dir is empty
                    if not scores:
                        raise NoScoresException()
                    
                    #For the printer
                    self.piece_lbl.setText(piece_dir.name)
                    self.printer.actual_piece_dir = piece_dir
                    
                    sorted_scores = InstrumentSorter.sort_instruments(scores)
                    self.instruments_combo_box.setEnabled(True)
                    self.instruments_combo_box.addItems(sorted_scores)
            
            #if the piece is not in the digital archive
            except FileNotFoundError:
                self.instruments_combo_box.clear()
                self.instruments_combo_box.insertItem(0,self.tr("NOT DIGITALIZED")) #TRADUCIR
                self.instruments_combo_box.setEnabled(False)
            except NoScoresException:
                self.instruments_combo_box.clear()
                self.instruments_combo_box.insertItem(0,self.tr("NO SCORES")) #TRADUCIR
                self.instruments_combo_box.setEnabled(False)
        
        else:
            self.instruments_combo_box.clear()
            self.instruments_combo_box.setEnabled(False)


    def add_score_frontend_pyqt(self):
        """
        Add the score with all the data from the widgets. 
        This function is called when you click the add button.
        It validates the selection and if it's valid, it calls the add_score function.
        """

        try:
            dir = self.printer.actual_piece_dir

            if self.archive.file_manager.path_exists(dir.path):
                preset_name = self.presets_combo_box.currentText()
                preset = self.preset_manager.get_preset(preset_name)
                            
                if preset == None:
                    ShowError.show_tooltip_error(self.tr("Preset not found"),5000,self.presets_combo_box)
                    self.presets_combo_box.setCurrentIndex(-1)
                    return False
                
                copies = int(self.num_copies.currentText())

                self.piece_search_bar.clear() #Only clear the bar and not the label because maybe the user want to insert another time the sameone
                self.piece_search_bar.setFocus()
                return self.add_score(dir, preset, copies)
            
        except AttributeError:
            ShowError.show_tooltip_error(self.tr("You need to select a piece with scores associated"),5000,self.piece_search_bar)
        return False
        
        

    #Add the score to the list of added scores an update it in the labels list
    def add_score(self, dir:Dir, preset:Preset, copies:int) -> bool:
        """Add the score to the printer and update the scroll area"""

        scrolleable_item_id = self.printer.add(copies,
                                                preset,
                                                dir)
        

        #Update the labels of the down scores
        self.scroll.add_item(StatusConsoleItemWithTwoTexts(dir.name,
                                                preset.name,
                                                copies,
                                                scrolleable_item_id,
                                                self.scroll.remove_item,
                                                self.printer.remove))

        #Block the presets combobox
        self.presets_combo_box.setEnabled(False)
        return True
    

    #Display a window to select a location to save a pdf
    def dialog_window_select_exporting_path(self):
        return QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("Select Folder to export"))


    
    def create_pdf(self):     
        """Generate the pdf with the selected presets and pieces"""
        try:
            if self.printer.items:
                #Ask for the type of creation. By instruments or by pieces
                window = TypeOfExportWindow(self)
                if window.type_of_export == TypeOfExport.CANCELLED:
                    return
                elif window.type_of_export == TypeOfExport.ALL_IN_ONE:
                    self.printer.sorted_export = window.sort_alphabetically
                elif window.type_of_export == TypeOfExport.BY_INSTRUMENTS:
                    self.printer.sorted_export = window.sort_alphabetically
                    self.printer.ignore_preset_copies = window.ignore_preset_copies
                    self.printer.add_piece_number = window.add_piece_numbers
                    self.printer.add_cover_page = window.add_cover_page
                    self.printer.add_index = window.add_index
                    self.printer.add_blank_page_after_index = window.add_blank_page_after_index

                #Make the preporcess and solve the errros
                errors = self.printer.preprocess_export()
                r = ResolveNotMatchedPresets(errors,self)
                
                if len(r.resolved) < len(errors):
                    return #Not all scores selected
                if len(r.resolved) > len(errors):
                    raise MoreScoresThanPresetsException(self.tr("Something went wrong during the selection of the presets"))
                
                #Add resolution to the solution
                for i in r.resolved:
                    print(i)
                    if i.state == PresetResolverStates.IGNORED:
                        continue
                    print(f"Exist {i.resolution} for piece {i.piece} and instrument {i.instrument}")
                    self.printer.add_to_solution(i)

                #Export and save
                pdf_path = self.dialog_window_select_exporting_path()
                if not pdf_path:
                    return
                
                if window.type_of_export == TypeOfExport.ALL_IN_ONE:
                    self.printer.export_all_in_one(pdf_path)
                elif window.type_of_export == TypeOfExport.BY_PIECES:
                    self.printer.export_by_pieces(pdf_path)
                elif window.type_of_export == TypeOfExport.BY_INSTRUMENTS:
                    self.printer.export_by_instruments(pdf_path)

                YesNoWindow(self.tr("Pdfs exported successfully"),True,self)
            
            else:
                error = self.tr("*You need to add some piece")
                ShowError.show_tooltip_error(error,5000,self.btn_confirm)

                
        
        except Exception as e:
            Error_window.print_error(e)

    
    def refresh_presets_list(self, keep_current_index:bool = False):
        self.preset_manager.load() #Update the presets
        self.set_presets(keep_current_index=keep_current_index)

    #Refresh the list of pieces and delete the info in the printer  
    def refresh(self):
        self.scroll.clear()
        self.scroll.update()
        self.piece_search_bar.clear()
        self.piece_lbl.clear()
        self.num_copies.setCurrentIndex(0)
        
        #Printer
        self.printer = PresetsPrinter()
        self.archive.update_pieces()
        #Preview
        self.preview.clear()

        self.refresh_presets_list()


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
        piece = Validate.check_if_piece_in_list(self.piece_search_bar.text(),self.archive.pieces.get_parsed_names())
        if not isinstance(piece,Dir_Error):
            try:
                if not piece.get_scores():
                    raise NoScoresException()
                try:
                    if piece_parsed_name == self.preview_controller.piece_parsed_name:
                        self.preview_controller.instrument = instrument
                        self.preview_controller.page_number = 0
                        self.preview_controller.update_path()
                        self.check_mv_btns_enableability() # Update the buttons states
                    else:
                        self.preview_controller = Preview_controller(piece.name,instrument)
                except Exception:
                    self.preview_controller = Preview_controller(piece.name,instrument)

                self.change_preview_img()
            except NoScoresException:
                pass
            except FileNotFoundError:
                pass
            except Exception as e:
                print(type(e)," ",e)

    

    def save_pieces_preset(self):
        """Save the pieces preset with the selected preset and all the pieces with their presets added"""

        if self.printer.items:
            #Ask for the name of the preset
            preset_name, ok = QtWidgets.QInputDialog.getText(self, self.tr("Save pieces preset"), self.tr("Preset name:"))
            if ok and preset_name:
                pieces_to_add:list[tuple[str,str,str]] = []
                for i in self.printer.items:
                    pieces_to_add.append((i.dir.name, i.preset.name, str(i.copies)))

                was_added = self.piece_preset_manager.add_preset_by_elements(preset_name, i.preset.name, pieces_to_add)
                
                if not was_added:
                    Error_window.print_error(message=self.tr("Preset with this name already exists"))
                else:
                    self.piece_preset_manager.dump() #Save the presets to the file

    
    def load_pieces_preset(self, preset_name:str):
        """Load a pieces preset by the name in the mulple selection window"""
        self.refresh()
        dir_error_msg:str = self.tr("The pieces are not found:\n")
        dir_error:bool = False
        preset_error_msg:str = self.tr("The instrument presets are not found:\n")
        preset_error:bool = False

        if self.piece_preset_manager.exist(preset_name):
            piece_preset = self.piece_preset_manager.get_preset(preset_name)
            if isinstance(piece_preset, PiecesPreset):
                #Set the instrument preset in the combo box
                combobox_id = self.presets_combo_box.findText(piece_preset.preset_name)
                if combobox_id != -1:
                    self.presets_combo_box.setCurrentIndex(combobox_id)
                else:
                    ShowError.show_tooltip_error(self.tr(f"Preset {piece_preset.preset_name} not found in the list"),5000,self.presets_combo_box)
                    self.presets_combo_box.setCurrentIndex(-1)
                
                from frontend_pyqt.pop_up_windows.dropdown_window import DropdownWindow

                instrument_preset_name = ""
                #Set the elements in the printer (piece + instrument preset)
                for i in piece_preset.pieces:
                    dir = Validate.check_if_piece_in_list(i[0],self.archive.pieces.get_parsed_names())
                    if not isinstance(dir, Dir_Error):
                        
                        #Ask for the instrument preset for the import
                        if instrument_preset_name == "":
                            window = DropdownWindow(self.preset_manager.get_names(),i[1],self)
                            instrument_preset_name = window.selected_option
                            instrument_preset = self.preset_manager.get_preset(instrument_preset_name)
                        
                        if instrument_preset != None:
                            self.add_score(dir, instrument_preset, int(i[2]))
                        else:
                            preset_error_msg += f"{i[1]}\n"
                            preset_error = True
                    else:
                        dir_error_msg += f"{i[0]}\n"
                        dir_error = True
        
        
        #Show the error message if there are errors
        error:str = ""
        if dir_error:
            error += dir_error_msg
            if preset_error:
                error += "\n" + preset_error_msg
        else:
            if preset_error:
                error += preset_error_msg
        if error != "":
            Error_window.print_error(message="\n"+error)

                