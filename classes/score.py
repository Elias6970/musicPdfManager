class Score:
    def __init__(self,cod,name=None,author=None,type=None,parts=None,create_date=None,last_modification=None):
        self.cod = cod
        self.name = name
        #self.path = str(cod)+"-"+name
        self.parts = parts
        self.type = type
        self.author = author
        self.create_date = create_date
        self.last_modification = last_modification
        
            
    @classmethod
    def get_from_db(cls,cod):
        pass

class Part:
    def __init__(self,type,path):
        self.type = type
        self.path = path
