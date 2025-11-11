from classes.files_management.archive_file_manager import ArchiveFileManager
from classes.files_management.file_decompressor import FileDecompressor
from classes.constants.constants import RELATIVE_ARCHIVE_PATH
from classes.loggers.massive_importer_logger import MassiveImporterLogger
import os, shutil, zipfile, rarfile, tarfile, tempfile
from pathlib import Path

class MassiveImporter:
    """Class that imports a lot of pieces to the archive"""
    def __init__(self):
        self.logger = MassiveImporterLogger()
        self.fd = FileDecompressor(MassiveImporterLogger())



    def __import(self, piece_parsed_name:str, files:list[str]) -> bool:
        """
        Import a piece into the archive (only the files, not db)
        :param piece_parsed_name: std name of the piece (not path)
        :param files: absolut path of each file to copy
        """
        ArchiveFileManager.make_dir(RELATIVE_ARCHIVE_PATH(),piece_parsed_name)
        are_moved = ArchiveFileManager.move_files(piece_parsed_name,files)

        return are_moved

    

    def import_only__into_archive(self, pieces_to_import:str, overwrite=False, use_db_name=True):
        """
        Imports only the pieces to the archive (RELATIVE_ARCHIVE_PATH()) without registering them in the db.
        Use only if the pieces are already in the db.
        
        :param pieces_to_import: absolut path to the folder where pieces to import are. 
            At this folder, each folder inside is consider as a piece. The name of the folders need to be in a standard way (cod-name).
            All the folders inside a piece are ignored and only the files are imported. Also junk files like .DS_Store aren't imported
        :param overwrite: overwrite the pieces that already exist in the archieve
        :param use_db_name: If it is true it search the id of the piece in the db and uses that name (if it doesn't exist it takes the folder's name). If not, the folder's name is used. 
        """
    
        for dir_path in Path(pieces_to_import).iterdir():
            if not dir_path.is_dir():
                continue

            temp_dir = Path(tempfile.gettempdir()) / os.urandom(24).hex()
            temp_dir.mkdir(parents=True, exist_ok=True)
            files_to_import:list[str] = []

            # Iterate over the 
            for i in dir_path.rglob("*"):
                if i.is_file():

                    if not i.suffix.lower() in [".rar", ".zip", ".tar.gz", ".tar", ".7z"]:
                        files_to_import.append(i)
                        continue
                    
                    #Compressed files
                    if i.suffix.lower() == ".zip" and zipfile.is_zipfile(i):
                        extracted = self.fd.decompress_zip_without_folders(i,temp_dir)
                        files_to_import.extend(extracted)

                    elif i.suffix.lower() == ".rar" and rarfile.is_rarfile(i):
                        extracted = self.fd.decompress_rar_without_folders(i,temp_dir)
                        files_to_import.extend(extracted)

                    elif i.suffix.lower() == ".tar.gz":
                        self.logger.error(".tar.gz decompression not implemented yet, ignoring file %s",i.absolute())
                    elif i.suffix.lower() == ".tar":
                        self.logger.error(".tar decompression not implemented yet, ignoring file %s",i.absolute())
                    elif i.suffix.lower() == ".7z":
                        self.logger.error(".7z decompression not implemented yet, ignoring file %s",i.absolute())

            #Iter the temp_dir to find compresed files
            #If found, extract files and delete the compressed file
            compressed = [f for f in temp_dir.iterdir() if f.is_file() and f.suffix.lower() in (".zip", ".rar",".tar.gz",".tar",".7z")]
            while compressed != []:
                for i in compressed:
                    pass
                
                
                compressed = [f for f in temp_dir.iterdir() if f.is_file() and f.suffix.lower() in (".zip", ".rar",".tar.gz",".tar",".7z")]


            #Copy all the files

            #Delete temp dir

            






