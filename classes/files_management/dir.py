import os,shutil
from classes.files_management.file import File
from classes.db_manage import Db_archive
from classes.constants import DIR_SCORES,DIR_EXTRAS, DB_NAME

class Dir(File):
    def __init__(self, path,name=None):
        super().__init__(path)
        if name == None:
            self.name = os.path.basename(path)
        else:
            self.name = name

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

#Class for returning errors
class Dir_Error(Dir):
    def __init__(self):
        super().__init__("Error")