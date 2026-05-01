import tarfile, os, io
from typing import Generator
from backend.app.massive_import.file_decompressor.strategies.base_extractor import BaseExtractor 

class TarExtractor(BaseExtractor):
    def extract_items(self, file_data: io.BytesIO) -> Generator[tuple[str, bytes], None, None]:
        """
        Extracts files from a TAR (gzip, bzip2, etc.) archive provided as an in-memory file object.
        It yields tuples of (base_filename, file_bytes) for each file in the archive,
        ignoring directories and preserving only the base filename.
        """
        # mode 'r:*' automatically handles raw tar, gzip, bzip2, etc.
        with tarfile.open(fileobj=file_data, mode='r:*') as archive:
            for member in archive.getmembers():
                if member.isreg(): # Check if it's a regular file
                    base_name = os.path.basename(member.name)
                    if base_name:
                        f = archive.extractfile(member)
                        if f:
                            yield base_name, f.read()