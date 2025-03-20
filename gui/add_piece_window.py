
from PyQt6 import QtWidgets
from classes.files_management.dir import Dir
from classes.files_management.archive import Archive
from classes.files_management.archive_file_manager import ArchiveFileManager
from classes.constants import *
from classes.error import PdfNotFoundException,StopClassifyingException
from gui.error_window import Error_window
from gui.abstract_windows.abstract_fields_window import AbstractFieldsWindow
from gui.pop_up_window import PopUpWindow
from gui.score_classifier.score_classifier_window import ScoreClassifierWindow

#Window to add a new piece to the db. When you add the piece you must add the corresponding scores
#Parameters:
#   	archive: Archive object of the archive
#Window parts:
#   4 fields to fill(code,name,author,type)
#   Two buttons(add the piece, close the window)
#   handwritten checkbox TODO: add posibility to not add scores
#   
class Add_piece_window(AbstractFieldsWindow):
    def __init__(self, archive: Archive, parent=None):
        super().__init__(archive, self.tr("Add new piece"), self.tr("Add"), [HANDWRITTEN,DONT_ADD_SCORES],self.add_score, parent=parent)

        self.line_cod.setText(str(self.archive.db.get_next_cod()))#cambiar

        #Change checkboxes text to be tranlatable
        self.checkboxes_dict[HANDWRITTEN].setText(self.tr("handwritten"))
        self.checkboxes_dict[DONT_ADD_SCORES].setText(self.tr("Don't add scores"))


        self.exec()

    def add_score(self):
        cod = self.line_cod.text()
        name = self.line_name.text()
        parsed_name = Archive.get_parsed_name(cod,name)
        
        if self.verifications(cod,name):
            
            #Open a dialog to select the files to be putted in the directory
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)  # Allow selecting any file type
            file_dialog.setWindowTitle(self.tr("Select a folder or a file")) #traducir
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptOpen)  # Set the dialog to save mode


            
            
            if file_dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
                ArchiveFileManager.make_dir(RELATIVE_ARCHIVE_PATH(),parsed_name)
                
                if ArchiveFileManager.move_files(parsed_name,file_dialog.selectedFiles()) and self.archive.db.insert(int(cod),name,self.line_author.text(),self.line_type.text(),handwritten=int(self.checkboxes_dict[HANDWRITTEN].isChecked()),parted=0,digitalized=1):
                    try:
                        ScoreClassifierWindow([Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),parsed_name))],self.archive.db.update_parted)
                        self.archive.pieces.add(int(cod),name,parsed_name,True)
                    
                    except StopClassifyingException:
                        self.archive.pieces.add(int(cod),name,parsed_name)
                    except PdfNotFoundException: 
                        pass
                    except Exception:
                        pass
                    PopUpWindow(self.tr("{} has been correctly imported".format(parsed_name)),True,self)
                    self.reset_fields()
                else:
                    PopUpWindow(self.tr("Has been an error importing {}".format(parsed_name)),True,self)
                



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
                            warning_text = warning_text + Archive.get_parsed_name(i[0],i[1]) + "\n"
                        
                        #Pop up the scores matched
                        warning_window = PopUpWindow(warning_text,False,self)
                    
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




