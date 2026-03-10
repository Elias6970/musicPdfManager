import os
from backend.app.files_management.dir import Dir,Dir_Error
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.constants.constants import RELATIVE_ARCHIVE_PATH
class Validate():
    #UNUSED
    @staticmethod
    def validate_selection(src_txt:str,list_of_texts:list[str]) -> bool:
        for i in list_of_texts:
            if src_txt == i:
                return True
            
        return False
    


    @staticmethod
    def check_if_piece_in_list(src_txt:str,list_of_pieces:list[str]) -> Dir:
        """"Check if the src_txt is in the list_of_pieces.
        If it is, return a Dir object with the path and name.
        If it is not, return a Dir_Error object.
        Return the Dir object even if the folder doesn't
        """
        for i in list_of_pieces:
            if src_txt == i:
                folder_name = ArchiveFileManager.parse_name_to_file_manager(i)
                return Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),folder_name),folder_name)
        return Dir_Error()