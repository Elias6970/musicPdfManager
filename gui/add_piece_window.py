
from PyQt5 import QtWidgets
from classes.files_manage import Archive,File,Archive_file_manager
from classes.constants import *
from classes.error import PdfNotFoundException
from gui.error_window import Error_window
from gui.abstract_windows import *
from gui.score_classifier_window import Score_classifier_window


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
        
        self.line_cod.setText(str(self.archive.db.get_next_cod()))#cambiar


        self.exec_()

    def add_score(self):
        cod = self.line_cod.text()
        name = self.line_name.text()
        parsed_name = Archive.get_parsed_name(cod,name)
        
        if self.verifications(cod,name):
            
            #Open a dialog to select the files to be putted in the directory
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)  # Allow selecting any file type
            file_dialog.setWindowTitle(self.tr("Select a folder or a file")) #traducir
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)  # Set the dialog to save mode


            
            
            if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
                Archive_file_manager.make_dir(RELATIVE_ARCHIVE_PATH(),parsed_name)
                
                if Archive_file_manager.move_files(parsed_name,file_dialog.selectedFiles()) and self.archive.db.insert(int(cod),name,self.line_author.text(),self.line_type.text(),handwritten=int(self.checkboxes_dict[HANDWRITTEN].isChecked()),parted=0):
                    pdfs:list = [i for i in file_dialog.selectedFiles() if File.is_pdf(i)]

                    #Check if there are any pdf
                    #if not pdfs == []:
                    try:
                        Score_classifier_window([Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),parsed_name))],self.archive.db.update_parted)
                    except PdfNotFoundException: 
                        pass
                    except Exception:
                        pass
                    Pop_up_window(self.tr("{} has been correctly imported".format(parsed_name)),True,self)
                    self.reset_fields()
                else:
                    Pop_up_window(self.tr("Has been an error importing {}".format(parsed_name)),True,self)
                



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
                        warning_window = Pop_up_window(warning_text,False,self)
                    
                    try:
                        return warning_window.btn_confirm_pressed #type:ignore
                    except UnboundLocalError as e: #if the pop up warning is not being showed(not similar names)
                        return True
            else:
                alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Warning","Already exists a score with this cod or \nname can't be empty",QtWidgets.QMessageBox.Ok,self) #traducir
                alert.exec_()
            

        except Exception as e:
            Error_window.print_error(e)
        
        return False




