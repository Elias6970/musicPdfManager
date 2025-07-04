from PyQt6 import QtWidgets
from classes.utils.name_manager import NameManager
from  classes.files_management.dir import Dir
from classes.files_management.archive import Archive
from classes.constants.constants import RELATIVE_ARCHIVE_PATH
from classes.error import StopClassifyingException, PdfNotFoundException
from gui.status_console import StatusConsole
from gui.score_search_bar import ScoreSearchBar
from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.list_items.status_console_item_two_texts import StatusConsleItemWithTwoTexts
from gui.error_window import Error_window
from gui.score_classifier.score_classifier_window import ScoreClassifierWindow
import os


#Window to select the pieces to classify with the score_classifier tool:
#   update_parted_flag_db_function: pointer to the function that update the flag 
#           parted in the db. This function is used in the ScoreClassifierWindow
class PieceSelectorToClassifyWindow(QtWidgets.QDialog):
    def __init__(self,archive:Archive,parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle(self.tr("Select pieces"))


        self.pieces_to_classify:list[str] = []
        self.archive = archive

        #Gui
        container_layout = QtWidgets.QVBoxLayout()
        
        self.search_bar = ScoreSearchBar(self.archive.pieces.get_digitalized_parsed_names(),self.validate_selection) #type: ignore
        self.status_area = StatusConsole()
        
        #Butons
        btn_layout = QtWidgets.QHBoxLayout()

        add_btn = QtWidgets.QPushButton(self.tr("Add")) #traducir
        classify_btn = QtWidgets.QPushButton(self.tr("Classify")) #traducir
        close_btn = QtWidgets.QPushButton(self.tr("Close")) #traducir
        add_btn.clicked.connect(self.btn_add)
        classify_btn.clicked.connect(self.btn_classify)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(classify_btn)
        btn_layout.addWidget(close_btn)

        container_layout.addWidget(self.search_bar)
        container_layout.addLayout(btn_layout)
        container_layout.addWidget(self.status_area)
        
        self.setLayout(container_layout)
        self.setGeometry(500,200,500,400)
        self.exec()


    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        for i in self.search_bar.pieces_parsed_names:
            if text == i:
                return True
        return False
    
    def remove_piece(self,piece:str):
        self.pieces_to_classify.remove(piece)

    def btn_add(self):
        if self.validate_selection(self.search_bar.text()):
            self.pieces_to_classify.append(self.search_bar.text())
            self.status_area.add_item(StatusConsleItemWithTwoTexts("",
                                     self.search_bar.text(),
                                     "",
                                     self.search_bar.text(),
                                     self.status_area.remove_item,
                                     self.remove_piece))

            self.search_bar.clear()


    #Button that opens the classify window.
    #   This function checks if the pieces have the parted flag = 1 in the db
    def btn_classify(self):
        to_classify:list[Dir] = [] 
        error_classified:list[str] = [] #This list is of pieces that are already classified
        for i in self.pieces_to_classify:
            if self.archive.db.is_parted(str(NameManager.get_cod(i))):
                error_classified.append(i)
            else:
                to_classify.append(Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),i)))
        
        if not error_classified == "":
            for i in error_classified:
                answer = YesNoWindow(i + self.tr(" is already splited,\n")+self.tr("do you want to redo it? "),False,self) #traducir
                if answer.btn_confirm_pressed == True:
                    to_classify.append(Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),i)))

        if len(to_classify) > 0:
            try:
                ScoreClassifierWindow(to_classify,self.archive.db.update_parted,parent=self)
            except StopClassifyingException:
                pass
            except PdfNotFoundException as e:
                Error_window.print_error(e,self.tr("The piece doesn't have any pdf")) #traducir
                return
            except Exception as e:
                Error_window.print_error(e,self.tr("An error ocurred when classifying")) #traducir 
        else:
            Error_window.print_error(self.tr("Any score to classify")) #traducir
            return
        
        self.close()

    def close(self):
        self.hide()
