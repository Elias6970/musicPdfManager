import pickle,os,sys

#Config files location
#The sys._MEIPASS is variable that has the path to a temp folder where data folder is created. 
#Every time you execute the application a temp folder is created
"""if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    PLAIN_TEXT_CONFIG_PATH = os.path.join(sys._MEIPASS,"data","config.yml") #type: ignore
    PRESETS_PATH = os.path.join(sys._MEIPASS,"data","presets.bin") #type: ignore
else:"""
PLAIN_TEXT_CONFIG_PATH = os.path.join("data","config.yml")
PRESETS_PATH = os.path.join("data","presets.bin")


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
        #return Configuration_setter.import_archive_path()
        try:
            with open(PLAIN_TEXT_CONFIG_PATH,'r') as file:
                for i in file.readlines():
                    split = i.split("=")
                    if(split[0].upper() == "ARCHIVE_PATH"):
                        return split[1].split("\n")[0]

        except FileNotFoundError:
            try:
                os.mkdir("data")
            except Exception:
                pass
            
            open(PLAIN_TEXT_CONFIG_PATH,'w')

        return ""
    
    
    @staticmethod
    def get_dossier_cover() -> str:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS,"data","portada_dossier_partituras.pdf") #type: ignore
        
        try:     
            with open(PLAIN_TEXT_CONFIG_PATH,'r') as file:
                for i in file.readlines():
                    split = i.split("=")
                    if(split[0].upper() == "DOSSIER_COVER"):
                        return split[1].split("\n")[0]

        except FileNotFoundError:
            try:
                os.mkdir("data")
            except Exception:
                pass
            
            open(PLAIN_TEXT_CONFIG_PATH,'w')

        
        return ""        


    @staticmethod
    def get_presets() -> list[Instruments_preset]:
        try:
            return Configuration_setter.import_prests()
        except FileNotFoundError:
            pass
        return []

    @staticmethod
    def export_paths(archive_path:str,dossier_cover:str):
        with open(PLAIN_TEXT_CONFIG_PATH,'w') as file:
            file.write("ARCHIVE_PATH="+archive_path+"\n")
            file.write("DOSSIER_COVER="+dossier_cover)