import os,shutil,re,tempfile,datetime
from typing import List,Tuple
from classes.error import *
from classes.files_manage import File,Dir,Archive
from classes.constants import DIR_SCORES
from classes.crop_rectangle import CropRectangle
import PyPDF2

#Represents a pdf to be exported
#   have a path to the original pdf
#   and a list with the new names and temp pdf paths
class Exportable_pdf(File):
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
        if crop_rectangle:
            print(crop_rectangle.get())
        else:
            print("None")
    
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


#Object that controlls the pdfs ONLY IN ONE PIECE DIR
#   actual_pdf_number: index of the pdf in the dir(dir/scores)
#   actual_pdf_page: page of the actual pdf in scores dir
#   pdfs: list of Exportable_pdf objects that have the path of the pdfs, their new names and the path to the temp file
#   
#   THROWS PdfNotFoundException()
class Pdf_controller():
    def __init__(self,dir:Dir,actual_pdf_number=0) -> None:
        self.dir_path = dir.path

        self.actual_pdf_number:int = actual_pdf_number

        pdfs_paths:List[str] = [os.path.join(dir.path,DIR_SCORES,i) for i in dir.get_scores()]
        
        if pdfs_paths == []:
            raise PdfNotFoundException()
        
        self.pdfs:List[Exportable_pdf] = [Exportable_pdf(i) for i in pdfs_paths if os.path.isfile(i)]
         

    #return the actual pdf
    def get_actual_pdf(self):
        return self.pdfs[self.actual_pdf_number]

    #Move the original to a new folder to have a backup 
    #Return the folder name
    def move_originals(self) -> str:
        if not os.path.exists(os.path.join(self.dir_path,"partituras_sin_clasificar")):
            os.mkdir(os.path.join(self.dir_path,"partituras_sin_clasificar"))
       
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not os.path.exists(os.path.join(self.dir_path,"partituras_sin_clasificar",date)):
            os.mkdir(os.path.join(self.dir_path,"partituras_sin_clasificar",date))
            
        for i in self.pdfs:
            shutil.move(i.path,os.path.join(self.dir_path,"partituras_sin_clasificar",date,os.path.basename(i.path)))

        return date

    #Move from backup to scores and delete the original folder
    def move_from_backup_to_partituras(self,folder_name:str):
        for i in os.listdir(os.path.join(self.dir_path,"partituras_sin_clasificar",folder_name)):
            if os.path.isfile(i):
                shutil.move(i,os.path.join(self.dir_path,DIR_SCORES))
        shutil.rmtree(folder_name)

    def export(self):
        backup_dir = self.move_originals()
        try:
            for i in self.pdfs:
                i.export()
        except:
            self.move_from_backup_to_partituras(backup_dir)
        

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
        Exportable_pdf.rotate(degrees,self.last_temp_file_path)
        self.last_rotation = degrees
    
    #Parse the initial input to a standarized program form
    def parse_input(self,input):
        if input == "" and self.last_new_name == "":
            raise EmptyInitialInputException()
        if input == "":
            input_analized = self.last_new_name
        else:
            #Can raise ValueError
            input_analized = Text_analizer.analize(input)
            self.last_new_name = input_analized
        
        return input_analized
    
    
    #Pass the page to the next one
    def next_page(self,rotation_checkbox:bool):
        try:
            return self.pdf_controller.get_actual_pdf().get_actual_temp_path()
        except IndexError:
            pass

        temp_path = self.generate_temp()
        reader = PyPDF2.PdfReader(self.pdf_controller.get_actual_pdf().path)
        writer = PyPDF2.PdfWriter()
        writer.add_page(reader.pages[self.pdf_controller.get_actual_pdf().actual_pdf_page])
        writer.write(temp_path)

        if rotation_checkbox:
            self.rotate(self.last_rotation)

        return temp_path
    


    #Jump to the next piece
    def next_piece(self):
        self.last_rotation = 0
        self.actual_piece += 1
        self.pdf_controller = Pdf_controller(self.pieces_to_classify[self.actual_piece])
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
            self.update_parted_flag_db_function(Archive.extract_cod(self.pieces_to_classify[self.actual_piece].name),True)
            
            self.pdf_controller.export()
            self.next_piece()

        #Finish classifing all the list
        else: 
            #Update the parted flag to 1 in the db
            self.update_parted_flag_db_function(Archive.extract_cod(self.pieces_to_classify[self.actual_piece].name),True)
            self.pdf_controller.export()

            raise NoMorePiecesToClassifyException()

        
        return self.next_page(rotation_checkbox)

            
    #Classify the input
    def classify(self,input:str,crop_rectangle:CropRectangle):
        input_analized = self.parse_input(input)

        self.pdf_controller.get_actual_pdf().add_pdf_page(self.last_temp_file_path,input_analized,crop_rectangle)




class Text_analizer():
    instruments = {
            "w":"general",
            "g":"guion",
            "o":"oboe",
            "f":"flauta",
            "n":"flautin",
            "r":"requinto",
            "c":"clarinete",
            "j":"clarinete_bajo",
            "s":"saxofon",
            "x":"saxofon_tenor",
            "b":"saxofon_baritono",
            "a":"fagot",
            "t":"trompa",
            "l":"fliscorno",
            "e":"trompeta",
            "m":"trombon",
            "d":"bombardino",
            "z":"bajo",
            "u":"tuba",
            "p":"percusion"
        }
    instruments_chars = ','.join(list(instruments.keys()))

    def __init__(self) -> None:
        pass
    
    #Return a tuple with the (instrument,number) or 
    #raise a ValueError if doens't match any re (probably because input has not letters or numbers)
    @staticmethod
    def parse_input(text:str) -> Tuple[str,str|None]:

        #Exception for principal clarinet
        if text == "cp":
            return ("clarinete_pral",None)
        
        elif re.fullmatch(fr'^[{Text_analizer.instruments_chars}]$', text,re.IGNORECASE):
            return (text,None)
        
        elif re.fullmatch(fr'^[{Text_analizer.instruments_chars}]\d$', text,re.IGNORECASE):
            input = re.split(r"(\d+)",text)
            return (str(input[0]),str(input[1]))

        elif re.fullmatch(r"[a-z]+$",text,re.IGNORECASE):
            return (text,None)
        
        elif re.fullmatch(r'^[a-zA-Z]+\d+$',text,re.IGNORECASE):
            input = re.split(r"(\d+)",text)
            return (str(input[0]),str(input[1]))

        elif text == "":
            return ("",None)
        else:
            raise ValueError("Only permited letters and numbers")



    #Analize the input and return the name of the file
    #Can raise ValueError if doesn't match any re
    @staticmethod
    def analize(text:str):
        instrument,num = Text_analizer.parse_input(text)
        if num != None:
            try:
                return Text_analizer.instruments[instrument]+"_"+num
            #If the name is not in the list but is correct
            except KeyError:
                return instrument.lower()+"_"+num
        else:
            try:
                return Text_analizer.instruments[instrument]
            #If the name is not in the list but is correct
            except KeyError as e:
                return instrument.lower()
    

    #Return a list with the internal names of the instruments
    @staticmethod
    def get_internal_names(names:list[str]):
        internal_names:list[str] = []
        for i in names:
            #Quit .pdf
            i = os.path.splitext(i)[0]
            
            try:
                internal_names.append(i.split("_")[0]+i.split("_")[1])
            except IndexError:
                internal_names.append(i.split("_")[0])
            
        return internal_names