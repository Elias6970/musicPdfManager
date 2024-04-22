import os,shutil,time
from unidecode import unidecode
import zipfile,rarfile
from classes.piece import Piece,Pieces_list
from classes.constants import *
from classes.db_manage import Db_archive
from gui.error_window import Error_window

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
        #print(self.name," ",os.path.abspath(self.path))
        #self.scores:list[str] = self.get_names(os.path.join(path,DIR_SCORES))
        #self.extras:list[str] = self.get_names(os.path.join(path,DIR_EXTRAS))


    #Returns the names of the files inside it avoiding .DS_Store
    def get_names(self,path):
        list = os.listdir(path)
        return [i for i in list if i != ".DS_Store"]

    def get_scores(self):
        return self.get_names(os.path.join(self.path,DIR_SCORES))
    def get_extras(self):
        return self.get_names(os.path.join(self.path,DIR_EXTRAS))
    
    def change_name(self,new_name):
        try:
            shutil.move(self.path,os.path.join(os.path.dirname(self.path),new_name))
            self.set_path(os.path.join(os.path.dirname(self.path),new_name))
            return True
        
        except Exception as e:
            if self.path == os.path.join(os.path.dirname(self.path),new_name): # if the name is the same
                return True
        
        return False

    #-------Unused function made to test the db-----------------
    #Get the names from the database and the names from the dirs to check if are equals
    def export_all_names(self,path):
        file_dirs = open("archivo_names.txt","w")
        file_db = open("db_names.txt","w")
        db_con = Db_archive(DB_NAME)

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
class Archive:
    def __init__(self,db_name,archive_path):
        self.db = Db_archive(db_name)
        self.archive_path = archive_path
        self.pieces = Pieces_list()
        #List of dirs objects
        self.pieces_in_dirs:list[Dir] = []
        #Pieces List
        self.pieces.update_pieces(self.db.get_all_cod_name_digitalized())
        
    """
    #----------------RESULTS----------------
    #With 1603 pieces and 308 digitalized
    #Dir:  0.0008343287467956542
    #Piece:  0.011169951963424683
    #Set:  0.011861127614974976
    #Query:  0.00045802669525146485
    
    #------------------TESTS-----------------
        print("Dir: ",self.test(self.update_pieces_in_dirs))
        print("Piece: ",self.test(self.update_pieces))
        print("Set: ",self.test(self.update_pieces_set))
        print("Query: ",self.test(self.query))


    def test(self,func):
        b = 0
        for i in range(1000):
            r = time.time()
            func()   
            b = b + (time.time() - r)
        return b/1000
    
    def query(self):
        self.get_all_parsed_names()
    """

    #Get the files inside the archive dir    
    def update_pieces_in_dirs(self):
        self.pieces_in_dirs = [] #Reset the variable to avoid duplication
        for i in os.listdir(self.archive_path):
            for j in IGNORE_FILES:
                if i not in j: #Ignore the DS_Store 
                    self.pieces_in_dirs.append(Dir(os.path.join(self.archive_path,i),i))

    #Refactor to use Piece objects not a list of Dirs
    def update_pieces(self):
        self.pieces = []
        for i in self.db.get_all_parsed_names():
            i = i[0]
            if os.path.exists(os.path.join(self.archive_path,i)):
                self.pieces.append(Piece.from_parsed_name(i,os.path.join(self.archive_path,i)))
            else:
                self.pieces.append(Piece.from_parsed_name(i))
    

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
    def get_parsed_name_from_db(self,cod):
        name = self.db.get_with_equals("cod",cod,"cod,name")

        return str(name[0][0])+HYPHEN+unidecode(str(name[0][1])).upper()
    
    #Return the standard name in the dirs structure
    @staticmethod
    def get_parsed_name(cod,name):
        return str(cod)+HYPHEN+unidecode(str(name)).upper() 
    

    #Compare the names in the archive dir with the db and set digitalized to 1 if the dir exists    
    def add_digitalized_mark(self):
        names = os.listdir(RELATIVE_ARCHIVE_PATH())

        for i in names:
            if "DS_Store" not in i:
                cod = self.extract_cod(i)
                self.db.cur.execute("UPDATE {} SET digitalized = 1 WHERE cod = {};".format(DB_NAME,cod))
                        
        self.db.con.commit()




#This class make all the interactions with the files on the archive path
class Archive_file_manager:
    
    #Returns the name of the folder in the directory archive
    #Parsed_name: is the parsed name(cod-NAME) but
    #replaces the forbidden simbols
    #forbidden (space) its replaces:
    #\ ^
    #/ ^
    #: _
    #* +
    #? ¿
    #" '
    #< ^
    #> ^
    #| ^
    @staticmethod
    def parse_name_to_file_manager(parsed_name:str) -> str:
        return parsed_name.replace("\\","^").replace("/","^").replace(":","_").replace("*","+").replace("?","¿").replace('"',"'").replace("<","^").replace(">","^").replace("|","^")
    
    #Move the files to the internal archive deppending if there are scores or extras
    @staticmethod
    def move_files(piece_path:str,files:list):
        try:
            for i in files:
                if File.is_pdf(i):
                    shutil.copy(i,os.path.join(RELATIVE_ARCHIVE_PATH(),piece_path,DIR_SCORES,os.path.basename(i)))
                else:
                    shutil.copy(i,os.path.join(RELATIVE_ARCHIVE_PATH(),piece_path,DIR_EXTRAS,os.path.basename(i)))
            return True
        
        except Exception as e:
            Error_window.print_error(e)
        
        return False
    
    #If the piece doesn't exist or doesn't have any score it returns an empty list
    @staticmethod
    def get_scores(piece_path:str,normalized_name:str) -> list[str]:
        try:
            list = os.listdir(piece_path)
            return [i for i in list if i != ".DS_Store"]
        except FileNotFoundError:
            return []


    #If the piece doesn't exist or doesn't have any exta it returns an empty list
    @staticmethod
    def get_extras(piece_path:str,normalized_name:str) -> list[str]:
        try:
            list = os.listdir(piece_path)
            return [i for i in list if i != ".DS_Store"]
        except FileNotFoundError:
            return []


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
    
    #delete a piece. Recive the stadard name-> num-name ej: 1-HOLA
    @staticmethod
    def delete_piece(parsed_piece_name:str):
        shutil.rmtree(os.path.join(RELATIVE_ARCHIVE_PATH(),parsed_piece_name)) #Delete files
    
    #TODO: Make this
    @staticmethod
    def change_piece_dir_name(cod:int,name:str):
        pass

"""    #Change the name of the folder in the archive directory
    #Recive the cod and the name
    def change_piece_dir_name(self,cod:int,name:str):
        for i in self.pieces_in_dirs:
            if int(Archive.extract_cod(os.path.basename(i.path))) == int(cod):
                if i.change_name(Archive.get_parsed_name(cod,name)):
                    return True
        return False"""

#Reorganice the archive
class Reorganize(Archive):
    def __init__(self,archive_name,db_name,new_archive_path):
        super(Reorganize,self).__init__(archive_name,db_name)

        self.new_archive_path = new_archive_path

        self.create_new_archive()
        self.clear_trash()    
          
  
    
    #Create a new archive with with correct and standart names
    def create_new_archive(self):
        dir_list = os.listdir(self.archive_path)

        for i in dir_list:
            if i not in IGNORE_FILES:
                query = self.db.get_with_equals("cod",self.extract_cod(i),"cod,name")
                new_name = Archive.get_parsed_name(query[0][0],query[0][1])

                Archive_file_manager.make_dir(self.new_archive_path,new_name)

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
                        Error_window.print_error(e,"Error with zip: "+internal_zip_file.filename)


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
                        Error_window.print_error(e,"Error with rar: "+internal_rar_file.filename)



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

        for i in dir_list:
            if "__MACOSX" in i:
                shutil.rmtree(self.archive_path+i)
            
            for root,dirs,files in os.walk(self.new_archive_path+i):
                for j in dirs:
                    if "__MACOSX" in j:
                        shutil.rmtree(os.path.join(root,j))
    

    
