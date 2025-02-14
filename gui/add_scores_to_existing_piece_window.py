from PyQt6 import  QtWidgets
from classes.files_manage import Archive,Archive_file_manager,Dir
from classes.constants import RELATIVE_ARCHIVE_PATH
from classes.error import PdfNotFoundException,StopClassifyingException
from gui.abstract_windows import *
from gui.score_classifier_window import Score_classifier_window

#Creates a window to add scores to pieces existing in the archive directory or only in the db 
class Add_scores_to_existing_piece_window(Abstract_serch_bar_and_two_buttons_window):
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
            if self.validate_selection(self.search_bar.text()) and Archive_file_manager.move_files(self.search_bar.text(),file_dialog.selectedFiles()):
                try: 
                    Score_classifier_window([Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),self.search_bar.text()))],self.archive.db.update_parted)
                except StopClassifyingException:
                    pass
                except PdfNotFoundException: 
                    pass
                Pop_up_window(self.tr("Correctly imported"),True,self) #Traducir