import os,unidecode
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
        #self.pieces.update_pieces(self.db.get_all_cod_name_digitalized())
        self.update_pieces()
        
    """
    #----------------RESULTS----------------
    #With 1603 pieces and 308 digitalized
    #Dir:  0.0008343287467956542
    #Piece:  0.011169951963424683
    #Set:  0.011861127614974976
    #Query:  0.00045802669525146485
    
    #------------------TESTS-----------------
        print("Dir: ",self.test(self.update_pieces_in_dirs))
        print("Piece: ",self.test(self.update_pieces))
        print("Set: ",self.test(self.update_pieces_set))
        print("Query: ",self.test(self.query))


    def test(self,func):
        b = 0
        for i in range(1000):
            r = time.time()
            func()   
            b = b + (time.time() - r)
        return b/1000
    
    def query(self):
        self.get_all_parsed_names()
    """

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

    """#Refactor to use Piece objects not a list of Dirs
    def update_pieces(self):
        self.pieces = []
        for i in self.db.get_all_parsed_names():
            i = i[0]
            if os.path.exists(os.path.join(self.archive_path,i)):
                self.pieces.append(Piece.from_parsed_name(i,os.path.join(self.archive_path,i)))
            else:
                self.pieces.append(Piece.from_parsed_name(i))
    """

    #Extract the cod giving parsed name(cod+name), ej(1591-ATMURAF)-->1591
    @staticmethod
    def extract_cod(name) -> int:
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
