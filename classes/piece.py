import os
from classes.constants import RELATIVE_ARCHIVE_PATH
from classes.error import PathNotFoundException

#Class that represents a piece
#raise PathNotFoundException if the path doesn't exits unless is None
class Piece:
    def __init__(self,cod:int,name:str,path=None,parsed_name=None):
        self.cod = cod
        self.name = name
        self.path = path

        if(path != None and not os.path.exists(path)):
            raise PathNotFoundException()
        
        if parsed_name == None:
            self.parsed_name = self.update_parsed_name()   
        else:
            self.parsed_name = parsed_name 
        

    #Constructor overload that gets the parsed name
    @classmethod
    def from_parsed_name(cls,std_name:str,path=None):
        cod = Piece.extract_cod(std_name)
        name = Piece.extract_name(std_name)
        return cls(cod,name,path,std_name)
    
    
    def update_parsed_name(self) -> str:
        return str(self.cod) + "-" + self.name
    
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
    def __init__(self,names:list|None) -> None:
        self.pieces:list[Piece] = []
        
        if(names != None):
            self.update_pieces(names)

    #Refactor to use Piece objects not a list of Dirs
    #parsed names is a list of cod-name, ej: 18-PETRER
    def update_pieces(self,names:list):
        for i in names:
            i = i[0]
            try:
                self.pieces.append(Piece.from_parsed_name(i,os.path.join(RELATIVE_ARCHIVE_PATH(),i)))
            except PathNotFoundException:
                self.pieces.append(Piece.from_parsed_name(i))      
    
    #Return a list with digitalized pieces
    def get_digitalized(self):
        digitalized:list = []
        for i in self.pieces:
            if(i.path != None):
                digitalized.append(i)
        
        return digitalized
    
    #raise PathNotFoundException if the path doesn't exits unless is None
    def add(self,cod:int,name:str,path = None,parsed_name=None):
        self.pieces.append(Piece(cod,name,path,parsed_name))
        return True

    #raise PathNotFoundException if the path doesn't exits unless is None      
    def add_parsed(self,parsed_name,path=None):
        self.pieces.append(Piece.from_parsed_name(parsed_name,path))
        return True

    #Raise ValueError if Piece doesn't exists
    def remove(self,cod:int,name:str,path = None,parsed_name=None):
        self.pieces.remove(Piece(cod,name,path,parsed_name))
        return True
    
    #Raise ValueError if Piece doesn't exists
    def remove_parsed(self,parsed_name,path=None):
        self.pieces.remove(Piece.from_parsed_name(parsed_name,path))
        return True