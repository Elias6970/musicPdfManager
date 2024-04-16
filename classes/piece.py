class Piece:
    def __init__(self,cod:int,name:str,path=None,parsed_name=None):
        self.cod = cod
        self.name = name
        self.path = path

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
