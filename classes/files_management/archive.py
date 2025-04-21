import os
from unidecode import unidecode
from classes.files_management.dir import Dir
from classes.db_manage import Db_archive
from classes.constants.constants import DB_NAME,HYPHEN,IGNORE_FILES,RELATIVE_ARCHIVE_PATH
from classes.piece import Pieces_list

#The connection with the db is started when the obj is created with the super.
class Archive:
    def __init__(self,db_name,archive_path):
        self.db = Db_archive(db_name)
        self.archive_path = archive_path
        self.pieces = Pieces_list()
        #List of dirs objects
        self.pieces_in_dirs:list[Dir] = []
        #Pieces List
        self.update_pieces()
        

    #Update the list of pieces with the db
    def update_pieces(self):
        self.pieces.update_pieces(self.db.get_all_cod_name_digitalized())

    #Get the files inside the archive dir    
    def update_pieces_in_dirs(self):
        self.pieces_in_dirs = [] #Reset the variable to avoid duplication
        for i in os.listdir(self.archive_path):
            for j in IGNORE_FILES:
                if i not in j: #Ignore the DS_Store 
                    self.pieces_in_dirs.append(Dir(os.path.join(self.archive_path,i),i))


    #Extract the cod giving parsed name(cod+name), ej(1591-ATMURAF)-->1591
    @staticmethod
    def extract_cod(name:str) -> int:
        one = name.split("-",1)[0]
        two = name.split(" ",1)[0]
        if len(one) < len(two):
            return one
        return two
    

    #Stablish the name to the folders get from the db to standarize the names
    #"cod-name" in capital leters and without accents
    def get_parsed_name_from_db(self,cod):
        name = self.db.get_with_equals("cod",cod,"cod,name")

        return str(name[0][0])+HYPHEN+unidecode(str(name[0][1])).upper()
    
    #Return the standard name in the dirs structure
    @staticmethod
    def get_parsed_name(cod,name):
        return str(cod)+HYPHEN+unidecode(str(name)).upper() 
    

    #Compare the names in the archive dir with the db and set digitalized to 1 if the dir exists    
    def add_digitalized_mark(self):
        names = os.listdir(RELATIVE_ARCHIVE_PATH())

        for i in names:
            if "DS_Store" not in i:
                cod = self.extract_cod(i)
                self.db.cur.execute("UPDATE {} SET digitalized = 1 WHERE cod = {};".format(DB_NAME,cod))
                        
        self.db.con.commit()
