from classes.files_management.archive_file_manager import ArchiveFileManager
from classes.files_management.file_decompressor import FileDecompressor
from classes.db_manage import Db_archive
from classes.constants.constants import RELATIVE_ARCHIVE_PATH
from classes.loggers.massive_importer_logger import MassiveImporterLogger
from classes.utils.name_manager import NameManager
import os, shutil, zipfile, rarfile, tarfile, tempfile
from pathlib import Path

class MassiveImporter:
    """Class that imports a lot of pieces to the archive"""
    def __init__(self,db:Db_archive):
        self.logger = MassiveImporterLogger()
        self.fd = FileDecompressor(MassiveImporterLogger())
        self.db = db

    
    def __manage_a_file(self,file:Path,temp_dir:Path) -> list[str]:
        """
        Decide how to import a single file. 
        If it is compressed file (rar,zip,tar.gz,tar,7z) 
        it tries to decompress it and add the temporally path where they have been decompressed to the list.
        If it is a junk file (.DS_Store, any file starting with ._, .Spotligth, etc) is ignored
        If it is a normal file it is added to the list and returned.
        
        :param file: the file that is going to be managed
        :param temp_dir: directory where the decompressed files are going to be placed
        :return: return a list with the file path to import
        """
        files_to_import:list[str] = []
        if file.is_file():
            self.logger.info("Importing file %s",file)

            if not file.suffix.lower() in [".rar", ".zip", ".tar.gz", ".tar", ".7z"]:
                files_to_import.append(file.absolute())
                return files_to_import
            
            #Compressed files
            if file.suffix.lower() == ".zip" and zipfile.is_zipfile(file):
                self.logger.info("Decompressing zip %s",file)
                extracted = self.fd.decompress_zip_without_folders(file,temp_dir)
                files_to_import.extend(extracted)

            elif file.suffix.lower() == ".rar" and rarfile.is_rarfile(file):
                self.logger.info("Decompressing rar %s",file)
                extracted = self.fd.decompress_rar_without_folders(file,temp_dir)
                files_to_import.extend(extracted)

            elif file.suffix.lower() == ".tar.gz":
                self.logger.error(".tar.gz decompression not implemented yet, ignoring file %s",file.absolute())
                files_to_import.append(file.absolute())
            elif file.suffix.lower() == ".tar":
                self.logger.error(".tar decompression not implemented yet, ignoring file %s",file.absolute())
                files_to_import.append(file.absolute())
            elif file.suffix.lower() == ".7z":
                self.logger.error(".7z decompression not implemented yet, ignoring file %s",file.absolute())
                files_to_import.append(file.absolute())

        return files_to_import


    def __delete_duplicated_elements(self, pieces_list:list[str]) -> list[str]:
        """
        Delete all duplicated files when importing. 
        
        :param pieces_list: Absolut path of pieces that are going to be imported
        :type pieces_list: list[str]
        :return: The list without any duplicated file
        :rtype: list[str]
        """
        for i,item in enumerate(pieces_list):
            for j in pieces_list[i+1:]: #TODO: Check if the expresion is the correct one
                if ArchiveFileManager.are_the_same(item,j):
                    pieces_list.remove(j)
                    return self.__delete_duplicated_elements(pieces_list)
        
        return pieces_list
    

    def import_only__into_archive(self, pieces_to_import:str, overwrite=False, use_db_name=True) -> list[str]:
        """
        Imports only the pieces to the archive (RELATIVE_ARCHIVE_PATH()) without registering them in the db.
        Use only if the pieces are already in the db.
        
        :param pieces_to_import: absolut path to the folder where pieces to import are. 
            At this folder, each folder inside is consider as a piece. The name of the folders need to be in a standard way (cod-name).
            All the folders inside a piece are ignored and only the files are imported. Also junk files like .DS_Store aren't imported
        :param overwrite: overwrite the pieces that already exist in the archive (NOT IMPLEMENTED)
        :param use_db_name: If it is true it search the id of the piece in the db and uses that name (if it doesn't exist it takes the folder's name). If not, the folder's name is used. 
        :return: List of imported pieces with the imported name
        """
        imported:list[str] = []
    
        for dir_path in Path(pieces_to_import).iterdir():
            self.logger.info("Importing %s...", dir_path)

            if not dir_path.is_dir():
                self.logger.info("%s is not a path", dir_path)
                continue
            
            temp_dir = Path(tempfile.gettempdir()) / os.urandom(24).hex()
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Creating temp dir in %s",temp_dir)

            files_to_import:list[str] = []

            # Iterate all the files over the dir
            for i in dir_path.rglob("*"):
                if i.is_file():
                    to_import = self.__manage_a_file(i,temp_dir)
                    files_to_import.extend(to_import)

            print("ORIGINAL NAMEESSSS",files_to_import)
            #Iter the temp_dir to find compresed files
            #If found, extract files and delete the compressed file
            compressed = [f for f in temp_dir.iterdir() if f.is_file() and f.suffix.lower() in (".zip", ".rar",".tar.gz",".tar",".7z")]
            did_it = [] # Files already decompressed
            while compressed != []:
                for i in compressed:
                    if i not in did_it:
                        to_import = self.__manage_a_file(i, temp_dir)
                        files_to_import.extend(to_import)
                        print("NAMEEEE:",i.resolve())
                        print("Actual files to import:",files_to_import)
                        files_to_import.remove(i.absolute())
                        did_it.append(i)
                        self.logger.info("File decompressed %s",i) 
                        print(f"DID IT: {did_it}") 
                
                compressed = [f for f in temp_dir.iterdir() if f.is_file() and f.suffix.lower() in (".zip", ".rar",".tar.gz",".tar",".7z") and f not in did_it]

            print("He salido del while")

            #Delete duplicated elements in the list with md5
            files_to_import = self.__delete_duplicated_elements(files_to_import)
            print(f"Files to import: {files_to_import}")


            self.logger.info("Exporting next files: %s",str(len(files_to_import)))
            list(map(lambda x: self.logger.info("Exporting %s",x),files_to_import))

            #Copy all the files
            self.logger.info("Coping the files")
            if use_db_name:
                self.logger.info("Using db name...")
                cod = NameManager.get_cod(dir_path.name)
                name = self.db.get_with_equals("cod",cod,"cod,name")
                std_name = NameManager.get_std_name(cod,name[0][1]) if name else None
                if std_name == None:
                    self.logger.error("use_db_name flag enabled but cod is not in the db for %s. Using this name",dir_path.name)
                    dir_name = dir_path.name
                else:
                    dir_name = std_name
            else:
                dir_name = dir_path.name
            
            ArchiveFileManager.make_dir(dir_name)
            self.logger.info("Dir created in the archive")
            are_imported = ArchiveFileManager.copy_files_in_archive(dir_name,files_to_import)

            if are_imported:
                self.logger.info("Files coppied correctly")
            else:
                self.logger.error("Error copying the files, somethig went wrong")


            #Delete temp dir with all the files
            self.logger.info("Removing temporally dir")
            #shutil.rmtree(temp_dir)


            imported.append(dir_path.name)

        
        return imported






