import sys, rarfile, os, io, shutil
from typing import Generator
from backend.app.massive_import.file_decompressor.strategies.base_extractor import BaseExtractor

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
        bundle_path = os.path.join(sys._MEIPASS, exe_name) #type: ignore
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


class RarExtractor(BaseExtractor):
    def extract_items(self, file_data: io.BytesIO) -> Generator[tuple[str, bytes], None, None]:
        """
        Extracts files from a RAR archive provided as an in-memory file object.
        It yields tuples of (base_filename, file_bytes) for each file in the archive,
        ignoring directories and preserving only the base filename.
        """
        with rarfile.RarFile(file_data, 'r') as archive:
            for info in archive.infolist():
                if isinstance(info, rarfile.RarInfo) and not info.isdir():
                    base_name = os.path.basename(info.filename or "")
                    if base_name:
                        yield base_name, archive.read(info)
    

    def extract_all(self, file_data: io.BytesIO) -> dict[str, bytes]:
        """
        Extracts all files from a RAR preserving the directory structure. 
        It returns a dictionary mapping the full path (including directories) to the file bytes.
        """
        extracted_files = {}
        with rarfile.RarFile(file_data, 'r') as archive:
            for info in archive.infolist():
                if isinstance(info, rarfile.RarInfo) and not info.isdir():
                    extracted_files[info.filename] = archive.read(info)
        return extracted_files