import os,shutil,hashlib
from backend.app.constants.constants import DIR_SCORES,DIR_EXTRAS, HYPHEN
import unicodedata
from pathlib import Path

#This class make all the interactions with the files on the archive path
class ArchiveFileManager:
    def __init__(self, archive_path:str):
        self.archive_path = archive_path

    @staticmethod
    def is_pdf(path:str):
        extension = os.path.splitext(path)[1].lower() #Extract the extension
        if ".pdf" == extension:
            return True
        return False
    
    @staticmethod
    def parse_name_to_file_manager(parsed_name: str) -> str:
        r"""
        Normalize and sanitize a file name string for safe use in the file manager.

        This function removes diacritical marks from the given name, converts it to
        uppercase, and remove characters that are typically invalid in file names:
        There are removed this chars: `\`, `/`, `<`, `>`, `|`, `:`, `*`, `?`, `"` 

        Args:
            parsed_name (str): The original file name to normalize and sanitize.

        Returns:
            str: The sanitized, uppercase file name suitable for the file manager.
        """
        normalized = unicodedata.normalize("NFD", parsed_name)
        no_accents = normalized.encode("ascii", "ignore").decode("ascii")
        uppercased = no_accents.upper()
        if "-" in uppercased:
            number, rest = uppercased.split("-", 1)
            uppercased = f"{number.strip()}{HYPHEN}{rest.strip()}"

        return (
            uppercased.replace("\\", "")
            .replace("/", "")
            .replace(":", "")
            .replace("*", "")
            .replace("?", "")
            .replace('"', "")
            .replace("<", "")
            .replace(">", "")
            .replace("|", "")
        )
    
    @staticmethod
    def extract_original_filename(file_path: str) -> str:
        """Extracts the original filename from a temporarily uploaded file, removing the UUID prefix if it exists."""
        return os.path.basename(file_path).split("_", 1)[-1]
        
    @staticmethod
    def format_temp_filename(file_uuid: str, filename: str) -> str:
        """Formats a filename with a UUID prefix for temporary storage."""
        return f"{file_uuid}_{os.path.basename(filename)}"
    
    def add_file_to_piece(self, piece_path: str, source_file_bytes: bytes, filename: str, check_duplicates: bool = True) -> bool:
        """
        Copy a file to the internal archive depending on if it is a score or an extra
        and remove the temporally prefix of the name of the file.
            :param piece_path: name of the piece in the internal archive (without the relative archive path, only the name)
            :param source_file_bytes: bytes of the file to be copied
            :param filename: original filename (with extension) to determine if it's a score or extra
            :param check_duplicates: whether to check for duplicate files in the destination folder
        Returns:
            - True if the files was copied successfully or if a duplicate identical file already exists (when check_duplicates is True)
            - False if there was an error copying the file.
        """
        folder = DIR_SCORES if self.is_pdf(filename) else DIR_EXTRAS    
        destination_path = os.path.join(self.archive_path, piece_path, folder, filename)
        
        if check_duplicates:
            if os.path.exists(destination_path):
                for existing_file in os.listdir(os.path.dirname(destination_path)):
                        existing_file_path = os.path.join(os.path.dirname(destination_path), existing_file)
                        if self.are_the_same(source_file_bytes, existing_file_path):
                            print(f"File {filename} already exists in the destination and is identical. Skipping copy.")
                            return True
        try:
            with open(destination_path, "wb") as dest_file:
                dest_file.write(source_file_bytes)
            return True
        except Exception as e:
            print(f"Error copying file {filename} to archive: {type(e)}:{e}")
            return False
        

    def copy_files_in_archive(self,piece_path:str,files:list) -> bool:
        """
        Copy the files to the internal archive deppending if they are scores or extras
        and remove the temporarily prefix of the name of the files.
        If an error is produced, nothing is copied and it returns false.
            :param piece_path: name of the piece in the internal archive (without the relative archive path, only the name)
            :param files: list of strs with the absolute path of each file
        """
        copied_files = []
        try:
            for i in files:
                folder = DIR_SCORES if self.is_pdf(i) else DIR_EXTRAS    
                filename = self.extract_original_filename(i)
                path = os.path.join(self.archive_path,piece_path,folder,filename)
                shutil.copy(i,path)
                copied_files.append(i)

            return True
        
        except Exception as e:
            print(f"{type(e)}:{e}")
            for f in copied_files:
                try:
                    os.remove(os.path.join(self.archive_path,piece_path,DIR_SCORES,os.path.basename(f)))
                except Exception as e:
                    print(f"Error removing copied file {f} from Scores: {type(e)}:{e}")
                try:
                    os.remove(os.path.join(self.archive_path,piece_path,DIR_EXTRAS,os.path.basename(f)))
                except Exception as e:
                    print(f"Error removing copied file {f} from Extras: {type(e)}:{e}")
        
        return False
    
    
    def move_files(self,path:str,new_path:str) -> str:
        """
        Move a file, files of folder from path to new_path
        Returns the new path if the file was moved successfully
        If the file is already in the new path, it returns the same path
        If the file couldn't be moved, it returns an empty string
        """
        try:
            shutil.move(path,os.path.join(os.path.dirname(path),new_path))
            return os.path.join(os.path.dirname(path),new_path)
        
        except Exception as e:
            if path == os.path.join(os.path.dirname(path),new_path): # if the name is the same
                return path
        
        return ""


    
    def _get_file_names(self,path:str) -> list[str]:
        """
        Get the names of the files inside a path avoiding .DS_Store.
        If the path doesn't exist or doesn't have anything inside it returns an empty list
        """
        try:
            list = os.listdir(path)
            return [i for i in list if i != ".DS_Store"]
        except FileNotFoundError:
            return []
        
    
    
    def get_scores(self,piece_std_name:str) -> list[str]:
        """
        Get the path of the piece without the Scores dir extension  
        and return the list of scores inside it
        """
        piece_name = self.parse_name_to_file_manager(piece_std_name)
        return self._get_file_names(os.path.join(self.archive_path,piece_name,DIR_SCORES))


    #If the piece doesn't exist or doesn't have any exta it returns an empty list
    
    def get_extras(self,piece_std_name:str) -> list[str]:
        """
        Get the path of the piece without the Extras dir extension
        and return the list of extras inside it
        """
        piece_name = self.parse_name_to_file_manager(piece_std_name)
        return self._get_file_names(os.path.join(self.archive_path,piece_name,DIR_EXTRAS))


    
    def make_dir(self,name):
        """Create a dir for a piece in the archive path. Create the scores and extras folders inside it."""
        folder_name = self.parse_name_to_file_manager(name)
        piece_path = os.path.join(self.archive_path,folder_name)

        try:
            os.makedirs(os.path.join(piece_path,DIR_SCORES),exist_ok=True) #Create partituras
        except Exception as e:
            print(e, type(e))

        try:
            os.makedirs(os.path.join(piece_path,DIR_EXTRAS),exist_ok=True) #Create extras
        except Exception as e:
            print(e, type(e))


    #delete a piece. Recive the stadard name-> num-name ej: 1-HOLA 
    def delete_piece(self,parsed_piece_name:str):
        shutil.rmtree(os.path.join(self.archive_path,parsed_piece_name)) #Delete files


    #Change the name of a directory depending on the cod
    def change_piece_dir_name(self,old_name:str,new_name:str):
        os.rename(os.path.join(self.archive_path,old_name),os.path.join(self.archive_path,new_name))

    
    def get_piece_path(self,cod:str) -> str:
        """
        Get the piece path in the archive directory using only the cod (it only checks cod- the name is not checked)
        If the piece doesn't exist it returns an empty string
        """
        for i in os.listdir(self.archive_path):
            if i.startswith(str(cod) + "-"):
                return os.path.join(self.archive_path,i)
        return ""
    
    
    def _md5_hash(self,file_path:str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


    def _md5_hash_bytes(self,file_bytes:bytes) -> str:
        hash_md5 = hashlib.md5()
        hash_md5.update(file_bytes)
        return hash_md5.hexdigest()


    def are_the_same(self,path1:str|bytes,path2:str|bytes) -> bool:
        """
        Check if two files are the sameones using md5
        Params:
            - path1: path of the first file or bytes of the first file
            - path2: path of the second file or bytes of the second file
        Returns:
            - True if the files are the same, False otherwise
        """
        if isinstance(path1, str):
            hash1 = self._md5_hash(path1)
        else:
            hash1 = self._md5_hash_bytes(path1)

        if isinstance(path2, str):
            hash2 = self._md5_hash(path2)
        else:
            hash2 = self._md5_hash_bytes(path2)

        return hash1 == hash2


    def sanitize_archive_folder_names(self):
        """
        Rename archive folders replacing forbidden characters using parse_name_to_file_manager.
        """
        for folder in os.listdir(self.archive_path):
            parsed_name = self.parse_name_to_file_manager(folder)
            if folder != parsed_name:
                os.rename(os.path.join(self.archive_path, folder),
                          os.path.join(self.archive_path, parsed_name))
                print(f"Renamed folder {folder} to {parsed_name} in archive.")

    
    def move_uppercase_pdfs_to_scores(self):
        """
        Iterate over the archive and move files ending with .PDF from Extras to Scores.
        """
        base_path = Path(self.archive_path)
        for pdf_file in base_path.rglob("*.PDF"):
            if pdf_file.parent.name != DIR_EXTRAS:
                continue
            destination = pdf_file.parent.parent / DIR_SCORES / pdf_file.with_suffix(".pdf").name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(pdf_file), str(destination))
            print(f"Moved {pdf_file} to {destination}.")
    
    
    def path_exists(self,path:str) -> bool:
        """Check if a path exists in the system"""
        return os.path.exists(path)