import os,sys,shutil,tempfile
from unidecode import unidecode
import zipfile,rarfile
from reportlab.platypus import SimpleDocTemplate,Table,Image
from reportlab.lib import pagesizes,colors
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter,PdfReader
from classes.constants import *
from classes.db_manage import Db
from gui.error_window import Error

class File:
    def __init__(self,path):
        self.path = path
    
    def set_path(self,path):
        self.path = path
    
    def remove(self):
        os.remove(self.path)

    @staticmethod
    def is_pdf(path:str):
        extension = os.path.splitext(path) #Extract the extension
        if ".pdf" == extension[1]:
            return True
        return False


class Print_file(File):
    def __init__(self, path,copies:int):
        super().__init__(path)
        
        self.copies = copies




class Dir(File):
    def __init__(self, path,name=None):
        super().__init__(path)
        self.name = os.path.basename(path)

        self.scores = self.get_names(os.path.join(path,DIR_SCORES))
        self.extras = self.get_names(os.path.join(path,DIR_EXTRAS))


    #Returns the names of the files inside it avoiding .DS_Store
    def get_names(self,path):
        list = os.listdir(path)
        return [i for i in list if i != ".DS_Store"]

   
    def change_name(self,new_name):
        try:
            shutil.move(self.path,os.path.join(os.path.dirname(self.path),new_name))
            self.set_path(os.path.join(os.path.dirname(self.path),new_name))
            return True
        
        except Exception as e:
            Error.print_error(e,"Error tocho")
        
        return False

    #Unused function made to test the db
    #Get the names from the database and the names from the dirs to check if are equals
    def export_all_names(self,path):
        file_dirs = open("archivo_names.txt","w")
        file_db = open("db_names.txt","w")
        db_con = Db(DB_NAME,DB_FILE_NAME)

        names = os.listdir(path)

        for i in names:
            file_dirs.write(i+'\n')
            if i in "DS_Store":
                continue
            actual_index = str(i).split("-",1)[0]
            a = db_con.get_with_equals("cod",actual_index,"cod,name")[0]
            
            file_db.write(str(a[0])+"-"+a[1]+'\n')
        
        file_dirs.close()
        file_db.close()







#The connection with the db is started when the obj is created with the super.
class Archive(Db):
    def __init__(self,db_name,db_file_name,path):
        super(Archive,self).__init__(db_name,db_file_name)
        
        self.archive_path = path

        #List of dirs objects
        self.pieces_in_dirs:list[Dir] = []
        
        #Get the scores and extras of all pieces
        self.update_pieces_in_dirs()

    #Get the files inside the archive dir    
    def update_pieces_in_dirs(self):
        self.pieces_in_dirs = [] #Reset the variable to avoid duplication
        for i in os.listdir(self.archive_path):
            for j in IGNORE_FILES:
                if i not in j: #Ignore the DS_Store 
                    self.pieces_in_dirs.append(Dir(os.path.join(self.archive_path,i),i))

    #Extract the cod giving parsed name(cod+name), ej(1591-ATMURAF)-->1591
    @staticmethod
    def extract_cod(name) -> int:
        one = name.split("-",1)[0]
        two = name.split(" ",1)[0]
        if len(one) < len(two):
            return one
        return two
    

    #Stablish the name to the folders get from the db to standarize the names
    #"cod-name" in capital leters and without accents
    """def get_parsed_name_from_db(self,cod):
        name = self.get_with_equals("cod",cod,"cod,name")

        return str(name[0][0])+HYPHEN+unidecode(str(name[0][1])).upper()""" 
    
    #Return the standard name in the dirs structure
    @staticmethod
    def get_parsed_name(cod,name):
        return str(cod)+HYPHEN+unidecode(str(name)).upper() 
    

    #Create the dirs and return the path
    @staticmethod
    def make_dir(archive_path,name):
        try:
            os.makedirs(os.path.join(archive_path,name,DIR_SCORES)) #Create partituras
        except:
            pass

        try:
            os.makedirs(os.path.join(archive_path,name,DIR_EXTRAS)) #Create extras
        except:
            pass
    #Compare the names in the archive dir with the db and set digitalized to 1 if the dir exists    
    def add_digitalized_mark(self):
        names = os.listdir(RELATIVE_ARCHIVE_PATH)

        for i in names:
            if "DS_Store" not in i:
                cod = self.extract_cod(i)
                self.cur.execute("UPDATE {} SET digitalized = 1 WHERE cod = {};".format(DB_NAME,cod))
                        
        self.con.commit()


    #Export the pdf dossier with the list of scores to be printed
    def export_pdf_dossier_to_print(self,new_pdf_path:str,extra_cover_text:str):
        #Create a temp file because later we need to merge this pdf with the front page with the band logo
        #temp_dossier = tempfile.NamedTemporaryFile(delete=True)
        temp_dossier = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())

        # Read Excel data into a list
        data = self.get_all_to_print()
        data.insert(0,("Digitalizada","Cod","Nombre","Autor","tipo")) #traducir

        # Create a PDF document
        doc = SimpleDocTemplate(temp_dossier, pagesize=pagesizes.landscape(pagesizes.A4),topMargin=15,bottomMargin=10)

        table = Table(data)

        # Customize table appearance
        cell_padding = 1.5
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), cell_padding),
            ('RIGHTPADDING', (0, 0), (-1, -1), cell_padding),
            ('TOPPADDING', (0, 0), (-1, -1), cell_padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), cell_padding),
        ]
        table.spaceAfter = 0
        table.spaceBefore = 0
        table.setStyle(style)
        
        #Modify the front page to put a string
        temp_overlay = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        canvas_overlay = canvas.Canvas(temp_overlay)
        canvas_overlay.setFont("Helvetica-Bold",30)
        canvas_overlay.drawString(453,70,extra_cover_text)
        canvas_overlay.save()
        
        #Merge in the same page the cover and the text
        cover_reader = PdfReader(COVER_PARTITURES_GUIDE)
        overlay_reader = PdfReader(temp_overlay)
        cover_reader.pages[0].merge_page(overlay_reader.pages[0])

        # Build the score list pdf
        story = [table]
        doc.build(story)

        
        #Merge the cover(portada) and the list of score names
        try:
            merged_pdf = PdfWriter()
            if os.path.exists(COVER_PARTITURES_GUIDE) and os.path.exists(temp_dossier):
                merged_pdf.append(cover_reader)
                merged_pdf.append(temp_dossier)
            
            merged_pdf.write(new_pdf_path)
            merged_pdf.close()
            
            #Delete the temp file
            os.unlink(temp_dossier)

            
        except Exception as e:
            Error.print_error(e)
   

    #Change the name of the folder in the archive directory
    #Recive the cod and the name
    def change_piece_dir_name(self,cod:int,name:str):
        for i in self.pieces_in_dirs:
            if int(Archive.extract_cod(os.path.basename(i.path))) == int(cod):
                if i.change_name(Archive.get_parsed_name(cod,name)):
                    return True
        return False

    #Move the files to the internal archive deppending if there are scores or extras
    def move_files(self,score_path,files:list):
        try:
            for i in files:
                if File.is_pdf(i):
                    shutil.copy(i,os.path.join(RELATIVE_ARCHIVE_PATH,score_path,DIR_SCORES,os.path.basename(i)))
                else:
                    shutil.copy(i,os.path.join(RELATIVE_ARCHIVE_PATH,score_path,DIR_EXTRAS,os.path.basename(i)))
            return True
        
        except Exception as e:
            Error.print_error(e)
        
        return False



#Reorganice the archive
class Reorganize(Archive):
    def __init__(self,archive_name,db_name,archive_path,new_archive_path):
        super(Reorganize,self).__init__(archive_name,db_name,archive_path)

        self.new_archive_path = new_archive_path

        self.create_new_archive()
        self.clear_trash()    
          
  
    
    #Create a new archive with with correct and standart names
    def create_new_archive(self):
        dir_list = os.listdir(self.archive_path)

        for i in dir_list:
            if i not in IGNORE_FILES:
                query = self.get_with_equals("cod",self.extract_cod(i),"cod,name")
                new_name = Archive.get_parsed_name(query[0][0],query[0][1])

                Archive.make_dir(self.new_archive_path,new_name)

                for root,dir,files in os.walk(self.archive_path+i):
                    for j in files:
                        if j not in IGNORE_FILES:
                            self.copy_file(os.path.join(root,j),new_name)
                    


    #Copy the file to the new path deppending the type of file 
    def copy_file(self,actual_path,name):
        if ".pdf" in actual_path:
            shutil.copyfile(actual_path,os.path.join(self.new_archive_path,name,DIR_SCORES,os.path.basename(actual_path)))
        
        elif ".PDF" in actual_path: # To change PDF to pdf(not capital letters)
            name_without_extension = os.path.splitext(os.path.basename(actual_path))[0]
            shutil.copyfile(actual_path,os.path.join(self.new_archive_path,name,DIR_SCORES,name_without_extension+".pdf"))

        elif ".zip" in actual_path:
            with zipfile.ZipFile(actual_path,'r') as zip:
                for internal_zip_file in zip.infolist():
                    if ".pdf" in internal_zip_file.filename:
                        dir_name = os.path.join(name,DIR_SCORES)
                    elif "DS_Store" in internal_zip_file.filename:
                        continue
                    else:
                        dir_name = os.path.join(name,DIR_EXTRAS)
        
                    try:
                        zip.extract(internal_zip_file.filename,path=self.new_archive_path+dir_name)
                        self.delete_intermediate_folders(dir_name,internal_zip_file,internal_zip_file.is_dir())

                    except Exception as e:
                        Error.print_error(e,"Error with zip: "+internal_zip_file.filename)
                        #print("Error",e," with: ",internal_zip_file.filename)

        elif ".rar" in actual_path:
            with rarfile.RarFile(actual_path, 'r') as rar:
                for internal_rar_file in rar.infolist():
                    if ".pdf" in internal_rar_file.filename:  
                        dir_name = os.path.join(name,DIR_SCORES)
                    elif "DS_Store" in internal_rar_file.filename:
                        continue
                    else:
                        dir_name = os.path.join(name,DIR_EXTRAS)

                    try:
                        rar.extract(internal_rar_file.filename,path=self.new_archive_path+dir_name)
                        self.delete_intermediate_folders(dir_name,internal_rar_file,internal_rar_file.isdir())
                    
                    except Exception as e:
                        Error.print_error(e,"Error with rar: "+internal_rar_file.filename)
                        #print("Error",e," with: ",internal_rar_file.filename)


        elif "DS_Store" in actual_path:
            return
        
        else:
            shutil.copyfile(actual_path,os.path.join(self.new_archive_path+name,DIR_EXTRAS,os.path.basename(actual_path)))


    #Delete the folders that are inside rar and zip files
    def delete_intermediate_folders(self,dir_name,file,is_dir):
        if not is_dir:
            os.rename(os.path.join(self.new_archive_path,dir_name,file.filename),os.path.join(self.new_archive_path,dir_name,os.path.basename(file.filename)))
            
            if os.path.dirname(file.filename) != "" and os.path.dirname(file.filename) != "partituras" and os.path.dirname(file.filename) != "extras": #Is a dir
                os.rmdir(os.path.join(self.new_archive_path,dir_name,os.path.dirname(file.filename)))   

        elif is_dir and os.path.dirname(file.filename) != "extras":
            os.rmdir(os.path.join(self.new_archive_path,dir_name,file.filename))
        


    #Clear the __MACOSX dirs
    def clear_trash(self):
        dir_list = os.listdir(self.new_archive_path)
        #print(dir_list)
        for i in dir_list:
            if "__MACOSX" in i:
                shutil.rmtree(self.archive_path+i)
            
            for root,dirs,files in os.walk(self.new_archive_path+i):
                for j in dirs:
                    if "__MACOSX" in j:
                        shutil.rmtree(os.path.join(root,j))
    

    
