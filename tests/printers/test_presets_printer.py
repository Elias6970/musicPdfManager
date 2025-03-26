from classes.presets.preset import Preset
from classes.printers.presets_printer import PresetsPrinter
from classes.printers.printeable_preset import PrinteablePreset
from classes.files_management.dir import Dir
import pytest


def test_create_and_remove_presets_printer():
    p = Preset("Primero")
    p.add_instrument("oboe",3,["clariente","flauta"])
    
    dir = Dir("abc")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)

    assert pp.items[0].copies == 1
    assert pp.items[0].preset == p
    assert pp.items[0].dir == dir

    assert pp.remove(printeable_id) == True
  
    assert len(pp.items) == 0


def test_create_create_and_remove_presets_printer():
    p = Preset("Primero")
    p.add_instrument("oboe",3,["clariente","flauta"])
    
    p2 = Preset("Segundo")
    p2.add_instrument("fagot",3,["platos","flauta"])
    
    p3 = Preset("Tercero")
    p3.add_instrument("clarinete",3,["clariente","flauta"])
    
    dir = Dir("abc")
    dir2 = Dir("mrew")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)
    printeable_id_2 = pp.add(4,p2,dir)
    printeable_id_3 = pp.add(2,p3,dir2)

    assert pp.items[0].copies == 1
    assert pp.items[0].preset == p
    assert pp.items[0].dir == dir
    assert pp.items[1].copies == 4
    assert pp.items[1].preset == p2
    assert pp.items[1].dir == dir
    assert pp.items[2].copies == 2
    assert pp.items[2].preset == p3
    assert pp.items[2].dir == dir2

    assert pp.remove(printeable_id_2) == True
    assert len(pp.items) == 2


    assert pp.items[0].copies == 1
    assert pp.items[0].preset == p
    assert pp.items[0].dir == dir
    assert pp.items[1].copies == 2
    assert pp.items[1].preset == p3
    assert pp.items[1].dir == dir2