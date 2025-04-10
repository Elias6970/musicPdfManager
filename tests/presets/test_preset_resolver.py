from classes.presets.preset_resolver import PresetResolver, PresetResolverStates
from classes.presets.preset import Preset
from classes.constants.constants import PRESETS_COPIES,PRESETS_OTHER_OPTIONS
import pytest



def test_presetResolver_same_names_resolution():
    p = Preset("Juan")
    p.add_instrument("oboe_1",2,["oboe","oboe_2","flauta_1","flauta_2","flauta","clarinete"])
    p.add_instrument("clarinete",10,["clarinete_1","trombon"])
    p.add_instrument("caja",1,["bombo"])
    scores = ["oboe_1","clarinete","caja"]

    preset_resolver = PresetResolver()
    resolution = preset_resolver.resolve(p,scores)

    assert resolution == [(PresetResolverStates.RESOLVED,2,"oboe_1","oboe_1"),
                          (PresetResolverStates.RESOLVED,10,"clarinete","clarinete"),
                          (PresetResolverStates.RESOLVED,1,"caja","caja")]


def test_presetResolver_in_others_lists():
    p = Preset("Juan")
    p.add_instrument("oboe_1",2,["oboe","oboe_2","flauta_1","flauta_2","flauta","clarinete"])
    p.add_instrument("clarinete",10,["clarinete_1","trombon"])
    p.add_instrument("caja",1,["bombo"])
    
    scores = ["oboe","trombon","bombo"]

    preset_resolver = PresetResolver()
    resolution = preset_resolver.resolve(p,scores)

    expected_resolution = [(PresetResolverStates.RESOLVED,2,"oboe_1","oboe"),
                          (PresetResolverStates.RESOLVED,10,"clarinete","trombon"),
                          (PresetResolverStates.RESOLVED,1,"caja","bombo")]

    assert resolution == expected_resolution

#Is going to fail becasue auto resolved is not yet implemented
#Need to be autoresolved
def test_presetResolver_same_instrument_not_in_the_list():
    p = Preset("Juan")
    p.add_instrument("oboe_1",2,["flauta_1","flauta_2","flauta","clarinete"])
    p.add_instrument("clarinete_3",10,["flauta","arpa_2"])
    p.add_instrument("caja_2",1,["bombo"])
    
    scores = ["oboe","clarinete","caja"]

    preset_resolver = PresetResolver()
    resolution = preset_resolver.resolve(p,scores)
    
    expected_resolution = [(PresetResolverStates.AUTO_RESOLVED,2,"oboe_1","oboe"),
                          (PresetResolverStates.AUTO_RESOLVED,10,"clarinete_3","clarinete"),
                          (PresetResolverStates.AUTO_RESOLVED,1,"caja_2","caja")]

    assert resolution == expected_resolution




def test_instrument_different_number():
    pass