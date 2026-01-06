import os,re
from classes.utils.name_manager import NameManager
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
        self.update_pieces()
        

    #Update the list of pieces with the db
    def update_pieces(self):
        self.pieces.update_pieces(self.db.get_all_cod_name_digitalized())


    #Stablish the name to the folders get from the db to standarize the names
    #"cod-name" in capital leters and without accents
    def get_parsed_name_from_db(self,cod):
        name = self.db.get_with_equals("cod",cod,"cod,name")

        return NameManager.get_std_name(cod,name[0][1]) if name else None
    

    #Compare the names in the archive dir with the db and set digitalized to 1 if the dir exists    
    def add_digitalized_mark(self):
        names = os.listdir(RELATIVE_ARCHIVE_PATH())

        for i in names:
            if "DS_Store" not in i:
                cod = NameManager.get_cod(i)
                self.db.cur.execute("UPDATE {} SET digitalized = 1 WHERE cod = {};".format(DB_NAME,str(cod)))
                        
        self.db.con.commit()
