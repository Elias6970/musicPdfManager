import pickle,os,sys

#Config files location
PLAIN_TEXT_CONFIG_PATH = os.path.join("data","config.yml")
PRESETS_PATH = os.path.join("data","presets.bin")

#Class that represents a list of instruments to make presets to make pdfs
class Instruments_preset():
    def __init__(self) -> None:
        self.instruments:list[str] = []

    
    def add_instrument(self,new_instruments:str | list[str]):
        if type(new_instruments) == str:
            new_instruments = [new_instruments]
        
        for i in new_instruments:
            self.instruments.append(i)

    def delete_instrument(self,instrument:str):
        self.instruments.remove(instrument)


class Configuration_setter():
    @staticmethod
    def import_archive_path():
        try:
            with open(PLAIN_TEXT_CONFIG_PATH,'r') as file:
                for i in file.readlines():
                    split = i.split("=")
                    if(split[0].upper() == "ARCHIVE_PATH"):
                        return split[1].split("\n")[0]

        except FileNotFoundError:
            open(PLAIN_TEXT_CONFIG_PATH,'w')

        return ""
    
    @staticmethod
    def import_dossier_cover_path():
        try:     
            with open(PLAIN_TEXT_CONFIG_PATH,'r') as file:
                for i in file.readlines():
                    split = i.split("=")
                    if(split[0].upper() == "DOSSIER_COVER"):
                        return split[1].split("\n")[0]

        except FileNotFoundError:
            open(PLAIN_TEXT_CONFIG_PATH,'w')
        
        return ""
    
    @staticmethod
    def import_prests():
        with open(PRESETS_PATH,'rb') as file:
            a = pickle.load(file)
        return a

    @staticmethod
    def export_presets(presets:list[Instruments_preset],path:str):
        with open(PRESETS_PATH,'wb') as file:      
            pickle.dump(presets,file)
            file.close()
    
    @staticmethod
    def export_paths(archive_path:str,dossier_cover:str):
        with open(PLAIN_TEXT_CONFIG_PATH,'w') as file:
            file.write("ARCHIVE_PATH="+archive_path+"\n")
            file.write("DOSSIER_COVER="+dossier_cover)

#Idea of static class to get the configuration of the application
class Configuration():

    @staticmethod
    def get_archive_path() -> str:
        return Configuration_setter.import_archive_path()
    
    @staticmethod
    def get_dossier_cover() -> str:
        return Configuration_setter.import_dossier_cover_path()

    @staticmethod
    def get_presets() -> list[Instruments_preset]:
        try:
            return Configuration_setter.import_prests()
        except FileNotFoundError:
            pass
        return []
