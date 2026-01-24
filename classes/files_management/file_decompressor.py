import zipfile,os, rarfile, sys, shutil
from pathlib import Path
from classes.loggers.default_logger import DefaultLogger

def get_unrar_path() -> str | None:
    """
    Locates the UnRAR executable.
    Returns the absolute path as a string, or None if not found.
    """
    # 1. Priority: Check Environment Variable (User Override)
    # If the user explicitly set this, trust them and return it.
    env_path = os.environ.get("UNRAR_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    exe_name = "UnRAR.exe" if sys.platform.startswith("win") else "unrar"

    # 2. Priority: PyInstaller / Frozen Bundle
    # If wrapped in an exe, check the temporary extraction folder.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_path = os.path.join(sys._MEIPASS, exe_name)
        if os.path.exists(bundle_path):
            return bundle_path

    # 3. Priority: System PATH (The standard way)
    # This works for Linux/macOS and correctly configured Windows.
    path_from_shutil = shutil.which(exe_name)
    if path_from_shutil:
        return path_from_shutil

    # 4. Priority: Common Windows Installation Paths (Fallback)
    if sys.platform.startswith("win"):
        # Check standard 64-bit and 32-bit WinRAR folders
        common_paths = [
            os.path.join(os.environ.get("ProgramFiles", r"C:\\Program Files"), "WinRAR", exe_name),
            os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)"), "WinRAR", exe_name),
            # Keep your original guess just in case
            r"C:\\Program Files\\Unrar\\UnRAR.exe", 
        ]
        
        for candidate in common_paths:
            if os.path.exists(candidate):
                return candidate

    # 5. Not found
    return None

rarfile.UNRAR_TOOL = get_unrar_path()

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
    

    def decompress_zip_without_folders(self,zip_path:str, out_dir_path:str) -> list[str]:
        """
        Extract all the files without the folder structure inside a zip. Only the files.
        Ignore also junk files like .DS_Store.
        """
        files_extracted:list[str] = []
        out_dir = Path(out_dir_path)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, "r") as z:
            self.logger.info("Extracting zip without folders %s...",zip_path)

            for member in z.infolist():
                if not member.is_dir():  # skip directories
                    # Get only the filename (ignore folders inside the zip)
                    filename = Path(member.filename).name
                    if filename:  # avoid empty names
                        filename = self.get_unique_filename(out_dir.absolute(), filename)
                        target_path = out_dir / filename

                        with z.open(member) as source, target_path.open("wb") as target:
                            target.write(source.read())
                            files_extracted.append(target_path.absolute())
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