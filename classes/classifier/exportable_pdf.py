import os,shutil
from typing import List,Tuple
from classes.files_manage import File
from classes.crop_rectangle import CropRectangle
import PyPDF2

#Represents a pdf to be exported
#   have a path to the original pdf
#   and a list with the new names and temp pdf paths
class ExportablePdf(File):
    def __init__(self,path) -> None:
        super().__init__(path)

        self.num_pages:int = len(PyPDF2.PdfReader(path).pages)

        self.actual_pdf_page:int = 0

        #The list have tuples with (temp_file_path,new_name,cropRectangle)
        self.list_of_new_files:List[Tuple[str,str,CropRectangle]] = []


    #Append a new page to an existing temp pdf in list_of_new_files
    @staticmethod
    def append_page(file_src:str,to_append:str):
        merger = PyPDF2.PdfMerger()
        merger.append(PyPDF2.PdfReader(open(file_src, 'rb')))
        merger.append(PyPDF2.PdfReader(open(to_append, 'rb')))
        merger.write(file_src)


    #Add a new page to the list of new files.
    #Appends the new pdf to the list with its name
    def add_pdf_page(self,temp_file_path:str,new_name:str,crop_rectangle:CropRectangle) -> None:  
        self.list_of_new_files.append((temp_file_path,new_name,crop_rectangle))
    
    #Remove the latest page from the list
    def remove_latest_page(self) -> None:
        self.list_of_new_files.pop()

    #Return the temporaly path from the actual pdf page
    def get_actual_temp_path(self):
        return self.list_of_new_files[self.actual_pdf_page][0]
    
    def export(self):
        for i in self.list_of_new_files:
            #Check if need to be cropped
            if not i[2].is_empty():
                cropped_pdf = i[2].crop(i[0])
                shutil.copy(cropped_pdf,os.path.join(os.path.dirname(self.path),i[1])+".pdf")
            
            elif os.path.isfile(os.path.join(os.path.dirname(self.path),i[1])+".pdf"):
                self.append_page(os.path.join(os.path.dirname(self.path),i[1])+".pdf",i[0])
            else:
                shutil.copy(i[0],os.path.join(os.path.dirname(self.path),i[1])+".pdf")

    #Rotate all the pdf clockwise. 
    #   Degrees need to be multiple of 90
    @staticmethod
    def rotate(degrees:int,path:str) -> None:
        reader = PyPDF2.PdfReader(path)
        writer = PyPDF2.PdfWriter()

        for i in range(len(reader.pages)):
            page = reader.pages[i]
            page.rotate(degrees)
            writer.add_page(page)
        
        writer.write(path)

