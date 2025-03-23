from classes.printers.printeable_file import PrinteableFile
from classes.printers.default_printer import DefualtPrinter
import pytest

def test_create_printeable_files():
    a1 = PrinteableFile("H",20)
    a2 = PrinteableFile("M",2)
    a3 = PrinteableFile("CC",200)

    assert a1.id == 0
    assert a1.copies == 20
    assert a2.id == 1
    assert a2.copies == 2
    assert a3.id == 2
    assert a3.copies == 200


def test_create_default_printer():
    t1 = "H"
    copies1 = 20
    t2 = "M"
    copies2 = 3

    dp = DefualtPrinter()
    i1 = dp.add(t1,copies1)
    i2 = dp.add(t2,copies2)

    assert dp.items[0].path == "H"
    assert dp.items[0].copies == 20
    assert dp.items[1].path == "M"
    assert dp.items[1].copies == 3
    
    assert dp.remove(i1)
    assert dp.items[0].path == "M"
    assert dp.items[0].copies == 3



