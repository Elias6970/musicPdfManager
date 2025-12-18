
from PyQt6 import QtWidgets
from classes.utils.name_manager import NameManager
from classes.files_management.dir import Dir
from classes.files_management.archive import Archive
from classes.files_management.archive_file_manager import ArchiveFileManager
from classes.constants.constants import RELATIVE_ARCHIVE_PATH,HANDWRITTEN,DONT_ADD_SCORES,DONT_CLASSIFY_NOW
from gui.error_window import Error_window
from gui.abstract_windows.abstract_fields_window import AbstractFieldsWindow
from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.score_classifier.score_classifier_window import ScoreClassifierWindow
import os

#Window to add a new piece to the db. When you add the piece you must add the corresponding scores
#Parameters:
#   	archive: Archive object of the archive
#Window parts:
#   4 fields to fill(code,name,author,type)
#   Two buttons(add the piece, close the window)
#   handwritten checkbox
#   
class Add_piece_window(AbstractFieldsWindow):
    def __init__(self, archive: Archive, parent=None):
        super().__init__(archive, self.tr("Add new piece"), self.tr("Add"), [HANDWRITTEN,DONT_ADD_SCORES,DONT_CLASSIFY_NOW],self.add_score, parent=parent)

        self.line_cod.setText(str(self.archive.db.get_next_cod()))#cambiar

        #Change checkboxes text to be tranlatable
        self.checkboxes_dict[HANDWRITTEN].setText(self.tr("Handwritten"))
        self.checkboxes_dict[DONT_ADD_SCORES].setText(self.tr("Don't add scores"))
        self.checkboxes_dict[DONT_CLASSIFY_NOW].setText(self.tr("Don't classify now"))


        self.exec()

    def add_score(self):
        """Add a score to the database and move the files to the archive."""
        cod = self.line_cod.text()
        name = self.line_name.text()
        parsed_name = NameManager.get_std_name(cod,name)
        classified = False

        if self.verifications(cod,name):

            if not self.checkboxes_dict[DONT_ADD_SCORES].isChecked():
                #Open a dialog to select the files to be putted in the directory
                file_dialog = QtWidgets.QFileDialog()
                file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)  # Allow selecting any file type
                file_dialog.setWindowTitle(self.tr("Select a folder or a file")) #traducir
                file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptOpen)  # Set the dialog to save mode
    
                if file_dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
                    ArchiveFileManager.make_dir(parsed_name)
                    are_moved = ArchiveFileManager.copy_files_in_archive(parsed_name,file_dialog.selectedFiles())

                    if are_moved:
                        if not self.checkboxes_dict[DONT_CLASSIFY_NOW].isChecked():
                            try:
                                ScoreClassifierWindow([Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),parsed_name))],self.archive.db.update_parted)
                                classified = True                        
                            except Exception:
                                pass
                    else:
                        YesNoWindow(self.tr("There has been an error importing {}".format(parsed_name)),True,self)
                        return
                else:
                    YesNoWindow(self.tr("There has been an error selecting the files"),True,self)
                    return


            is_inserted = self.archive.db.insert(int(cod),
                                                 name,
                                                 self.line_author.text(),
                                                 self.line_type.text(),
                                                 handwritten=int(self.checkboxes_dict[HANDWRITTEN].isChecked()),
                                                 parted=0,
                                                 digitalized=1)

            if is_inserted:
                self.archive.pieces.add(int(cod),name,parsed_name,classified)

                YesNoWindow(self.tr("{} has been correctly imported".format(parsed_name)),True,self)
                self.reset_fields()

                



    #Check if the input adding the score is correct 
    #Checks:
    #   if the cod is in the db
    #   if the name is not empty
    #   if its name in in the db --> ONLY APPEAR A WINDOW SHOWING THE NAMES SIMILARS(YOU CAN CHOOSE YES OR NO TO ADD IT)
    def verifications(self,cod,name:str):
        try:
            checked_cod = self.archive.db.get_with_equals("cod",cod,"cod") #Check if the cod is in the db
            
            if checked_cod == [] and len(name.strip()) != 0:
                    name_matches = self.archive.db.get_with_like("name",name,"cod,name")
                    
                    
                    if name_matches != []:
                        warning_text = "This score is called similar like these ones:\n" #traducir
                        for i in name_matches:
                            warning_text = warning_text + NameManager.get_std_name(i[0],i[1]) + "\n"
                        
                        #Pop up the scores matched
                        warning_window = YesNoWindow(warning_text,False,self)
                    
                    try:
                        return warning_window.btn_confirm_pressed 
                    except UnboundLocalError as e: #if the pop up warning is not being showed(not similar names)
                        return True
            else:
                alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.NoIcon,"Warning","Already exists a score with this cod or \nname can't be empty",QtWidgets.QMessageBox.StandardButton.Ok,self) #traducir
                alert.exec()
            

        except Exception as e:
            Error_window.print_error(e)
        
        return False




