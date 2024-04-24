from unidecode import unidecode
from classes.constants import RELATIVE_ARCHIVE_PATH
from classes.error import PieceNotFoundException

#Class that represents a piece
#raise PathNotFoundException if the path doesn't exits unless is None
class Piece:
    def __init__(self,cod:int,name:str,parsed_name=None,digitalized:bool=False):
        self.cod = cod
        self.name = name
        self.digitalized:bool = digitalized

        if parsed_name == None:
            self.parsed_name = self.update_parsed_name()   
        else:
            self.parsed_name = parsed_name 
        

    #Constructor overload that gets the parsed name
    @classmethod
    def from_parsed_name(cls,std_name:str,digitalized:bool=False):
        cod = Piece.extract_cod(std_name)
        name = Piece.extract_name(std_name)
        return cls(cod,name,std_name,digitalized)
    
    
    def update_parsed_name(self) -> str:
        return str(self.cod) + "-" + unidecode(self.name).upper()

    
    #Return the cod of a parsed name
    @staticmethod
    def extract_cod(std_name:str) -> int:
        one = std_name.split("-",1)[0]
        two = std_name.split(" ",1)[0]
        if len(one) < len(two):
            return int(one)
        return int(two)
    
    #Return the name of a parsed name
    @staticmethod
    def extract_name(std_name:str) -> str:
        return std_name.split("-",maxsplit=1)[1]
    
    @staticmethod
    def make_parsed_name(cod,name) -> str:
        return str(cod) + "-" + name

#List of pieces
class Pieces_list:
    pieces:list[Piece]
    def __init__(self):
        self.pieces = []
    #Refactor to use Piece objects not a list of Dirs
    #parsed names is a list of cod-name, ej: 18-PETRER
    def update_pieces_parsed_names(self,names:list):
        for i in names:
            self.pieces.append(Piece.from_parsed_name(i[0]))
    
    def update_pieces(self,cod_names:list[tuple]):
        self.pieces.clear()
        for i in cod_names:
            self.add(i[0],i[1],digitalized=bool(i[2]))

    #Return a list with digitalized parsed names
    def get_digitalized_parsed_names(self) -> list[str]:
        return [i.parsed_name for i in self.pieces if i.digitalized]
    
    #Return a list with all parsed names
    def get_parsed_names(self) -> list[str]:
        return [i.parsed_name for i in self.pieces]

    #raise PathNotFoundException if the path doesn't exits unless is None
    def add(self,cod:int,name:str,parsed_name=None,digitalized:bool=False):
        self.pieces.append(Piece(cod,name,parsed_name,digitalized))
        return True

    #raise PathNotFoundException if the path doesn't exits unless is None      
    def add_parsed(self,parsed_name,digitalized:bool=False):
        self.pieces.append(Piece.from_parsed_name(parsed_name,digitalized))
        return True

    #Raise ValueError if Piece doesn't exists
    def remove(self,cod:int) -> bool:
        for i in self.pieces:
            if i.cod == cod:
                self.pieces.remove(i)
                return True
        return False
    
    #Raise ValueError if Piece doesn't exists
    def remove_parsed(self,parsed_name:str) -> bool:
        return self.remove(Piece.extract_cod(parsed_name))
    
    #Return a copy of an element. Raise PieceNotFoundException if the piece doesn't exists
    def get(self,cod:int):
        try:
            return [i for i in self.pieces if i.cod == cod][0]
        except IndexError:
            raise PieceNotFoundException()
    
    #Update the name of a piece
    def update_cod_and_name(self,old_cod:int,new_cod,new_name:str):
        for i in self.pieces:
            if i.cod == old_cod:
                i.cod = new_cod
                i.name = new_name
                i.parsed_name = i.update_parsed_name()
                return True
        return False