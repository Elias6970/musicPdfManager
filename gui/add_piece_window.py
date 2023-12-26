
from PyQt5 import QtWidgets
from classes.files_manage import Archive
from classes.constants import *
from gui.error_window import Error
from gui.abstract_windows import *


#Window to add a new piece to the db. When you add the piece you must add the corresponding scores
#Parameters:
#   	archive: Archive object of the archive
#Window parts:
#   4 fields to fill(code,name,author,type)
#   Two buttons(add the piece, close the window)
#   handwritten checkbox TODO: add posibility to not add scores
#   
class Add_piece_window(Abstract_fields_window):
    def __init__(self, archive: Archive, parent=None):
        super().__init__(archive, "Add new piece", "Add", [HANDWRITTEN],self.add_score, parent=parent)
        
        self.line_cod.setText(str(self.archive.get_next_cod()))#cambiar


        self.exec_()

    def add_score(self):
        cod = self.line_cod.text()
        name = self.line_name.text()
        parsed_name = Archive.get_parsed_name(cod,name)
        
        if self.verifications(cod,name):
            
            #Open a dialog to select the files to be putted in the directory
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)  # Allow selecting any file type
            file_dialog.setWindowTitle("Select a folder or a file") #traducir
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)  # Set the dialog to save mode


            
            
            if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
                Archive.make_dir(RELATIVE_ARCHIVE_PATH,parsed_name)
                
                if self.archive.move_files(parsed_name,file_dialog.selectedFiles()) and self.archive.insert(int(cod),name,self.line_author.text(),self.line_type.text(),handwritten=int(self.checkboxes_dict[HANDWRITTEN].isChecked()),parted=0):
                    Pop_up_window("{} has been correctly imported".format(parsed_name),True,self)
                    self.reset_fields()
                else:
                    Pop_up_window("Has been an error importing {}".format(parsed_name),True,self)
                



    #Check if the input adding the score is correct 
    #Checks:
    #   if the cod is in the db
    #   if the name is not empty
    #   if its name in in the db --> ONLY APPEAR A WINDOW SHOWING THE NAMES SIMILARS(YOU CAN CHOOSE YES OR NO TO ADD IT)
    def verifications(self,cod,name:str):
        try:
            checked_cod = self.archive.get_with_equals("cod",cod,"cod") #Check if the cod is in the db
            
            if checked_cod == [] and len(name.strip()) != 0:
                    name_matches = self.archive.get_with_like("name",name,"cod,name")
                    
                    
                    if name_matches != []:
                        warning_text = "This score is called similar like these ones:\n" #traducir
                        for i in name_matches:
                            warning_text = warning_text + Archive.get_parsed_name(i[0],i[1]) + "\n"
                        
                        #Pop up the scores matched
                        warning_window = Pop_up_window(warning_text,False,self)
                    
                    try:
                        return warning_window.btn_confirm_pressed #type:ignore
                    except UnboundLocalError as e: #if the pop up warning is not being showed(not similar names)
                        return True
            else:
                alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Warning","Already exists a score with this cod or \nname can't be empty",QtWidgets.QMessageBox.Ok,self) #traducir
                alert.exec_()
            

        except Exception as e:
            Error.print_error(e)
        
        return False




