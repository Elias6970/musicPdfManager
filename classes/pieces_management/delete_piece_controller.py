from classes.files_management.archive import Archive
from classes.utils.name_manager import NameManager

class DeletePieceController:
    def __init__(self,archive:Archive):
        self.archive = archive

    def delete_piece(self,text:str):
        if self.archive.pieces.exists_parsed(text):
            cod = int(NameManager.get_cod(text))
            self.archive.delete_piece(cod,text)
            return True