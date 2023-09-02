class Score:
    def __init__(self,cod:int,name=None,author=None,type=None,created_date=None,last_modification=None,handwritten=None,digitalized=None,parted=None):
        self.cod = cod
        self.name = name
        self.author = author
        self.type = type
        self.created_date = created_date
        self.last_modification = last_modification
        self.handwritten = handwritten
        self.digitalized = digitalized
        self.parted = parted