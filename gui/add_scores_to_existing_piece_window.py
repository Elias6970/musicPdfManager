from PyQt6 import  QtWidgets
from classes.files_management.dir import Dir
from classes.files_management.archive import Archive
from classes.files_management.archive_file_manager import ArchiveFileManager
from classes.constants import RELATIVE_ARCHIVE_PATH
from classes.error import PdfNotFoundException,StopClassifyingException
from gui.abstract_windows.abstract_search_bar_and_two_buttons_window import AbstractSerchBarAndTwoButtonsWindow
from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.score_classifier.score_classifier_window import ScoreClassifierWindow
import os


#Creates a window to add scores to pieces existing in the archive directory or only in the db 
class Add_scores_to_existing_piece_window(AbstractSerchBarAndTwoButtonsWindow):
    def __init__(self,archive:Archive,parent=None):
        super(Add_scores_to_existing_piece_window,self).__init__(archive,self.add_score,parent)
        self.archive = archive
        
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
            if self.validate_selection(self.search_bar.text()) and ArchiveFileManager.move_files(self.search_bar.text(),file_dialog.selectedFiles()):
                try: 
                    ScoreClassifierWindow([Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),self.search_bar.text()))],self.archive.db.update_parted)
                except StopClassifyingException:
                    pass
                except PdfNotFoundException: 
                    pass
                YesNoWindow(self.tr("Correctly imported"),True,self) #Traducir