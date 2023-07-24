import os,sys,shutil
from classes.constants import *
from classes.db_manage import Db
from unidecode import unidecode
import zipfile,rarfile

class File:
    def __init__(self,path):
        self.path = path
    
    def set_path(self,path):
        self.path = path
    
    def remove(self):
        os.remove(self.path)






class Dir(File):
    def __init__(self, path,name=None):
        super().__init__(path)
         
        self.scores = self.get_names(path + DIR_SCORES)
        self.extras = self.get_names(path + DIR_EXTRAS)


    #With a path, returns the names of the files inside it
    def get_names(self,path):
        return os.listdir(path)

    
    #Get the names from the database and the names from the dirs to check if are equals
    def export_all_names(self,path):
        file_dirs = open("archivo_names.txt","w")
        file_db = open("db_names.txt","w")
        db_con = Db(DB_NAME)

        names = os.listdir(path)
        #indexes = []

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
class Archivo(Db):
    def __init__(self,name,db_name,path):
        super(Archivo,self).__init__(db_name)
        
        self.archive_path = path

        #List of dirs objects
        self.pieces_in_dirs = []
        
        #Get the scores and extras of all pieces
        for i in os.listdir(path):
            for j in IGNORE_FILES:
                if i not in j: #Ignore the DS_Store 
                    self.pieces_in_dirs.append(Dir(path+i,i))
        


    def get_dir_names(self):
        names = []
        for i in self.pieces_in_dirs:
            names.append(i.name)
        
        return names
    







#Reorganice the archive
class Reorganize(Archivo):
    def __init__(self,archive_name,db_name,archive_path,new_archive_path):
        super(Reorganize,self).__init__(archive_name,db_name,archive_path)

        self.new_archive_path = new_archive_path

        self.create_new_archive()
        self.clear_trash()


    #Extract the cod giving parsed name(cod+name), ej(1591-ATMURAF)-->1591
    def extract_cod(self,name) -> int:
        one = name.split("-",1)[0]
        two = name.split(" ",1)[0]
        if len(one) < len(two):
            return one
        return two
    
    #Stablish the name to the folders get from the db to standarize the names
    #"cod-name" in capital leters and without accents
    def get_parsed_name(self,cod):
        name = self.get_with_equals("cod",cod,"cod,name")

        return str(name[0][0])+HYPHEN+unidecode(str(name[0][1])).upper()     
          
    
    #Create the dirs and return the path
    def mk_score_and_extras_dirs(self,name):
        try:
            os.makedirs(self.new_archive_path+name+DIR_SCORES) #Create /partituras/
        except:
            pass

        try:
            os.makedirs(self.new_archive_path+name+DIR_EXTRAS) #Create /extras/
        except:
            pass
  
    
    #Create a new archive with with correct and standart names
    def create_new_archive(self):
        dir_list = os.listdir(self.archive_path)

        for i in dir_list:
            if i not in IGNORE_FILES:
                new_name = self.get_parsed_name(self.extract_cod(i))
                self.mk_score_and_extras_dirs(new_name)

                for root,dir,files in os.walk(self.archive_path+i):
                    for j in files:
                        if j not in IGNORE_FILES:
                            self.copy_file(os.path.join(root,j),new_name)
                    


    #Copy the file to the new path deppending the type of file 
    def copy_file(self,actual_path,name):
        if ".pdf" in actual_path:
            shutil.copyfile(actual_path,self.new_archive_path+name+DIR_SCORES+os.path.basename(actual_path))
        
        elif ".PDF" in actual_path: # To change PDF to pdf(not capital letters)
            name_without_extension = os.path.splitext(os.path.basename(actual_path))[0]
            shutil.copyfile(actual_path,self.new_archive_path+name+DIR_SCORES+name_without_extension+".pdf")

        elif ".zip" in actual_path:
            with zipfile.ZipFile(actual_path,'r') as zip:
                for internal_zip_file in zip.infolist():
                    if ".pdf" in internal_zip_file.filename:
                        dir_name = name+DIR_SCORES
                    elif "DS_Store" in internal_zip_file.filename:
                        continue
                    else:
                        dir_name = name+DIR_EXTRAS
        
                    try:
                        zip.extract(internal_zip_file.filename,path=self.new_archive_path+dir_name)
                        self.delete_intermediate_folders(dir_name,internal_zip_file,internal_zip_file.is_dir())

                    except Exception as e:
                        print("Error",e," with: ",internal_zip_file.filename)

        elif ".rar" in actual_path:
            with rarfile.RarFile(actual_path, 'r') as rar:
                for internal_rar_file in rar.infolist():
                    if ".pdf" in internal_rar_file.filename:  
                        dir_name = name+DIR_SCORES
                    elif "DS_Store" in internal_rar_file.filename:
                        continue
                    else:
                        dir_name = name+DIR_EXTRAS

                    try:
                        rar.extract(internal_rar_file.filename,path=self.new_archive_path+dir_name)
                        self.delete_intermediate_folders(dir_name,internal_rar_file,internal_rar_file.isdir())
                    
                    except Exception as e:
                        print("Error",e," with: ",internal_rar_file.filename)


        elif "DS_Store" in actual_path:
            return
        
        else:
            shutil.copyfile(actual_path,self.new_archive_path+name+DIR_EXTRAS+os.path.basename(actual_path))

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
    
