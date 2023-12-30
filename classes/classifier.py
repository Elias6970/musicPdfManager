import os,shutil,re
from typing import List,Tuple
from classes.error import PdfNotFoundException
from classes.files_manage import File,Dir
from classes.constants import DIR_SCORES
import PyPDF2

#Represents a pdf to be exported
#   have a path to the original pdf
#   and a list with the new names and temp pdf paths
class Exportable_pdf(File):
    def __init__(self,path) -> None:
        super().__init__(path)

        self.num_pages:int = len(PyPDF2.PdfReader(path).pages)

        self.actual_pdf_page:int = 0

        #The list have tuples with (temp_file_path,new_name)
        self.list_of_new_files:List[Tuple[str,str]] = []


    #Append a new page to an existing temp pdf in list_of_new_files
    @staticmethod
    def append_page(file_src:str,to_append:str):
        merger = PyPDF2.PdfMerger()
        merger.append(PyPDF2.PdfReader(open(file_src, 'rb')))
        merger.append(PyPDF2.PdfReader(open(to_append, 'rb')))
        merger.write(file_src)


    #Add a new page to the list of new files.
    #   if new_name exists in the list_of_new_files append this temp pdf
    #       to the one that is in the list
    #   if not, appends the new pdf to the list with its name
    def add_pdf_page(self,temp_file_path:str,new_name:str) -> None:
        for i in self.list_of_new_files:
            if(i[1] == new_name):
                self.append_page(i[0],temp_file_path)
                return None
            
        self.list_of_new_files.append((temp_file_path,new_name))
        
    
    def export(self):
        for i in self.list_of_new_files:
            if os.path.isfile(os.path.join(os.path.dirname(self.path),i[1])+".pdf"):
                self.append_page(os.path.join(os.path.dirname(self.path),i[1])+".pdf",i[0])
            else:
                shutil.copy(i[0],os.path.join(os.path.dirname(self.path),i[1])+".pdf")



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

        pdfs_paths:List[str] = [os.path.join(dir.path,DIR_SCORES,i) for i in dir.scores]
        
        if pdfs_paths == []:
            raise PdfNotFoundException()
        
        self.pdfs:List[Exportable_pdf] = [Exportable_pdf(i) for i in pdfs_paths if os.path.isfile(i)]
         
        """m=0
        for i in pdfs_paths:
            self.pdfs[0].add_new_page(i,"c"+str(m))
            m+=1 
        self.pdfs[0].export()"""

    #return the actual pdf
    def get_actual_pdf(self):
        return self.pdfs[self.actual_pdf_number]


    def move_originals(self):
        if not os.path.exists(os.path.join(self.dir_path,"partituras_antiguo")):
            os.mkdir(os.path.join(self.dir_path,"partituras_antiguo"))

        for i in self.pdfs:
            shutil.move(i.path,os.path.join(self.dir_path,"partituras_antiguo",os.path.basename(i.path)))


    def export(self):
        for i in self.pdfs:
            i.export()
        
        self.move_originals()
        


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
            "d":"bajo",
            "n":"tuba",
            "p":"percusion"
        }
    instruments_chars = ','.join(list(instruments.keys()))

    def __init__(self) -> None:
        pass
    
    #Return a tuple with the (instrument,number) or none if not match with any re
    @staticmethod
    def parse_input(text:str):# -> Tuple[str,int|None] | None:
        #if len(text) <= 2:
        #Exception for principal clarinet
        if text == "cp":
            return ("clarinete_pral",None)
        
        elif re.fullmatch(fr'^[{Text_analizer.instruments_chars}]$', text,re.IGNORECASE):
            return (text,None)
        
        elif re.fullmatch(fr'^[{Text_analizer.instruments_chars}]\d$', text,re.IGNORECASE):
            input = re.split(r"(\d+)",text)
            return (str(input[0]),int(input[1]))

        elif re.fullmatch(r"[a-z]{2,}$",text,re.IGNORECASE):
            return (text,None)
        
        #char+number
        elif re.fullmatch(r'^(?:[a-zA-Z]{2,}\d)$',text,re.IGNORECASE):
            input = re.split(r"(\d+)",text)
            return (str(input[0]),int(input[1]))

        elif text == "":
            return ("",None)
        else:
            raise ValueError()



    #Analize the input and return the name of the file
    @staticmethod
    def analize(text:str):
        instrument,num = Text_analizer.parse_input(text)
        if num != None:
            try:
                return Text_analizer.instruments[instrument]+"_"+str(num)
            #If the name is not in the list but is correct
            except KeyError:
                return instrument.lower()+"_"+str(num)
        else:
            try:
                return Text_analizer.instruments[instrument]
            #If the name is not in the list but is correct
            except KeyError as e:
                return instrument.lower()
            