import os
from classes.files_management.dir import Dir,Dir_Error
from classes.constants.constants import RELATIVE_ARCHIVE_PATH
class Validate():
    @staticmethod
    def validate_selection(src_txt:str,list_of_texts:list[str]) -> bool:
        for i in list_of_texts:
            if src_txt == i:
                return True
            
        return False
    


    @staticmethod
    def check_if_exist_dir(src_txt:str,list_of_pieces:list[str]) -> Dir:
        """"Check if the src_txt is in the list_of_pieces.
        If it is, return a Dir object with the path and name.
        If it is not, return a Dir_Error object.
        """
        for i in list_of_pieces:
            if src_txt == i:
                return Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),i),i)
        return Dir_Error()