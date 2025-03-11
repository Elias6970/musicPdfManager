import pytest
from classes.presets.preset import  Preset
from classes.constants import PRESETS_COPIES,PRESETS_OTHER_OPTIONS

def instruments_of_a_preset():
    return {
        "oboe_1" : {
            PRESETS_COPIES : 2,
            PRESETS_OTHER_OPTIONS : ["oboe","oboe_2","flauta_1","flauta_2","flauta","clarinete"]
            
        },
        "clarinete" : {
            PRESETS_COPIES : 10,
            PRESETS_OTHER_OPTIONS : ["clarinete_1","trombon"]
            
        },
        "caja" : {
            PRESETS_COPIES : 1,
            PRESETS_OTHER_OPTIONS : ["bombo"]
            
        }          
    }


def test_preset_creation():
    p = Preset("Juan")
    p.add_instrument("oboe_1",2,["oboe","oboe_2","flauta_1","flauta_2","flauta","clarinete"])
    p.add_instrument("clarinete",10,["clarinete_1","trombon"])
    p.add_instrument("caja",1,["bombo"])
    
    assert instruments_of_a_preset() == p.instruments

