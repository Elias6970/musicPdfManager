from backend.app.printers.printeable_element import PrinteableElement
from backend.app.files_management.dir import Dir

#This class represents an abstract printer
#The methods need to be implemented in the child backend.app
class Printer:
    def __init__(self) -> None:
        self.actual_piece_dir:Dir
        self.items:list[PrinteableElement] = []
    
    def set_actual_piece(self,new_piece:Dir):
        self.actual_piece_dir = new_piece

    def add(self,item:PrinteableElement):
        self.items.append(item)

    def remove(self,id:int) -> bool:
        try:
            for i in self.items:
                if i.id == id:
                    self.items.remove(i)
                    return True
        except ValueError:
            pass

        return False

    def export(self,path:str) -> None:
        pass
