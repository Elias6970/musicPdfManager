from classes.files_manage import Dir

class Validate():
    @staticmethod
    def validate_selection(src_txt:str,list_of_texts:list[str]) -> bool:
        for i in list_of_texts:
            if src_txt == i:
                return True
            
        return False
    
    #Check if the name exist in the list of pieces
    #return the list of scores(the insturments available)
    @staticmethod
    def select_window_validate_selection(src_txt:str,list_of_pieces:list[Dir]) -> Dir|None:
        for i in list_of_pieces:
            if src_txt == i.name:
                return i
        return None