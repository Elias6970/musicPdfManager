from PyQt6 import QtWidgets
from classes.files_management.archive import Archive
from classes.files_management.archive_file_manager import ArchiveFileManager
from gui.abstract_windows.abstract_search_bar_and_two_buttons_window import AbstractSerchBarAndTwoButtonsWindow
from gui.error_window import Error_window
from classes.constants import *

#Creates a window that can delete scores with search bar and 2 buttons
class Delete_piece_window(AbstractSerchBarAndTwoButtonsWindow):
    def __init__(self,archive:Archive,parent=None):
        super(Delete_piece_window,self).__init__(archive,self.delete_piece,parent) #traducir

        self.setWindowTitle(self.tr("Delete piece"))
        self.func_btn.setText(self.tr("Delete"))

        self.exec()

    #Delete the selected score
    def delete_piece(self):
        if self.validate_selection(self.search_bar.text()):
            cod = Archive.extract_cod(self.piece_lbl.text())
            #Ask to be sure that the user want to delete this score
            alert = QtWidgets.QMessageBox.question(self,self.tr("Warning"),self.tr("Are you sure that you want to delete \n{}".format(self.piece_lbl.text())),QtWidgets.QMessageBox.StandardButton.Yes,QtWidgets.QMessageBox.StandardButton.No) #traducir

            if alert == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    self.archive.db.delete_score(int(cod)) #Delete from db
                    self.archive.pieces.remove(int(cod))

                    try:
                        ArchiveFileManager.delete_piece(self.piece_lbl.text())
                    except FileNotFoundError:
                        pass

                    
                    alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.NoIcon,"",self.tr("{} has been correctly deleted".format(self.piece_lbl.text())),QtWidgets.QMessageBox.StandardButton.Ok,self) #traducir
                    self.search_bar.clear() #Clear the text
                    self.piece_lbl.clear()
                    self.update_autocompleter_scores()

                except Exception as e:
                    Error_window.print_error(e,message=self.tr("Error deleting"))
