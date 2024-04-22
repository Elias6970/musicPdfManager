import os
from unidecode import unidecode
from classes.constants import RELATIVE_ARCHIVE_PATH
from classes.error import PathNotFoundException

#Class that represents a piece
#raise PathNotFoundException if the path doesn't exits unless is None
class Piece:
    def __init__(self,cod:int,name:str,parsed_name=None):
        self.cod = cod
        self.name = name
        
        if parsed_name == None:
            self.parsed_name = self.update_parsed_name()   
        else:
            self.parsed_name = parsed_name 
        

    #Constructor overload that gets the parsed name
    @classmethod
    def from_parsed_name(cls,std_name:str,path=None):
        cod = Piece.extract_cod(std_name)
        name = Piece.extract_name(std_name)
        return cls(cod,name,std_name)
    
    
    def update_parsed_name(self) -> str:
        return str(self.cod) + "-" + unidecode(self.name).upper()
    
    #No se puede \ / : * ? " < > |
    def get_path(self) -> str:
        return self.parsed_name.replace('"',"'")

    
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

#List of pieces
class Pieces_list:
    pieces:list[Piece] = []
    def __init__(self):
        pass
    #Refactor to use Piece objects not a list of Dirs
    #parsed names is a list of cod-name, ej: 18-PETRER
    def update_pieces_parsed_names(self,names:list):
        for i in names:
            i = i[0]
            try:
                self.pieces.append(Piece.from_parsed_name(i,os.path.join(RELATIVE_ARCHIVE_PATH(),i)))
            except PathNotFoundException:
                self.pieces.append(Piece.from_parsed_name(i))      
    
    def update_pieces(self,cod_names:list[tuple[int,str]]):
        for i in cod_names:
            self.add(i[0],i[1])

    #Return a list with digitalized pieces
    def get_digitalized(self):
        digitalized:list = []
        for i in self.pieces:
            if(i.get_path() != None):
                digitalized.append(i)
        
        return digitalized
    
    #raise PathNotFoundException if the path doesn't exits unless is None
    def add(self,cod:int,name:str,parsed_name=None):
        self.pieces.append(Piece(cod,name,parsed_name))
        return True

    #raise PathNotFoundException if the path doesn't exits unless is None      
    def add_parsed(self,parsed_name,path=None):
        self.pieces.append(Piece.from_parsed_name(parsed_name,path))
        return True

    #Raise ValueError if Piece doesn't exists
    def remove(self,cod:int,name:str,parsed_name=None):
        self.pieces.remove(Piece(cod,name,parsed_name))
        return True
    
    #Raise ValueError if Piece doesn't exists
    def remove_parsed(self,parsed_name,path=None):
        self.pieces.remove(Piece.from_parsed_name(parsed_name,path))
        return True