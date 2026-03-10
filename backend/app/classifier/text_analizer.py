import os,re
from typing import Tuple
from backend.app.instruments_names_manager import InstrumentsNamesManager

class TextAnalizer():
    instruments = InstrumentsNamesManager.get_shortcuts_and_instruments()
    instruments_pattern = '|'.join(map(re.escape, list(instruments.keys())))

    def __init__(self) -> None:
        pass
    
    #Return a tuple with the (instrument,number) or 
    #raise a ValueError if doens't match any re (probably because input has not letters or numbers)
    @staticmethod
    def parse_input(text:str) -> Tuple[str,str|None]:

        if re.fullmatch(fr'^(?:{TextAnalizer.instruments_pattern})$', text, re.IGNORECASE):
            return (text,None)
        
        elif re.fullmatch(fr'^(?:{TextAnalizer.instruments_pattern})\d$', text, re.IGNORECASE):
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



    #Analize the input and return the name of the file
    #Can raise ValueError if doesn't match any re
    @staticmethod
    def analize(text:str):
        instrument,num = TextAnalizer.parse_input(text)

        num = "" if num == None else "_"+num
        try:
            return TextAnalizer.instruments[instrument]+num
        except KeyError as e:
            return instrument.replace(' ','_').lower()+num
        
    

    #Return a list with the internal names of the instruments
    @staticmethod
    def get_internal_names(names:list[str]):
        internal_names:list[str] = []
        for i in names:
            #Quit .pdf
            i = os.path.splitext(i)[0]
            
            try:
                internal_names.append(i.split("_")[0]+i.split("_")[1])
            except IndexError:
                internal_names.append(i.split("_")[0])
            
        return internal_names