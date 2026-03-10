import os,re
from backend.app.utils.name_manager import NameManager
from backend.app.error import IncorrectCodOrNameError, CodAlreadyExistsError
from backend.app.files_management.archive_file_manager import ArchiveFileManager
from backend.app.db_manage import Db_archive
from backend.app.constants.constants import RELATIVE_ARCHIVE_PATH
from backend.app.piece import Pieces_list
from backend.app.files_management.massive_importer import MassiveImporter
#The connection with the db is started when the obj is created with the super.
class Archive:
    def __init__(self,db_name,archive_path):
        self.db = Db_archive(db_name)
        self.archive_path = archive_path
        self.pieces = Pieces_list()
        self.update_pieces()

    def add_piece(self,cod:int|str, name:str, author:str, type:str,  files:list[str], handwritten:bool, digitalized:bool, parted:bool):
        """
        Add a new musical piece to the archive by creating its directory, copying associated files,
        and inserting its metadata into the database.
        Args:
            cod (str): Unique identifier for the piece.
            name (str): Name of the piece.
            files (list[str]): List of file paths to associate with the piece.
            author (str): Name of the author or composer.
            type (str): Type or category of the piece.
            handwritten (bool): True if the piece is handwritten.
            digitalized (bool): True if the piece has been digitalized.
            parted (bool): True if the piece is parted.
        Returns:
            bool: True if the piece was successfully added to the archive and database; False otherwise.
        """

        parsed_name = NameManager.get_std_name(cod,name)
        folder_name = ArchiveFileManager.parse_name_to_file_manager(parsed_name)

        #Create the dir in the archive
        ArchiveFileManager.make_dir(folder_name)

        if files != []:
            #Copy the files to the archive
            are_moved = ArchiveFileManager.copy_files_in_archive(folder_name,files)
        else:
            are_moved = True

        if are_moved:
            try:
                is_inserted = self.db.insert(cod=int(cod),
                                            name=name,
                                            author=author,
                                            type=type,
                                            handwritten=int(handwritten),
                                            parted=int(parted),
                                            digitalized=int(digitalized))
            except (CodAlreadyExistsError,IncorrectCodOrNameError) as e:
                return False
            
            if is_inserted:
                self.pieces.add(int(cod),name,parsed_name,digitalized)
                self.update_pieces() #Update the list of pieces with the db
                
                return True
            
        return False

    def add_files_to_piece(self,parsed_name:str,files:list[str]) -> bool:
        """
        Add files to an existing piece in the archive.
        Args:
            parsed_name (str): Standardized name of the piece to which files will be added.
            files (list[str]): List of file paths or file objects to add to the piece.
        Returns:
            bool: True if files are added successfully; False otherwise.
        """
        folder_name = ArchiveFileManager.parse_name_to_file_manager(parsed_name)
        are_moved = ArchiveFileManager.copy_files_in_archive(folder_name,files)
        return are_moved

    def delete_piece(self,cod:int,std_name:str=""):
        """
        Remove a music piece from the manager by its code, deleting it from the internal list,
        the database, and attempting to remove the associated file.
        Args:
            cod (int): The unique identifier of the piece to delete.
        Raises:
            ValueError: If the code is not present in the internal collection.
        """
        
        self.pieces.remove(int(cod))
        self.db.delete_score(int(cod)) #Delete from db

        try:
            if std_name == "":
                std_name = NameManager.get_std_name(cod,self.db.get_with_equals("cod",str(cod),"cod,name")[0][1])
            folder_name = ArchiveFileManager.parse_name_to_file_manager(std_name)
            ArchiveFileManager.delete_piece(folder_name)
        except FileNotFoundError:
            pass


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
                self.db.cur.execute("UPDATE {} SET digitalized = 1 WHERE cod = {};".format(self.db.table_name,str(cod)))
                        
        self.db.con.commit()
