import json, os
from backend.app.constants.constants import INSTRUMENTS_PATH
from backend.app.config import Configuration, LAN_ENG, LAN_ESP, LAN_VAL

class InstrumentsNamesManager:
    """
    A class to manage instruments names, translations and shortcuts.
    Standard names are used for internal processing, naming files, etc.
    Translations are used for displaying names in the user interface.
    The json file has a structure like this:
    {
        "instrument_name": {
            "translations": {
                "es_ES": "Instrument Name",
                "en_US": "Nombre del Instrumento",
                "ca_VA": "Nom de l'Instrument"
            },
            "classifier_hotkey": "i"
        },
        ...
    }
    """

    TRANSLATIONS = "translations"
    HOTKEYS = "classifier_hotkey"

    def __init__(self):
        pass

    @staticmethod
    def get_shortcuts_and_instruments() -> dict[str,str]:
        """
        Returns a dictionary with all the shortcuts as keys and standard names as values.
        Throws FileNotFoundError if the instruments file does not exist,
        and JSONDecodeError if the file is malformed.
        
        """
        try:
            with open(INSTRUMENTS_PATH(), 'r', encoding='utf-8') as file:
                language = Configuration.name_to_cod_language(Configuration.get_language())
                instruments = json.load(file)

                return {instruments[i][InstrumentsNamesManager.HOTKEYS]: i for i in instruments}
            
        except FileNotFoundError:
            print(f"Error: The file {INSTRUMENTS_PATH()} does not exist.")
            return {}
        except json.JSONDecodeError:
            print("Error: The JSON file is malformed.")
            return {}

    @staticmethod
    def get_instruments_and_shortcuts() -> dict[str,str]:
        """
        Returns a dict with the instrument standard name as key and its shortcut as value.
        Throws FileNotFoundError if the instruments file does not exist,
        and JSONDecodeError if the file is malformed.
        
        """
        try:
            with open(INSTRUMENTS_PATH(), 'r', encoding='utf-8') as file:
                language = Configuration.name_to_cod_language(Configuration.get_language())
                instruments = json.load(file)

                return {i : instruments[i][InstrumentsNamesManager.HOTKEYS] for i in instruments}
            
        except FileNotFoundError:
            print(f"Error: The file {INSTRUMENTS_PATH()} does not exist.")
            return []
        except json.JSONDecodeError:
            print("Error: The JSON file is malformed.")
            return []
    
    @staticmethod
    def get_instruments_and_shortcuts_translated() -> list[tuple[str,str]]:
        """
        Returns a list of tuples with the instrument name translated (not standard) and its shortcut.
        Throws FileNotFoundError if the instruments file does not exist,
        and JSONDecodeError if the file is malformed.
        
        """
        try:
            with open(INSTRUMENTS_PATH(), 'r', encoding='utf-8') as file:
                language = Configuration.name_to_cod_language(Configuration.get_language())
                instruments = json.load(file)

                return [(instruments[i][InstrumentsNamesManager.TRANSLATIONS][language], instruments[i][InstrumentsNamesManager.HOTKEYS]) for i in instruments]
            
        except FileNotFoundError:
            print(f"Error: The file {INSTRUMENTS_PATH()} does not exist.")
            return []
        except json.JSONDecodeError:
            print("Error: The JSON file is malformed.")
            return []
        
    @staticmethod
    def get_instruments() -> list[str]:
        """
        Returns a list with all the instrument standard names.
        Throws FileNotFoundError if the instruments file does not exist,
        and JSONDecodeError if the file is malformed.
        
        """
        try:
            with open(INSTRUMENTS_PATH(), 'r', encoding='utf-8') as file:
                instruments = json.load(file)

                return [i for i in instruments]
            
        except FileNotFoundError:
            print(f"Error: The file {INSTRUMENTS_PATH()} does not exist.")
            return []
        except json.JSONDecodeError:
            print("Error: The JSON file is malformed.")
            return []
        


    @staticmethod
    def get_instruments_and_shortcuts_as_str() -> str:
        """
        Returns a string with the instrument name translations and its shortcut.
        Throws FileNotFoundError if the instruments file does not exist,
        and JSONDecodeError if the file is malformed.
        
        """
        instruments = InstrumentsNamesManager.get_instruments_and_shortcuts_translated()
        return "\n".join([f"{name} -> {shortcut}" for name, shortcut in instruments])