from PyQt6 import QtWidgets
from backend.app.files_management.archive import Archive
from backend.app.pieces_management.delete_piece_controller import DeletePieceController
from frontend_pyqt.abstract_windows.abstract_search_bar_and_two_buttons_window import AbstractSerchBarAndTwoButtonsWindow
from frontend_pyqt.pop_up_windows.error_window import Error_window
from backend.app.constants.constants import *

#Creates a window that can delete scores with search bar and 2 buttons
class Delete_piece_window(AbstractSerchBarAndTwoButtonsWindow):
    def __init__(self,archive:Archive,parent=None):
        super(Delete_piece_window,self).__init__(archive,self.delete_piece,parent) #traducir

        self.controller = DeletePieceController(self.archive)

        self.setWindowTitle(self.tr("Delete piece"))
        self.func_btn.setText(self.tr("Delete"))

        self.exec()

    #Delete the selected score
    def delete_piece(self):
        if self.validate_selection(self.search_bar.text()):
            #Ask to be sure that the user want to delete this score
            alert = QtWidgets.QMessageBox.question(self,self.tr("Warning"),self.tr("Are you sure that you want to delete \n{}".format(self.piece_lbl.text())),QtWidgets.QMessageBox.StandardButton.Yes,QtWidgets.QMessageBox.StandardButton.No) #traducir

            if alert == QtWidgets.QMessageBox.StandardButton.Yes:
                try:
                    self.controller.delete_piece(self.piece_lbl.text())
                    
                    alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.NoIcon,"",self.tr("{} has been correctly deleted".format(self.piece_lbl.text())),QtWidgets.QMessageBox.StandardButton.Ok,self) #traducir
                    self.search_bar.clear() #Clear the text
                    self.piece_lbl.clear()
                    self.update_autocompleter_scores()

                except Exception as e:
                    Error_window.print_error(e,message=self.tr("Error deleting"))
