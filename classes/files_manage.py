import os,sys,shutil
from classes.constants import *
from classes.db_manage import Db
from unidecode import unidecode
import zipfile,rarfile
from unpack_recursive import unpack_recursive

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
        if(self.scores == []):
            print(path)
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
    def __init__(self,name,path):
        super(Archivo,self).__init__(name)
        
        self.archive_path = path


        #List of dirs objects
        self.list_of_pieces = []
        
        for i in os.listdir(path):
            if i not in IGNORE_FILES: #Ignore the DS_Store 
                self.list_of_pieces.append(Dir(path+i,i))
        


    def get_dir_names(self):
        names = []
        for i in self.list_of_pieces:
            names.append(i.name)
        
        return names
    


#Reorganice the archive
class Reorganize(Archivo):
    def __init__(self,db_name,archive_path):
        
        super(Reorganize,self).__init__(db_name,archive_path)
        

        self.new_path = "../newArchivo/"
        
        
        #self.create_new_archive()
        #self.clear_trash()

    #Get the cod giving the cod+name, ej(1591-ATMURAF)
    def get_cod(self,name) -> int:
        one = name.split("-",1)[0]
        two = name.split(" ",1)[0]
        if len(one) < len(two):
            return one
        return two
    
    #Stablish the name to the folders get from the db to standarize the names
    #cod-name in capital leters and without accents
    def get_new_name(self,cod):
        name = self.get_with_equals("cod",cod,"cod,name")

        return str(name[0][0])+HYPHEN+unidecode(str(name[0][1])).upper()     
          
    
    #Create the dirs and return the path
    def create_dirs(self,name):
        try:
            os.makedirs(self.new_path+name+DIR_SCORES) #Create /partituras/
        except:
            pass

        try:
            os.makedirs(self.new_path+name+DIR_EXTRAS) #Create /extras/
        except:
            pass
  
    
    #Create a new archive with with correct and standart names
    def create_new_archive(self):
        dir_list = os.listdir(self.archive_path)

        for i in dir_list:
            if i not in IGNORE_FILES:
                new_name = self.get_new_name(self.get_cod(i))
                self.create_dirs(new_name)

                for root,dir,files in os.walk(self.archive_path+i):
                    for j in files:
                        if j not in IGNORE_FILES:
                            self.copy_file(root+SLASH+j,new_name)
                    


    #Copy the file to the new path deppending the type of file 
    def copy_file(self,actual_path,name):
        if ".pdf" in actual_path:
            shutil.copyfile(actual_path,self.new_path+name+DIR_SCORES+os.path.basename(actual_path))
        
        elif ".PDF" in actual_path: # To change PDF to pdf(not capital letters)
            name_without_extension = os.path.splitext(os.path.basename(actual_path))[0]
            shutil.copyfile(actual_path,self.new_path+name+DIR_SCORES+name_without_extension+".pdf")

        elif ".zip" in actual_path:
            with zipfile.ZipFile(actual_path,'r') as zip:
                for internal_zip_file in zip.infolist():
                    if ".pdf" in internal_zip_file.filename:
                        try:
                            zip.extract(internal_zip_file,self.new_path+name+DIR_SCORES)
                        except:
                            print("Error with: ",internal_zip_file.filename)
                    elif "DS_Store" in internal_zip_file.filename:
                        continue
                    else:
                        try:
                            zip.extract(internal_zip_file,self.new_path+name+DIR_EXTRAS)
                        except:
                            print("Error with: ",internal_zip_file.filename)
        
        elif ".rar" in actual_path:
            with rarfile.RarFile(actual_path, 'r') as rar:
                for internal_rar_file in rar.infolist():
                    if ".pdf" in internal_rar_file.filename:
                        try:
                            rar.extract(internal_rar_file,path=self.new_path+name+DIR_SCORES)
                        except:
                            print("Error with: ",internal_rar_file.filename)
                    
                    elif "DS_Store" in internal_rar_file.filename:
                        continue
                    else:
                        try:
                            rar.extract(internal_rar_file,path=self.new_path+name+DIR_EXTRAS)
                        except:
                            print("Error with: ",internal_rar_file.filename)
        
        elif "DS_Store" in actual_path:
            return
        
        else:
            shutil.copyfile(actual_path,self.new_path+name+DIR_EXTRAS+os.path.basename(actual_path))


    #Clear the __MACOSX dirs
    def clear_trash(self):
        dir_list = os.listdir(self.new_path)
        #print(dir_list)
        for i in dir_list:
            if "__MACOSX" in i:
                shutil.rmtree(self.archive_path+i)
            
            for root,dirs,files in os.walk(self.new_path+i):
                for j in dirs:
                    if "__MACOSX" in j:
                        shutil.rmtree(root+SLASH+j)
                    
