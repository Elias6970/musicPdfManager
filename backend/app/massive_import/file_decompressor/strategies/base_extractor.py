import abc,io
from typing import Generator

class BaseExtractor(abc.ABC):
    """
    Abstract base class for all archive extraction strategies.
    """
    @abc.abstractmethod
    def extract_items(self, file_data: io.BytesIO) -> Generator[tuple[str, bytes], None, None]:
        """
        Takes an in-memory file object and yields (base_filename, file_bytes).
        Must be implemented by all concrete subclasses.
        """
        pass