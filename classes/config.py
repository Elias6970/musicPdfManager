import pickle,os,sys,locale,ctypes

#Config files location
PLAIN_TEXT_CONFIG_PATH = os.path.join("data","config.yml")
PRESETS_PATH = os.path.join("data","presets.bin")

#Languages
LAN_ESP = "Espanol"
LAN_ENG = "English"
LAN_VAL = "Valencià"

#Class that represents a list of instruments to make presets to make pdfs
class Instruments_preset():
    def __init__(self) -> None:
        self.instruments:list[str] = []

    def set_name(self,name):
        self.name = name
    
    def add_instrument(self,new_instruments:str | list[str]):
        if type(new_instruments) == str:
            new_instruments = [new_instruments]
        
        for i in new_instruments:
            self.instruments.append(i)

    def delete_instrument(self,instrument:str):
        self.instruments.remove(instrument)



#Idea of static class to get the configuration of the application
class Configuration():
    @staticmethod
    def get_attribute(attribute):
        try:
            with open(PLAIN_TEXT_CONFIG_PATH,'r') as file:
                for i in file.readlines():
                    split = i.split("=")
                    if(split[0].upper() == attribute):
                        return split[1].split("\n")[0]

        except FileNotFoundError:
            try:
                os.mkdir("data")
            except Exception:
                pass
            
            open(PLAIN_TEXT_CONFIG_PATH,'w')

        return ""
    
    
    @staticmethod
    def get_archive_path() -> str:
        return Configuration.get_attribute("ARCHIVE_PATH")
    
    @staticmethod
    def get_dossier_cover_path() -> str:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS,"data","portada_dossier_partituras.pdf") #type: ignore
        
        return Configuration.get_attribute("DOSSIER_COVER")       

    @staticmethod
    def get_language() -> str:
        language = Configuration.get_attribute("LANGUAGE")
        
        if language == "":
            #Get the system language
            if os.name == 'posix':
                return os.getenv('LANG')
            else:
                language = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
       
        if language.startswith("es_"):
            return LAN_ESP
        #for valenciano and catalan
        elif language.startswith("ca_"):
            return LAN_VAL
        #default case is english
        else:
            return LAN_ENG


    #If the language is not supported return an empty string
    @staticmethod
    def name_to_cod_language(name:str) -> str:
        if name == LAN_ESP:
            return "es_ES"
        elif name == LAN_ENG:
            return "en_US"
        elif name == LAN_VAL:
            return "ca_VA"
        else:
            return ""
    

    @staticmethod
    def get_presets() -> list[Instruments_preset]:
        try:
            with open(PRESETS_PATH,'rb') as file:
                a = pickle.load(file)
            return a

        except FileNotFoundError:
            pass
        return []

    #Lenguage has to be in es_ES format
    @staticmethod
    def save_config(archive_path:str,dossier_cover:str,language:str):
        with open(PLAIN_TEXT_CONFIG_PATH,'w') as file:
            file.write("ARCHIVE_PATH="+archive_path+"\n")
            file.write("DOSSIER_COVER="+dossier_cover+"\n")
            file.write("LANGUAGE="+language+"\n")


