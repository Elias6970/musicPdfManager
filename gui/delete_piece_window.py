from PyQt5 import QtWidgets
import os,shutil
from classes.files_manage import Archive
from gui.abstract_windows import *
from gui.error_window import Error
from classes.constants import *

#Creates a window that can delete scores with search bar and 2 buttons
class Delete_piece_window(Abstract_serch_bar_and_two_buttons_window):
    def __init__(self,archive:Archive,parent=None):
        super(Delete_piece_window,self).__init__(archive,"Delete piece","Delete",self.delete_piece,parent) #traducir

        self.exec_()

    #Delete the selected score
    def delete_piece(self):
        if self.validate_selection(self.search_bar.text()):
            cod = Archive.extract_cod(self.piece_lbl.text())
            #Ask to be sure that the user want to delete this score
            alert = QtWidgets.QMessageBox.question(self,"Warning","Are you sure that you want to delete \n{}".format(self.piece_lbl.text()),QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No) #traducir

            if alert == QtWidgets.QMessageBox.Yes:
                try:
                    self.archive.delete_score(int(cod)) #Delete from db
                    shutil.rmtree(os.path.join(RELATIVE_ARCHIVE_PATH,self.piece_lbl.text())) #Delete files

                    alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"","{} has been correctly deleted".format(self.piece_lbl.text()),QtWidgets.QMessageBox.Ok,self) #traducir
                    self.search_bar.clear() #Clear the text
                    self.piece_lbl.clear()
                    self.update_autocompleter_scores()

                except Exception as e:
                    #error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Error","Error: {},{}".format(type(e),e),QtWidgets.QMessageBox.Ok,self) #traducir
                    Error.print_error(e,message="Error deleting")
