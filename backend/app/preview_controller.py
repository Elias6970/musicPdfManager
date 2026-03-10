import os,tempfile,fitz
from backend.app.constants.constants import RELATIVE_ARCHIVE_PATH,DIR_SCORES
import pypdf

#Class that controlls the preview.
#The preview extract the pdf page and returns a png image
class Preview_controller:
    def __init__(self,piece_parsed_name:str,instrument:str=""):
        self.piece_parsed_name:str = piece_parsed_name
        self.instrument:str = instrument
        self.page_number = 0
        self.update_path()

    #Recalculates the path
    def update_path(self):
        self.path =  os.path.join(RELATIVE_ARCHIVE_PATH(),self.piece_parsed_name,DIR_SCORES,self.instrument)

    #Returns a png path with the image
    def get_image(self) -> str:  
        path =  os.path.join(tempfile.gettempdir(), os.urandom(24,).hex()+".png")
        file = fitz.open(self.path)
        page = file.load_page(self.page_number).get_pixmap(dpi=200) #type:ignore
        page.save(path)
        
        return path
    
    #Return the num of pages
    def num_of_pages(self):
        return len(pypdf.PdfReader(self.path).pages)
    

    #Pass the page to the next
    def next_page(self) -> bool:
        if self.page_number+1 < self.num_of_pages():
            self.page_number += 1
            return True
        return False
    
    #Pass the page to the previous
    def previous_page(self) -> bool:
        if self.page_number-1 >= 0:
            self.page_number -= 1
            return True
        return False
    
    
    def is_in_last_page(self) -> bool:
        return self.page_number+1 == self.num_of_pages()
    def is_in_first_page(self) -> bool:
        return self.page_number == 0