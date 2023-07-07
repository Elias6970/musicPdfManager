import os,sys
from classes.constants import *
from classes.db_manage import Db


class File:
    def __init__(self,path):
        self.path = path
    
    def set_path(self,path):
        self.path = path
    
    def remove(self):
        os.remove(self.path)



class Dir(File):
    def __init__(self, path):
        super().__init__(path)

        #self.scores = self.get_names(path + DIR_SCORES)
        self.scores = self.get_names(path)


    #With a path, returns the names of the files inside
    def get_names(self,path):
        files = os.listdir(path)
        return files

    
    #Get the names from the database and the names from the dirs to check if are equals
    def export_all_names(self,path):
        file_dirs = open("archivo_names.txt","w")
        file_db = open("db_names.txt","w")
        db_con = Db(DB_NAME)

        names = os.listdir(path)
        #indexes = []

        for i in names:
            file_dirs.write(i+'\n')
            if i in ".DS_Store":
                continue
            actual_index = str(i).split("-",1)[0]
            a = db_con.get_with_equals("cod",actual_index,"cod,name")[0]
            
            file_db.write(str(a[0])+"-"+a[1]+'\n')
        
        file_dirs.close()
        file_db.close()



class Archivo(Dir):
    def __init__(self, path):
        super().__init__(path)

        print(self.scores)
        
        
        