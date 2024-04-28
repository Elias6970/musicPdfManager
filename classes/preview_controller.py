import os,tempfile,shutil,re
from pdf2image import pdf2image
from classes.constants import RELATIVE_ARCHIVE_PATH,DIR_SCORES
import PyPDF2
class Preview_controller:
    def __init__(self,piece_parsed_name:str,instrument:str=""):
        self.piece_parsed_name:str = piece_parsed_name
        self.instrument:str = instrument
        self.page_number = 0
        self.update_path()

    def update_path(self):
        self.path =  os.path.join(RELATIVE_ARCHIVE_PATH(),self.piece_parsed_name,DIR_SCORES,self.instrument)
        print(self.path)

    def get_image(self) -> str:
        #Extract the page from the pdf. I make manually because i don't hav poppler installed
        path =  os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        page = PyPDF2.PdfReader(self.path).pages[self.page_number]
        writer = PyPDF2.PdfWriter()
        writer.add_page(page)
        writer.write(path)

        image = pdf2image.convert_from_path(path,200)

        print("AQui")
        image[0].save(path,'JPEG')
        print("AWUNO")
        return path
    
    def num_of_pages(self):
        return len(PyPDF2.PdfReader(self.path).pages)
    
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