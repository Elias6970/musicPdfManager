from PyQt5 import QtWidgets
from classes.files_manage import Archive
from gui.abstract_windows import *
from gui.error_window import Error
from classes.constants import *



class Modify_piece_window(QtWidgets.QDialog):
    def __init__(self,archive:Archive,parent=None):
        super(Modify_piece_window,self).__init__(parent=parent)
        
        self.archive = archive

        container_layout = QtWidgets.QVBoxLayout()

        self.search_bar = Score_search_bar(self.archive.pieces_in_dirs,self.validate_selection)
        self.abstract_fields = Abstract_fields_window(archive,"Modify piece","Modify",[HANDWRITTEN,DIGITALIZED,PARTED],self.add_modification,self.close)

        container_layout.addWidget(self.search_bar)
        container_layout.addWidget(self.abstract_fields)

        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)
        self.exec_()

    def add_modification(self):
        try:
            a1 = self.archive.upsert(int(self.abstract_fields.line_cod.text()),
                            self.abstract_fields.line_name.text(),
                            self.abstract_fields.line_author.text(),
                            self.abstract_fields.line_type.text(),
                            int(self.abstract_fields.checkboxes_dict[HANDWRITTEN].isChecked()),
                            int(self.abstract_fields.checkboxes_dict[DIGITALIZED].isChecked()),
                            int(self.abstract_fields.checkboxes_dict[PARTED].isChecked()))
        
            a2 = self.archive.change_piece_dir_name(int(self.abstract_fields.line_cod.text()),self.abstract_fields.line_name.text())

            if(a1 and a2):
                Pop_up_window("Correctly imported",True,self)
                self.archive.update_pieces_in_dirs()
                self.search_bar.update_autocompleter_scores(self.archive.pieces_in_dirs)

        except Exception as e:
            Error.print_error(e,"Error modificating")

     #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        for i in self.search_bar.pieces_names:
            if text == i:
                try:
                    getted = self.archive.get_with_equals(COD,self.archive.extract_cod(text),",".join([COD,NAME,AUTHOR,TYPE,HANDWRITTEN,DIGITALIZED,PARTED]))[0] 
                except Exception as e:
                    Error.print_error(e,"Piece doesn't found")
                    return False
                
                self.abstract_fields.line_cod.setText(str(getted[0]))
                self.abstract_fields.line_name.setText(getted[1])
                self.abstract_fields.line_author.setText(getted[2])
                self.abstract_fields.line_type.setText(getted[3])
                
                #Set checkboxes
                self.abstract_fields.checkboxes_dict[HANDWRITTEN].setChecked(bool(getted[4]))
                self.abstract_fields.checkboxes_dict[DIGITALIZED].setChecked(bool(getted[5]))
                self.abstract_fields.checkboxes_dict[PARTED].setChecked(bool(getted[6]))

                return True

    def close(self):
        self.hide()

