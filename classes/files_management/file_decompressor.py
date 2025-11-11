import zipfile,os, rarfile
from pathlib import Path
from classes.loggers.default_logger import DefaultLogger

rarfile.UNRAR_TOOL = r"C:\\Program Files\\unrar\\UnRAR.exe"

class FileDecompressor:
    logger:DefaultLogger
    def __init__(self,logger:DefaultLogger|None=None):
        if logger:
            self.logger = logger

    def get_unique_filename(self, out_dir:str, filename:str) -> str:
        """
        Return a unique filename if there is another file with the same name.
            :param out_dir: path to find if there are more files with the same filename.
            :param filename: name of the file without the path
            :return: return the unique filename
        """
        if not os.path.exists(os.path.join(out_dir, filename)):
            return filename
        
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(out_dir, f"{base}_{counter}{ext}")):
            counter += 1

        return f"{base}_{counter}{ext}"
    
    
    def decompress_zip_without_folders(self,zip_path:str, out_dir:str) -> list[str]:
        """
        Extract all the files without the folder structure inside a zip. Only the files.
        Ignore also junk files like .DS_Store.
        """
        files_extracted:list[str] = []

        with zipfile.ZipFile(zip_path, "r") as z:
            self.logger.info("Extracting zip without folder %s...",zip_path)

            for member in z.infolist():
                if not member.is_dir():  # skip directories
                    # Get only the filename (ignore folders inside the zip)
                    filename = os.path.basename(member.filename)
                    if filename:  # avoid empty names
                        filename = self.get_unique_filename(out_dir, filename)
                        target_path = os.path.join(out_dir, filename)
                        if not os.path.exists(out_dir):
                            os.makedirs(out_dir)

                        with z.open(member) as source, open(target_path, "wb") as target:
                            target.write(source.read())
                            files_extracted.append(target_path)
                            self.logger.info("Extracted %s into %s", filename, target_path)
       
        return files_extracted


    def decompress_rar_without_folders(self,rar_path:str, out_dir_path:str) -> list[str]:
        """
        Extract all the files without the folder structure inside a rar. Only the files.
        Ignore also junk files like .DS_Store.
        """
        files_extracted: list[str] = []
        out_dir = Path(out_dir_path)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Open the RAR archive
        with rarfile.RarFile(rar_path, "r") as rf:
            self.logger.info("Extracting rar without folders %s...", rar_path)

            for member in rf.infolist():
                if isinstance(member, rarfile.RarInfo) and not member.is_dir():  # skip directories
                    # Get only the filename (ignore folders inside the RAR)
                    filename = Path(member.filename).name
                    if filename:  # avoid empty names
                        # Ensure unique filename in the output directory
                        filename = self.get_unique_filename(out_dir.absolute(), filename)
                        target_path = out_dir / filename


                        # Extract the file
                        with rf.open(member) as source, target_path.open("wb") as target:
                            target.write(source.read())
                            files_extracted.append(target_path.absolute())
                            self.logger.info("Extracted %s into %s", filename, target_path)

        return files_extracted