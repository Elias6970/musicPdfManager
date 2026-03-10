from backend.app.utils.name_manager import NameManager
from backend.app.error import PieceNotFoundException
from backend.app.utils.name_manager import NameManager

#Class that represents a piece
#raise PathNotFoundException if the path doesn't exits unless is None
class Piece:
    def __init__(self,cod:int,name:str,parsed_name:str|None=None,digitalized:bool=False):
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
        cod = int(NameManager.get_cod(std_name))
        name = NameManager.get_name(std_name)
        return cls(cod,name,std_name,digitalized)
    
    
    def update_parsed_name(self) -> str:
        return NameManager.get_std_name(self.cod,self.name)



#List of pieces
class Pieces_list:
    pieces:list[Piece]
    def __init__(self):
        self.pieces = []
    #Refactor to use Piece objects not a list of Dirs
    #parsed names is a list of cod-name, ej: 18-PETRER
    def update_pieces_with_parsed_names(self,names:list):
        for i in names:
            self.pieces.append(Piece.from_parsed_name(i[0]))
    
    #Get a list of tuples with (cod:int,name:str,digitalized:bool)
    def update_pieces(self,cod_names:list[tuple[int|str,str,bool]]):
        self.pieces.clear()
        for i in cod_names:
            self.add(int(i[0]),i[1],digitalized=bool(i[2]))

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


    def remove(self,cod:int) -> bool:
        """Raise ValueError if Piece doesn't exists"""
        for i in self.pieces:
            if i.cod == cod:
                self.pieces.remove(i)
                return True
        return False
    
    #Raise ValueError if Piece doesn't exists
    def remove_parsed(self,parsed_name:str) -> bool:
        """
        Remove a piece by its parsed name (cod-name)
        Raise ValueError if Piece doesn't exists
        """
        return self.remove(int(NameManager.get_cod(parsed_name)))
    
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
    
    def exists_cod(self,cod:int) -> bool:
        """
        Check if a piece with the given code exists.

        :param cod int: The code to look for.
        :return bool: True if a piece with the specified code is found, False otherwise.
        """

        for i in self.pieces:
            if i.cod == cod:
                return True
        return False

    def exists_parsed(self,parsed_name:str) -> bool:
        """
        Check if a piece with the given parsed name exists in the collection.
        
        :param parsed_name str: The parsed identifier to search for.
        :return bool: True if a piece with the specified parsed name is found, else False.
        """
        
        for i in self.pieces:
            if i.parsed_name == parsed_name:
                return True
        return False