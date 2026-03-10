from PyQt6 import  QtWidgets
from backend.app.files_management.dir import Dir
from backend.app.files_management.archive import Archive
from backend.app.pieces_management.add_piece_controller import AddPieceController
from backend.app.constants.constants import RELATIVE_ARCHIVE_PATH
from backend.app.error import PdfNotFoundException,StopClassifyingException
from frontend_pyqt.abstract_windows.abstract_search_bar_and_two_buttons_window import AbstractSerchBarAndTwoButtonsWindow
from frontend_pyqt.pop_up_windows.yes_no_window import YesNoWindow
from frontend_pyqt.score_classifier.score_classifier_window import ScoreClassifierWindow
import os


#Creates a window to add scores to pieces existing in the archive directory or only in the db 
class Add_scores_to_existing_piece_window(AbstractSerchBarAndTwoButtonsWindow):
    def __init__(self,archive:Archive,parent=None):
        super(Add_scores_to_existing_piece_window,self).__init__(archive,self.add_score,parent)
        self.archive = archive
        self.controller = AddPieceController(self.archive)

        self.setWindowTitle(self.tr("Add scores to existing piece"))
        self.func_btn.setText(self.tr("Add"))
        
        self.exec()

    #Add scores to existing pieces
    def add_score(self):
        file_dialog = QtWidgets.QFileDialog()

        if self.validate_selection(self.search_bar.text()):
            file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)  # Allow selecting any file type
            file_dialog.setWindowTitle(self.tr("Select a folder or a file")) #traducir
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptOpen)  # Set the dialog to save mode


        if file_dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
            is_correct_std_name = self.validate_selection(self.search_bar.text())
            files_are_added = self.controller.add_files_to_piece(self.search_bar.text(),file_dialog.selectedFiles())
            if is_correct_std_name and files_are_added:
                try: 
                    #You reclassify the whole piece (this is why commented)
                    #ScoreClassifierWindow([Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),self.search_bar.text()))],self.archive.db.update_parted)
                    #TODO: Reclassify only the new files added
                    pass
                except StopClassifyingException:
                    pass
                except PdfNotFoundException: 
                    pass
                YesNoWindow(self.tr("Correctly imported"),True,self) #Traducir