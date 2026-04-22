import json
from backend.app.settings import get_server_settings

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
            with open(get_server_settings().instruments_names_file, 'r', encoding='utf-8') as file:
                instruments = json.load(file)

                return {instruments[i][InstrumentsNamesManager.HOTKEYS]: i for i in instruments}
            
        except FileNotFoundError:
            print(f"Error: The file {get_server_settings().instruments_names_file} does not exist.")
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
            with open(get_server_settings().instruments_names_file, 'r', encoding='utf-8') as file:
                instruments = json.load(file)

                return {i : instruments[i][InstrumentsNamesManager.HOTKEYS] for i in instruments}
            
        except FileNotFoundError:
            print(f"Error: The file {get_server_settings().instruments_names_file} does not exist.")
            return {}
        except json.JSONDecodeError:
            print("Error: The JSON file is malformed.")
            return {}
    
    @staticmethod
    def get_instruments_and_shortcuts_translated(language_cod: str) -> list[tuple[str,str]]:
        """
        Returns a list of tuples with the instrument name translated (not standard) and its shortcut.

            :param language_cod: The language code to get the translation. It should be one of the following: "es_ES", "en_US", "ca_VA".
        Raises:
            FileNotFoundError: If the instruments file does not exist.
            JSONDecodeError: If the instruments file is malformed.
            KeyError: If the language code is not found in the translations.
        """
        try:
            with open(get_server_settings().instruments_names_file, 'r', encoding='utf-8') as file:
                instruments = json.load(file)

                return [(instruments[i][InstrumentsNamesManager.TRANSLATIONS][language_cod], instruments[i][InstrumentsNamesManager.HOTKEYS]) for i in instruments]
            
        except FileNotFoundError:
            print(f"Error: The file {get_server_settings().instruments_names_file} does not exist.")
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
            with open(get_server_settings().instruments_names_file, 'r', encoding='utf-8') as file:
                instruments = json.load(file)
                return [i for i in instruments]
            
        except FileNotFoundError:
            print(f"Error: The file {get_server_settings().instruments_names_file} does not exist.")
            return []
        except json.JSONDecodeError:
            print("Error: The JSON file is malformed.")
            return []
        


    @staticmethod
    def get_instruments_and_shortcuts_as_str(language_cod: str) -> str:
        """
        Returns a string with the instrument name translations and its shortcut.
        Throws FileNotFoundError if the instruments file does not exist,
        and JSONDecodeError if the file is malformed.
            :param language_cod: The language code to get the translation. It should be one of the following: "es_ES", "en_US", "ca_VA".
            :return: A string with the instrument name translations and its shortcut.        
        """
        instruments = InstrumentsNamesManager.get_instruments_and_shortcuts_translated(language_cod)
        return "\n".join([f"{name} -> {shortcut}" for name, shortcut in instruments])