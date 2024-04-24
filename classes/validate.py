import os
from classes.files_manage import Dir,Dir_Error
from classes.constants import RELATIVE_ARCHIVE_PATH
class Validate():
    @staticmethod
    def validate_selection(src_txt:str,list_of_texts:list[str]) -> bool:
        for i in list_of_texts:
            if src_txt == i:
                return True
            
        return False
    
    #Check if the name exist in the list of pieces
    #Return a Dir object. If it is not found, it return a Dir_Error obj
    @staticmethod
    def select_window_validate_selection(src_txt:str,list_of_pieces:list[str]) -> Dir:
        for i in list_of_pieces:
            if src_txt == i:
                return Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),i),i)
        return Dir_Error()