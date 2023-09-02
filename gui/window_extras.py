import os
from PyQt5 import QtCore, QtWidgets

#TODO: tratar de eliminar la duplicacion de códgio de la search bar en main window. Actualmente nok puedo porque no se como actualizar el combo box de instrumentos
#Search bar + autocompleter + label that shows the score selected
class Search_score_bar(QtWidgets.QWidget):
    def __init__(self, pieces_in_dirs:list,parent=None) -> None:
        super(Search_score_bar,self).__init__(parent)

        self.pieces_in_dirs = pieces_in_dirs

        search_bar_layout = QtWidgets.QVBoxLayout()
        
        #Space
        #search_bar_layout.setContentsMargins(20,0,0,0)
        

        self.piece_search_bar = QtWidgets.QLineEdit()
        self.piece_search_bar.setPlaceholderText("Search score") #traducir
        self.piece_search_bar.textChanged.connect(lambda: self.validate_selection(self.piece_search_bar.text(),False)) #type: ignore
            
        self.pieces_names = [os.path.basename(i.path) for i in self.pieces_in_dirs]

        #Auto Completer
        completer = QtWidgets.QCompleter(self.pieces_names)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive) #type: ignore
        completer.setFilterMode(QtCore.Qt.MatchContains) #type: ignore

        self.piece_search_bar.setCompleter(completer)

        #Down label
        self.piece_lbl = QtWidgets.QLabel()

        search_bar_layout.addWidget(self.piece_search_bar)
        search_bar_layout.addWidget(self.piece_lbl)

        self.setLayout(search_bar_layout)


    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text,new_check=True):
        for i in self.pieces_in_dirs:
            if text == os.path.basename(i.path):
                self.piece_lbl.setText(text)
                self.actual_score = i

                if new_check:
                    self.set_option_of_instruments(i.scores)

                return True


class Error:
    @staticmethod
    def print_error(e=None,message=""):
        error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Error","Error: {},{} \n{}".format(type(e),e,message)) #traducir
        error.exec_()
    
