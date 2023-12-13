from PyQt5 import QtCore, QtWidgets
import os,shutil
from classes.files_manage import Archive,File
from gui.abstract_windows import Score_search_bar,Abstract_serch_bar_and_two_buttons_window
from classes.error import Error
from classes.constants import RELATIVE_ARCHIVE_PATH

#Creates a window that can delete scores with search bar and 2 buttons
class Delete_score_window(Abstract_serch_bar_and_two_buttons_window):
    def __init__(self,archive:Archive,parent=None):
        super(Delete_score_window,self).__init__(archive,"Delete score","Delete",parent) #traducir

    #Delete the selected score
    def btn_function(self):
        if self.validate_selection(self.search_bar.piece_search_bar.text()):
            cod = Archive.extract_cod(self.piece_lbl.text())
            #Ask to be sure that the user want to delete this score
            alert = QtWidgets.QMessageBox.question(self,"Warning","Are you sure that you want to delete \n{}".format(self.piece_lbl.text()),QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No) #traducir

            if alert == QtWidgets.QMessageBox.Yes:
                try:
                    self.archive.delete_score(int(cod)) #Delete from db
                    shutil.rmtree(os.path.join(RELATIVE_ARCHIVE_PATH,self.piece_lbl.text())) #Delete files

                    alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"","{} has been correctly deleted".format(self.piece_lbl.text()),QtWidgets.QMessageBox.Ok,self) #traducir
                    self.search_bar.piece_search_bar.clear() #Clear the text
                    self.piece_lbl.clear()
                    self.update_autocompleter_scores()

                except Exception as e:
                    #error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Error","Error: {},{}".format(type(e),e),QtWidgets.QMessageBox.Ok,self) #traducir
                    Error.print_error(e,message="Error deleting")


#Creates a window to add scores to pieces existing in the archive directory or only in the db 
class Add_scores_to_existing_piece_window(Abstract_serch_bar_and_two_buttons_window):
    def __init__(self,archive:Archive,parent=None):
        super(Add_scores_to_existing_piece_window,self).__init__(archive,"Add scores to existing piece","Add",parent)

    #Add scores to existing pieces
    def btn_function(self):
        if self.validate_selection(self.search_bar.piece_search_bar.text()):
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)  # Allow selecting any file type
            file_dialog.setWindowTitle("Select a folder or a file") #traducir
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)  # Set the dialog to save mode

        if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            print(file_dialog.selectedFiles())

"""
Archive.make_dir(RELATIVE_ARCHIVE_PATH,parsed_name)

if self.move_files(parsed_name,file_dialog.selectedFiles()) and self.archive.insert(Score(int(cod),name,self.line_author.text(),self.line_type.text(),handwritten=int(self.handwritten_cbox.isChecked()),parted=0)):
    self.alert_import(parsed_name,True)
    self.reset_fields()
else:
    self.alert_import(parsed_name,False)
"""



class Modify_score_window(QtWidgets.QDialog):
    def __init__(self,archive:Archive,parent=None):
        super(Modify_score_window,self).__init__(parent=parent)
    pass


