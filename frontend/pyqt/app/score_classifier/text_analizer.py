import os,re
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.instruments_names_api_client import InstrumentsNamesApiClient

class TextAnalizer():
    """
    Class that translate from a shortcut or an instrument name to the internal name of the instrument. Also can extract the number of the instrument if it is in the input. For example, "Flute2" will be translated to "flute_2" and "Flute" will be translated to "flute". If the input is not a shortcut or an instrument name, it will return the input with spaces replaced by underscores and in lowercase. For example, "Bass Clarinet" will be translated to "bass_clarinet". If the input is empty, it will return an empty string.
    """
    def __init__(self) -> None:
        self.instruments = {}
        self.instruments_pattern = ""
        self.instruments_names_api_client = InstrumentsNamesApiClient(get_base_client())
        self.instruments_names_api_client.get_shortcuts_and_instruments_success.connect(self._on_get_instruments)
        self.instruments_names_api_client.get_shortcuts_and_instruments_error.connect(lambda error: print(f"Failed to load instruments: {error}"))

        self.get_instruments()

    def get_instruments(self):
        """
        Get the instruments and shortcuts from the API and update the internal state of the class.
        """
        self.instruments_names_api_client.get_shortcuts_and_instruments()

    def _on_get_instruments(self, instruments:dict):
        """Update the internal instruments and shortcuts dict received from the API."""
        self.instruments = instruments
        self.instruments_pattern = '|'.join(map(re.escape, list(instruments.keys())))


    def parse_input(self, text:str) -> tuple[str,str|None]:
        """
        Parse the input text and return a tuple with the instrument and the number (if any). The method checks if the input matches any of the following patterns:
        1. A valid instrument shortcut (case insensitive), e.g., "f", "o".
        2. A valid instrument shortcut with a number at the end, e.g., "f2", "o3".
        3. A string containing only letters, spaces, or underscores, e.g., "Bass Clarinet", "bass_clarinet".
        4. A string containing letters followed by a number, e.g., "Bass Clarinet2", "bass_clarinet2".
        5. An empty string.

        Returns:
            tuple[str, str|None]: A tuple where the first element is the instrument name (or shortcut) and the second element is the number if it exists, otherwise None.
        Raises:
            ValueError: If the input text does not match any of the expected patterns, indicating that it contains invalid characters or format.
        """
        if re.fullmatch(fr'^(?:{self.instruments_pattern})$', text, re.IGNORECASE):
            return (text,None)
        
        elif re.fullmatch(fr'^(?:{self.instruments_pattern})\d$', text, re.IGNORECASE):
            input = re.split(r"(\d+)",text)
            return (str(input[0]),str(input[1]))

        elif re.fullmatch(r"[a-zA-Z _]+$",text,re.IGNORECASE):
            return (text,None)
        
        elif re.fullmatch(r'^[a-zA-Z _]+\d+$',text,re.IGNORECASE):
            input = re.split(r"(\d+)",text)
            return (str(input[0]),str(input[1]))

        elif text == "":
            return ("",None)
        else:
            raise ValueError("Only permited letters and numbers")


    def analyze(self, text:str):
        """
        Analyze the input text and return the corresponding internal instrument name with the number if applicable. 
        Args:
            text (str): The input text to be analyzed, which can be a shortcut, an instrument name, or a combination of both with an optional number at the end.
        Returns:
            str: The internal name of the instrument corresponding to the input text, formatted with underscores and lowercase, and including the number if it was present in the input.
        Raises:
            ValueError: If the input text does not match any of the expected patterns.
        """
        instrument,num = self.parse_input(text)

        num = "" if num == None else "_"+num
        try:
            return self.instruments[instrument]+num
        except KeyError as e:
            return instrument.replace(' ','_').lower()+num
        
    
    #Return a list with the internal names of the instruments
    def get_internal_names(self, names:list[str]):
        internal_names:list[str] = []
        for i in names:
            #Quit .pdf
            i = os.path.splitext(i)[0]
            
            try:
                internal_names.append(i.split("_")[0]+i.split("_")[1])
            except IndexError:
                internal_names.append(i.split("_")[0])
            
        return internal_names