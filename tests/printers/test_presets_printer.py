from classes.presets.preset import Preset
from classes.printers.presets_printer import PresetsPrinter
from classes.presets.resolved_preset_instrument import ResolvedPresetInstrument
from classes.presets.preset_resolver_states import PresetResolverStates
from classes.files_management.dir import Dir
import pytest,os


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



def test_export_by_instruments_one_pdf_file():
    oboe = "oboe"
    p = Preset("Primero")
    p.add_instrument(oboe,1)

    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)

    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    solution = {
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument
        }
    }
    try:
        os.mkdir("sol")
    except FileExistsError:
        pass
    try:
        os.mkdir("sol\\test1")
    except FileExistsError:
        pass

    pp.export_by_instruments(solution,"sol\\test1")


def test_export_by_instruments_two_instruments_one_piece_when_order_default():
    oboe = "oboe"
    clarinete = "clarinete"
    p = Preset("Primero")
    p.add_instrument(oboe,1)
    p.add_instrument(clarinete,1)


    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)

    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             clarinete,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Clarinete 1º.pdf")
    
    solution = {
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument
        },
        clarinete : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument2
        }
    }

    try:
        os.mkdir("sol")
    except FileExistsError:
        pass
    try:
        os.mkdir("sol\\test2")
    except FileExistsError:
        pass
    
    pp.export_by_instruments(solution,"sol\\test2")


def test_export_by_instruments_one_instrument_two_times_same_piece_when_order_default():
    oboe = "oboe"
    p = Preset("Primero")
    p.add_instrument(oboe,1)


    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)
    printeable_id = pp.add(1,p,dir)
    
    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Clarinete 1º.pdf")
    
    solution = {
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument
        },
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument2
        }
    }

    try:
        os.mkdir("sol")
    except FileExistsError:
        pass
    try:
        os.mkdir("sol\\test3")
    except FileExistsError:
        pass
    
    pp.export_by_instruments(solution,"sol\\test3")


def test_export_by_instruments_two_instruments_one_piece_when_order_default():
    oboe = "oboe"
    clarinete = "clarinete"
    p = Preset("Primero")
    p.add_instrument(oboe,1)
    p.add_instrument(clarinete,1)


    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)

    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             clarinete,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Clarinete 1º.pdf")
    
    solution = {
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument
        },
        clarinete : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument2
        }
    }

    try:
        os.mkdir("sol")
    except FileExistsError:
        pass
    try:
        os.mkdir("sol\\test2")
    except FileExistsError:
        pass
    
    pp.export_by_instruments(solution,"sol\\test2")


def test_export_by_instruments_one_instrument_two_different_pieces_when_order_default():
    oboe = "oboe"
    p = Preset("Primero")
    p.add_instrument(oboe,1)


    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")
    dir2 = Dir("..\\archivodigital\\1650-GTRT")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)
    printeable_id = pp.add(1,p,dir2)
    
    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "GTRT",
                             oboe,
                             "..\\archivodigital\\1650-GTRT\\partituras\\p.pdf")
    
    solution = {
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument,
            "GTRT" : resolved_instrument2
        }
    }

    try:
        os.mkdir("sol")
    except FileExistsError:
        pass
    try:
        os.mkdir("sol\\test4")
    except FileExistsError:
        pass
    
    pp.export_by_instruments(solution,"sol\\test4")


def test_export_by_instruments_one_instrument_two_times_different_pieces_when_order_alphabetic():
    oboe = "oboe"
    p = Preset("Primero")
    p.add_instrument(oboe,1)


    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")
    dir2 = Dir("..\\archivodigital\\1650-GTRT")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)
    printeable_id = pp.add(1,p,dir2)
    
    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "GTRT",
                             oboe,
                             "..\\archivodigital\\1650-GTRT\\partituras\\p.pdf")
    
    solution = {
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument,
            "GTRT" : resolved_instrument2
        }
    }

    try:
        os.mkdir("sol")
    except FileExistsError:
        pass
    try:
        os.mkdir("sol\\test5")
    except FileExistsError:
        pass
    
    pp.sorted_export = True
    pp.export_by_instruments(solution,"sol\\test5")




def test_export_by_instruments_two_instrument_two_different_pieces_each_instrument_when_order_default():
    oboe = "oboe"
    clarinete = "clarinete"
    p = Preset("Primero")
    p.add_instrument(oboe,1)
    p.add_instrument(clarinete,1)


    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")
    dir2 = Dir("..\\archivodigital\\1650-GTRT")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)
    printeable_id = pp.add(1,p,dir2)
    
    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "GTRT",
                             oboe,
                             "..\\archivodigital\\1650-GTRT\\partituras\\p.pdf")
    resolved_instrument_clar = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "LA BODA DE LUIS ALONSO",
                             clarinete,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Caja.pdf")
    resolved_instrument_clar2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "GTRT",
                             clarinete,
                             "..\\archivodigital\\1650-GTRT\\partituras\\imprimir.pdf")
    
    solution = {
        oboe : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument,
            "GTRT" : resolved_instrument2
        },
        clarinete : {
            "LA BODA DE LUIS ALONSO" : resolved_instrument_clar,
            "GTRT" : resolved_instrument_clar2            
        }
    }

    try:
        os.mkdir("sol")
    except FileExistsError:
        pass
    try:
        os.mkdir("sol\\test6")
    except FileExistsError:
        pass
    
    pp.export_by_instruments(solution,"sol\\test6")


def test_preprocess_export_should_one_instrument_one_piece_when_one_instrument():
    oboe = "Oboes"
    p = Preset("Primero")
    p.add_instrument(oboe,1)

    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)

    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "71-LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    
    solution = pp.preprocess_export()
    expected = {
        oboe : {
            "71-LA BODA DE LUIS ALONSO" : resolved_instrument
        }
    }

    assert len(solution[1]) == 0

    assert expected.get(oboe).keys() == solution[0].get(oboe).keys()

    assert expected.get(oboe)["71-LA BODA DE LUIS ALONSO"].resolution == solution[0].get(oboe)["71-LA BODA DE LUIS ALONSO"].resolution




def test_preprocess_export_should_one_instrument_two_pieces_when_one_instrument():
    oboe = "Oboes"
    p = Preset("Primero")
    p.add_instrument(oboe,1)

    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")
    dir2 = Dir("..\\archivodigital\\1650-GTRT")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)
    printeable_id = pp.add(1,p,dir2)

    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "71-LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "1650-GTRT",
                             oboe,
                             "..\\archivodigital\\1650-GTRT\\partituras\\Oboes.pdf")
    
    solution = pp.preprocess_export()
    expected = {
        oboe : {
            "71-LA BODA DE LUIS ALONSO" : resolved_instrument,
            "1650-GTRT" : resolved_instrument2
        }
    }

    assert len(solution[1]) == 0

    assert expected.get(oboe).keys() == solution[0].get(oboe).keys()

    assert expected.get(oboe)["71-LA BODA DE LUIS ALONSO"].resolution == solution[0].get(oboe)["71-LA BODA DE LUIS ALONSO"].resolution
    assert expected.get(oboe)["1650-GTRT"].resolution == solution[0].get(oboe)["1650-GTRT"].resolution


def test_preprocess_export_should_one_instrument_two_pieces_when_two_instruments():
    oboe = "Oboes"
    clarinete = "Clarinete 1º"

    p = Preset("Primero")
    p.add_instrument(oboe,1)
    p.add_instrument(clarinete,1)

    dir = Dir("..\\archivodigital\\71-LA BODA DE LUIS ALONSO")
    dir2 = Dir("..\\archivodigital\\1650-GTRT")

    pp = PresetsPrinter()
    printeable_id = pp.add(1,p,dir)
    printeable_id = pp.add(1,p,dir2)

    resolved_instrument = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "71-LA BODA DE LUIS ALONSO",
                             oboe,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Oboes.pdf")
    resolved_instrument2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "1650-GTRT",
                             oboe,
                             "..\\archivodigital\\1650-GTRT\\partituras\\Oboes.pdf")
    resolved_instrument_clar = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "71-LA BODA DE LUIS ALONSO",
                             clarinete,
                             "..\\archivodigital\\71-LA BODA DE LUIS ALONSO\\partituras\\Clarinete 1º.pdf")
    resolved_instrument_clar2 = ResolvedPresetInstrument(PresetResolverStates.RESOLVED,
                             1,
                             "1650-GTRT",
                             clarinete,
                             "..\\archivodigital\\1650-GTRT\\partituras\\Clarinete 1º.pdf")
    
    
    solution = pp.preprocess_export()
    expected = {
        oboe : {
            "71-LA BODA DE LUIS ALONSO" : resolved_instrument,
            "1650-GTRT" : resolved_instrument2
        },
        clarinete : {
            "71-LA BODA DE LUIS ALONSO" : resolved_instrument_clar,
            "1650-GTRT" : resolved_instrument_clar2
        }

    }

    assert len(solution[1]) == 0

    assert expected.get(oboe).keys() == solution[0].get(oboe).keys()

    assert expected.get(oboe)["71-LA BODA DE LUIS ALONSO"].resolution == solution[0].get(oboe)["71-LA BODA DE LUIS ALONSO"].resolution
    assert expected.get(oboe)["1650-GTRT"].resolution == solution[0].get(oboe)["1650-GTRT"].resolution
    assert expected.get(clarinete)["71-LA BODA DE LUIS ALONSO"].resolution == solution[0].get(clarinete)["71-LA BODA DE LUIS ALONSO"].resolution
    assert expected.get(clarinete)["1650-GTRT"].resolution == solution[0].get(clarinete)["1650-GTRT"].resolution
