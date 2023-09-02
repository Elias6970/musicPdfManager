from PyQt5 import QtCore, QtWidgets
import os,shutil
from classes.files_manage import Archivo,File
from gui.window_extras import Search_score_bar,Error
from classes.constants import RELATIVE_ARCHIVE_PATH

class Delete_score_window(QtWidgets.QDialog):
    
    def __init__(self,archive:Archivo,parent=None):
        super(Delete_score_window,self).__init__(parent=parent)
        
        self.archive = archive
        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        #container_layout.setContentsMargins(20,0,20,20)
        
        self.search_bar = Search_score_bar(self.archive.pieces_in_dirs)
        container_layout.addWidget(self.search_bar)
        container_layout.addLayout(self.create_buttons_layout())
        
        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        self.exec_()

    def create_buttons_layout(self):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        add_btn = QtWidgets.QPushButton("Delete") #traducir

        close_btn.clicked.connect(self.close)
        add_btn.clicked.connect(self.delete_score)
        
        btns_layout.addWidget(add_btn)
        btns_layout.addWidget(close_btn)
        
        return btns_layout
    
    #Delete the selected score
    def delete_score(self):
        if self.search_bar.validate_selection(self.search_bar.piece_search_bar.text(),False):
            cod = Archivo.extract_cod(self.search_bar.piece_lbl.text())
            #Ask to be sure that the user want to delete this score
            alert = QtWidgets.QMessageBox.question(self,"Warning","Are you sure that you want to delete \n{}".format(self.search_bar.piece_lbl.text()),QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No) #traducir

            if alert == QtWidgets.QMessageBox.Yes:
                try:
                    self.archive.delete_score(int(cod)) #Delete from db
                    shutil.rmtree(RELATIVE_ARCHIVE_PATH+self.search_bar.piece_lbl.text()) #Delete files

                    alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"","{} has been correctly deleted".format(self.search_bar.piece_lbl.text()),QtWidgets.QMessageBox.Ok,self) #traducir
                    self.search_bar.piece_search_bar.clear() #Clear the text
                    self.search_bar.piece_lbl.clear()
                    
                except Exception as e:
                    #error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Error","Error: {},{}".format(type(e),e),QtWidgets.QMessageBox.Ok,self) #traducir
                    Error.print_error(e,message="Error deleting")


    def close(self):
        self.hide()

class Modify_score_window(QtWidgets.QDialog):
    def __init__(self,archive:Archivo,parent=None):
        super(Modify_score_window,self).__init__(parent=parent)
    pass