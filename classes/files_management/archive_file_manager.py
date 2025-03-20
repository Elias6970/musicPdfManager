import os,shutil
from classes.files_management.file import File
from gui.error_window import Error_window
from classes.constants import DIR_SCORES,DIR_EXTRAS,RELATIVE_ARCHIVE_PATH

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
    
    #Change the name of a directory depending on the cod
    @staticmethod
    def change_piece_dir_name(old_name:str,new_name:str):
        os.rename(os.path.join(RELATIVE_ARCHIVE_PATH(),old_name),os.path.join(RELATIVE_ARCHIVE_PATH(),new_name))

