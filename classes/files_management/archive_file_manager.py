import os,shutil
from classes.files_management.file import File
from gui.error_window import Error_window
from classes.constants.constants import DIR_SCORES,DIR_EXTRAS,RELATIVE_ARCHIVE_PATH

#This class make all the interactions with the files on the archive path
class ArchiveFileManager:
    
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
    
    #
    @staticmethod
    def move_files_to_piece_dir(piece_path:str,files:list):
        """Move the files to the internal folder deppending if there are scores or extras"""
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
    
    @staticmethod
    def move_files(path:str,new_path:str) -> str:
        """
        Move a file, files of folder from path to new_path
        Returns the new path if the file was moved successfully
        If the file is already in the new path, it returns the same path
        If the file couldn't be moved, it returns an empty string
        """
        try:
            shutil.move(path,os.path.join(os.path.dirname(path),new_path))
            return os.path.join(os.path.dirname(path),new_path)
        
        except Exception as e:
            if path == os.path.join(os.path.dirname(path),new_path): # if the name is the same
                return path
        
        return ""


    @staticmethod
    def _get_names(path:str) -> list[str]:
        """
        Get the names of the files inside a path avoiding .DS_Store.
        If the path doesn't exist or doesn't have anything inside it returns an empty list
        """
        try:
            list = os.listdir(path)
            return [i for i in list if i != ".DS_Store"]
        except FileNotFoundError:
            return []
        
    
    @staticmethod
    def get_scores(piece_path:str) -> list[str]:
        """
        Get the path of the piece without the Scores dir extension  
        and return the list of scores inside it
        """
        return ArchiveFileManager._get_names(os.path.join(piece_path,DIR_SCORES))


    #If the piece doesn't exist or doesn't have any exta it returns an empty list
    @staticmethod
    def get_extras(piece_path:str) -> list[str]:
        """
        Get the path of the piece without the Extras dir extension
        and return the list of extras inside it
        """
        return ArchiveFileManager._get_names(os.path.join(piece_path,DIR_EXTRAS))

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
    
    #Change the name of a directory depending on the cod
    @staticmethod
    def change_piece_dir_name(old_name:str,new_name:str):
        os.rename(os.path.join(RELATIVE_ARCHIVE_PATH(),old_name),os.path.join(RELATIVE_ARCHIVE_PATH(),new_name))

    
    @staticmethod
    def get_piece_path(cod:str) -> str:
        """
        Get the piece path in the archive directory using only the cod (it only checks cod- the name is not checked)
        If the piece doesn't exist it returns an empty string
        """
        for i in os.listdir(RELATIVE_ARCHIVE_PATH()):
            if i.startswith(str(cod) + "-"):
                return os.path.join(RELATIVE_ARCHIVE_PATH(),i)
        return ""

