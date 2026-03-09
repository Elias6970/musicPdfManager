import os,shutil,re
from backend.app.utils.name_manager import NameManager
from backend.app.files_management.file import File
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.db_manage import Db_archive
from backend.app.constants.constants import DB_PIECES_TABLE

class Dir(File):
    def __init__(self, path,name=None):
        super().__init__(path)
        if name == None:
            self.name = os.path.basename(path)
        else:
            self.name = name

    def search_and_set_path(self) -> bool:
        """
        Try to search if the path exists in the archive path using the cod of the dir
        If the path exists, set the path to the dir and return True
        If the path does not exist, return False
        """
        path = ArchiveFileManager.get_piece_path(NameManager.get_cod(self.name))
        if path != "":
            self.set_path(path)
            return True
        return False

    def get_scores(self):
        """Return the scores names with the extension (always .pdf)"""
        return ArchiveFileManager.get_scores(self.path)
    
    def get_extras(self):
        """Return the extras names with the extensions"""
        return ArchiveFileManager.get_extras(self.path)
    
    
    def get_score_names_without_extension(self):
        """Return the score names without the extension (always .pdf)"""
        return [os.path.splitext(i)[0] for i in self.get_scores()]
    

    def change_name(self,new_name:str) -> bool:
        """Change the name of the dir"""
        path = ArchiveFileManager.move_files(self.path,new_name)
        
        if path == "":
            return False
        self.set_path(path)
        return True

    #-------Unused function made to test the db-----------------
    #Get the names from the database and the names from the dirs to check if are equals
    def export_all_names(self,path):
        file_dirs = open("archivo_names.txt","w")
        file_db = open("db_names.txt","w")
        db_con = Db_archive(DB_PIECES_TABLE)

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

    def __str__(self):
        return f"Dir: {self.name} Path: {self.path}"

#Class for returning errors
class Dir_Error(Dir):
    def __init__(self):
        super().__init__("Error")