import PyPDF2,os
from classes.files_manage import Print_file,Dir
from classes.validate import Validate
from classes.constants import DIR_SCORES

#This class represents a printer saving a list of pdfs to print
class Printer:
    def __init__(self) -> None:
        self.actual_piece:Dir
        self.pdfs_added:list[Print_file] = []
    
    def set_actual_score(self,new_piece:Dir):
        self.actual_piece = new_piece

    def add_score(self,score_path:str,num_copies:int,pieces:list[Dir]) -> bool:
         #Stops the user if try to add a score no existing
        if Validate.validate_selection(self.actual_piece.name,[i.name for i in pieces]):

            self.pdfs_added.append(Print_file(os.path.join(self.actual_piece.path,DIR_SCORES,score_path),num_copies))
            return True
        
        return False
    

    def create_pdf(self,path:str) -> None:
        merged_pdf = PyPDF2.PdfWriter()
        for i in self.pdfs_added:
            if os.path.exists(i.path):
                for j in range(i.copies): #Add the pdf the times that is selected in copies
                    merged_pdf.append(i.path)
        
        merged_pdf.write(path)
        merged_pdf.close()