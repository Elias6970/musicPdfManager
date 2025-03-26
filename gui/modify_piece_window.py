from PyQt6 import QtWidgets
from classes.files_management.archive import Archive
from classes.files_management.archive_file_manager import ArchiveFileManager
from classes.piece import Piece
from classes.error import AvoidModificationException
from gui.abstract_windows.abstract_fields_window import AbstractFieldsWindow
from gui.score_search_bar import ScoreSearchBar
from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.error_window import Error_window
from classes.constants import *



class Modify_piece_window(QtWidgets.QDialog):
    def __init__(self,archive:Archive,parent=None):
        super(Modify_piece_window,self).__init__(parent=parent)
        
        self.archive = archive

        container_layout = QtWidgets.QVBoxLayout()

        self.search_bar:Score_search_bar = ScoreSearchBar(self.archive.pieces.get_parsed_names(),self.validate_selection) # type: ignore
        self.abstract_fields = AbstractFieldsWindow(archive,self.tr("Modify piece"),self.tr("Modify"),[HANDWRITTEN,DIGITALIZED,PARTED],self.add_modification,self.close)

        container_layout.addWidget(self.search_bar)
        container_layout.addWidget(self.abstract_fields)

        #Change checkboxes text to be tranlatable
        self.abstract_fields.checkboxes_dict[HANDWRITTEN].setText(self.tr("handwritten")) #traducir
        self.abstract_fields.checkboxes_dict[PARTED].setText(self.tr("parted")) #traducir
        self.abstract_fields.checkboxes_dict[DIGITALIZED].setText(self.tr("digitalized")) #traducir

        #self.setGeometry(0,0,400,200)
        #self.setBaseSize(400,200)
        self.setLayout(container_layout)
        self.exec()

    def add_modification(self):
        try:
            #Ask the user if he want to modify the cod
            if self.old_piece.cod != int(self.abstract_fields.line_cod.text()):
                confirmation = YesNoWindow(self.tr("Are you sure that you want to modify the cod?")+"\n"+self.tr("It is a sensitive  and essential part of the archive"),False,self)
                if confirmation.btn_confirm_pressed == False:
                    raise AvoidModificationException()
            

            insertion = self.archive.db.upsert(self.old_piece.cod,
                            int(self.abstract_fields.line_cod.text()),
                            self.abstract_fields.line_name.text(),
                            self.abstract_fields.line_author.text(),
                            self.abstract_fields.line_type.text(),
                            int(self.abstract_fields.checkboxes_dict[HANDWRITTEN].isChecked()),
                            int(self.abstract_fields.checkboxes_dict[DIGITALIZED].isChecked()),
                            int(self.abstract_fields.checkboxes_dict[PARTED].isChecked()))
        

            if insertion:
                ArchiveFileManager.change_piece_dir_name(self.old_piece.parsed_name,Piece.make_parsed_name(int(self.abstract_fields.line_cod.text()),self.abstract_fields.line_name.text()))
                self.archive.pieces.update_cod_and_name(self.old_piece.cod,int(self.abstract_fields.line_cod.text()),self.abstract_fields.line_name.text())
                

                YesNoWindow(self.tr("Correctly modificated"),True,self) 

                self.clear_form()
                self.search_bar.update_autocompleter_scores(self.archive.pieces.get_parsed_names())

        except AvoidModificationException:
            pass
        except Exception as e:
            Error_window.print_error(e,self.tr("Error modificating"))

     #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        for i in self.search_bar.pieces_parsed_names:
            if text == i:
                try:
                    getted = self.archive.db.get_with_equals(COD,self.archive.extract_cod(text),",".join([COD,NAME,AUTHOR,TYPE,HANDWRITTEN,DIGITALIZED,PARTED]))[0] 
                except Exception as e:
                    Error_window.print_error(e,self.tr("Piece doesn't found")) #traducir
                    return False
                
                self.old_piece = self.archive.pieces.get(int(getted[0]))
                
                self.abstract_fields.line_cod.setText(str(getted[0]))
                self.abstract_fields.line_name.setText(getted[1])
                self.abstract_fields.line_author.setText(getted[2])
                self.abstract_fields.line_type.setText(getted[3])
                
                #Set checkboxes
                self.abstract_fields.checkboxes_dict[HANDWRITTEN].setChecked(bool(getted[4]))
                self.abstract_fields.checkboxes_dict[DIGITALIZED].setChecked(bool(getted[5]))
                self.abstract_fields.checkboxes_dict[PARTED].setChecked(bool(getted[6]))

                return True

    #Put all the form in blank
    def clear_form(self):
        self.search_bar.clear()
        self.abstract_fields.line_cod.clear()
        self.abstract_fields.line_name.clear()
        self.abstract_fields.line_author.clear()
        self.abstract_fields.line_type.clear()
        self.abstract_fields.checkboxes_dict[HANDWRITTEN].setChecked(False)
        self.abstract_fields.checkboxes_dict[DIGITALIZED].setChecked(False)
        self.abstract_fields.checkboxes_dict[PARTED].setChecked(False)

    def close(self):
        self.hide()

