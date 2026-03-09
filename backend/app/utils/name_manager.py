import re
from backend.app.constants.constants import HYPHEN
from unidecode import unidecode

class NameManager:
    """This class manages the names of files"""


    @staticmethod
    def get_cod(std_name:str) -> str:
        """
        Get the cod from the std name.
        The cod is the first part of the std name before the first hyphen.
        """
        return re.sub(r'-.*$', '', std_name)
    
    @staticmethod
    def get_name(std_name:str) -> str:
        """
        Extract the name from the std name.
        The name is the part of the std name after the hyphen.
        """
        return re.sub(r'^\d+-','',std_name)
    
    @staticmethod
    def get_std_name(cod:str|int,name:str) -> str:
        """Return the standard name in the format "cod-name" in capital letters and without accents."""
        return str(cod)+HYPHEN+unidecode(str(name)).upper() 
    
    