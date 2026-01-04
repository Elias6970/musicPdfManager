import os,tempfile
from classes.error import EmptyInitialInputException, FirstPageException, NoMorePiecesToClassifyException
from classes.utils.name_manager import NameManager
from classes.files_management.dir import Dir
from classes.files_management.archive import Archive
from classes.crop_rectangle import CropRectangle
from classes.classifier.exportable_pdf import ExportablePdf
from classes.classifier.text_analizer import TextAnalizer
from classes.classifier.pdf_controller import PdfController
import pypdf

#This class manage how pieces are classified.
class Classifier:
    def __init__(self,pieces_to_classify:list[Dir],update_parted_flag_db_function) -> None:
        self.actual_piece:int = -1#is the number of the piece in peices_list
        self.last_temp_file_path:str
        self.last_new_name:str = ""
        self.last_rotation:int = 0 #Save the last rotation
        self.actual_piece_name:str = ""

        self.pieces_to_classify = pieces_to_classify
        self.update_parted_flag_db_function = update_parted_flag_db_function
    
    #Used to show the first page of the classification
    def first_page(self) -> str:
        self.next_piece()
        return self.next_page(False)
    
    #Generates a temp file path
    def generate_temp(self) -> str:
        path = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        self.last_temp_file_path = path
        return path

    #Rotate a file x degress
    def rotate(self,degrees):
        ExportablePdf.rotate(degrees,self.last_temp_file_path)
        self.last_rotation = degrees
    
    #Parse the initial input to a standarized program form
    def parse_input(self,input):
        if input == "" and self.last_new_name == "":
            raise EmptyInitialInputException()
        if input == "":
            input_analized = self.last_new_name
        else:
            #Can raise ValueError
            input_analized = TextAnalizer.analize(input)
            self.last_new_name = input_analized
        
        return input_analized
    
    
    #Pass the page to the next one
    def next_page(self,rotation_checkbox:bool):
        try:
            return self.pdf_controller.get_actual_pdf().get_actual_temp_path()
        except IndexError:
            pass

        temp_path = self.generate_temp()
        reader = pypdf.PdfReader(self.pdf_controller.get_actual_pdf().path)
        writer = pypdf.PdfWriter()
        writer.add_page(reader.pages[self.pdf_controller.get_actual_pdf().actual_pdf_page])
        writer.write(temp_path)

        if rotation_checkbox:
            self.rotate(self.last_rotation)

        return temp_path
    


    #Jump to the next piece
    def next_piece(self):
        self.last_rotation = 0
        self.actual_piece += 1
        self.pdf_controller = PdfController(self.pieces_to_classify[self.actual_piece])
        self.actual_piece_name = os.path.basename(self.pieces_to_classify[self.actual_piece].path)

    #Manage the functionality to go to the previous page
    def previous_page_manager(self):
        if self.pdf_controller.actual_pdf_number == 0 and self.pdf_controller.get_actual_pdf().actual_pdf_page == 0:
            raise FirstPageException()
        
        elif self.pdf_controller.get_actual_pdf().actual_pdf_page == 0:
            self.pdf_controller.actual_pdf_number -= 1
        else:
            self.pdf_controller.get_actual_pdf().actual_pdf_page -= 1
        
        self.pdf_controller.get_actual_pdf().remove_latest_page()

        return self.next_page(False)


    #Decide what is the next pdf page that need to be showed
    #1-Check if the actual pdf have more pages
    #2-Check if the actual piece have more pdfs
    #3-Check if there are more pieces to classify
    def next_page_manager(self,rotation_checkbox:bool):
        self.pdf_controller.get_actual_pdf().actual_pdf_page += 1

        if self.pdf_controller.get_actual_pdf().actual_pdf_page < self.pdf_controller.get_actual_pdf().num_pages:
            pass
        
        elif self.pdf_controller.actual_pdf_number+1 < len(self.pdf_controller.pdfs):
            self.pdf_controller.actual_pdf_number += 1

        
        elif self.actual_piece+1 < len(self.pieces_to_classify):
            #Update the parted flag to 1 in the db
            self.update_parted_flag_db_function(NameManager.get_cod(self.pieces_to_classify[self.actual_piece].name),True)
            
            self.pdf_controller.export()
            self.next_piece()

        #Finish classifing all the list
        else: 
            #Update the parted flag to 1 in the db
            self.update_parted_flag_db_function(NameManager.get_cod(self.pieces_to_classify[self.actual_piece].name),True)
            self.pdf_controller.export()
            raise NoMorePiecesToClassifyException()

        
        return self.next_page(rotation_checkbox)

            
    #Classify the input
    def classify(self,input:str,crop_rectangle:CropRectangle):
        input_analized = self.parse_input(input)

        self.pdf_controller.get_actual_pdf().add_pdf_page(self.last_temp_file_path,input_analized,crop_rectangle)

