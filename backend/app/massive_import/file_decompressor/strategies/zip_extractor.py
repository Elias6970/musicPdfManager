

from typing import Generator
import zipfile, os, io
from backend.app.massive_import.file_decompressor.strategies.base_extractor import BaseExtractor

class ZipExtractor(BaseExtractor):
    def extract_items(self, file_data: io.BytesIO) -> Generator[tuple[str, bytes], None, None]:
        """
        Extracts files from a ZIP archive provided as an in-memory file object.
        It yields tuples of (base_filename, file_bytes) for each file in the archive, 
        ignoring directories and preserving only the base filename.
        """
        with zipfile.ZipFile(file_data, 'r') as archive:
            for info in archive.infolist():
                if not info.is_dir():
                    base_name = os.path.basename(info.filename)
                    if base_name:
                        with archive.open(info) as f:
                            yield base_name, f.read()
    

    def extract_all(self, file_data: io.BytesIO) -> dict[str, bytes]:
        """
        Extracts all files from a ZIP preserving the directory structure. 
        It returns a dictionary mapping the full path (including directories) to the file bytes.
        """
        extracted_files = {}
        with zipfile.ZipFile(file_data, 'r') as archive:
            for info in archive.infolist():
                if not info.is_dir():
                    with archive.open(info) as f:
                        extracted_files[info.filename] = f.read()
        return extracted_files