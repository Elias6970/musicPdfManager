import pytest
from unittest.mock import MagicMock

import backend.app.massive_import.excell_extractor_services as services
from backend.app.massive_import.excell_extractor_services import (
    _read_csv,
    _read_xls,
    _read_xlsx,
    clean_str,
    clean_to_int,
    read_data,
)


class _FakeXlrdSheet:
    def __init__(self, rows):
        self._rows = rows
        self.nrows = len(rows)

    def row_values(self, i):
        return self._rows[i]


class _FakeXlrdBook:
    def __init__(self, rows):
        self._sheet = _FakeXlrdSheet(rows)

    def sheet_by_index(self, _index):
        return self._sheet


class _FakeCell:
    def __init__(self, value):
        self.value = value


class _FakeOpenpyxlSheet:
    def __init__(self, rows):
        self._rows = rows

    def iter_rows(self):
        for row in self._rows:
            yield tuple(_FakeCell(v) for v in row)


class _FakeOpenpyxlBook:
    def __init__(self, rows):
        self.worksheets = [_FakeOpenpyxlSheet(rows)]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("\t  Hello\n", "Hello"),
        ("Line1\nLine2", "Line1 Line2"),
        ("  A\tB  ", "A B"),
        ("", ""),
    ],
)
def test_clean_str(raw, expected):
    assert clean_str(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("123", 123),
        (" 1,234 ", 1234),
        ("AB-99-CD", 99),
        ("12.34", 1234),
        ("", 0),
        ("abc", 0),
    ],
)
def test_clean_to_int(raw, expected):
    assert clean_to_int(raw) == expected


def test_read_data_dispatches_to_xlsx(monkeypatch):
    sentinel = [(1, "a", "b", "c")]
    spy = MagicMock(return_value=sentinel)
    monkeypatch.setattr(services, "_read_xlsx", spy)

    result = read_data("file.xlsx", ignore_first_row=True)

    assert result == sentinel
    spy.assert_called_once_with("file.xlsx", True)


def test_read_data_dispatches_to_xls(monkeypatch):
    sentinel = [(2, "x", "y", "z")]
    spy = MagicMock(return_value=sentinel)
    monkeypatch.setattr(services, "_read_xls", spy)

    result = read_data("file.xls", ignore_first_row=False)

    assert result == sentinel
    spy.assert_called_once_with("file.xls", False)


def test_read_data_dispatches_to_csv(monkeypatch):
    sentinel = [(3, "m", "n", "o")]
    spy = MagicMock(return_value=sentinel)
    monkeypatch.setattr(services, "_read_csv", spy)

    result = read_data("file.csv", ignore_first_row=True)

    assert result == sentinel
    spy.assert_called_once_with("file.csv", True)


def test_read_data_returns_empty_list_for_unsupported_extension():
    assert read_data("file.txt") == []


def test_read_csv_reads_valid_rows(tmp_path, monkeypatch):
    file_path = tmp_path / "ok.csv"
    file_path.write_text(
        "101, Symphony , Beethoven , classical \n"
        "202,Nocturne, Chopin, romantic\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(services, "logger", MagicMock())

    result = _read_csv(str(file_path), ignore_first_row=False)

    assert result == [
        (101, "Symphony", "Beethoven", "classical"),
        (202, "Nocturne", "Chopin", "romantic"),
    ]


def test_read_csv_ignores_first_row(tmp_path, monkeypatch):
    file_path = tmp_path / "header.csv"
    file_path.write_text(
        "code,name,composer,type\n"
        "303, Waltz , Strauss , dance\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(services, "logger", MagicMock())

    result = _read_csv(str(file_path), ignore_first_row=True)

    assert result == [(303, "Waltz", "Strauss", "dance")]


def test_read_csv_logs_error_and_continues_on_bad_row(tmp_path, monkeypatch):
    file_path = tmp_path / "bad.csv"
    file_path.write_text(
        "111,Title,Composer,Type\n"
        "bad,row\n"
        "222,Title2,Composer2,Type2\n",
        encoding="utf-8",
    )
    fake_logger = MagicMock()
    monkeypatch.setattr(services, "logger", fake_logger)

    result = _read_csv(str(file_path), ignore_first_row=False)

    assert result == [
        (111, "Title", "Composer", "Type"),
        (222, "Title2", "Composer2", "Type2"),
    ]
    assert fake_logger.error.call_count >= 1


def test_read_xls_reads_valid_rows(monkeypatch):
    rows = [
        [101, " Symphony ", " Beethoven ", " classical "],
        [202, "Nocturne", "Chopin", "romantic"],
    ]
    monkeypatch.setattr(services.xlrd, "open_workbook", lambda _p: _FakeXlrdBook(rows))
    monkeypatch.setattr(services, "logger", MagicMock())

    result = _read_xls("dummy.xls", ignore_first_row=False)

    assert result == [
        (101, "Symphony", "Beethoven", "classical"),
        (202, "Nocturne", "Chopin", "romantic"),
    ]


def test_read_xls_ignores_first_row(monkeypatch):
    rows = [
        ["code", "name", "composer", "type"],
        [303, " Waltz ", " Strauss ", " dance "],
    ]
    monkeypatch.setattr(services.xlrd, "open_workbook", lambda _p: _FakeXlrdBook(rows))
    monkeypatch.setattr(services, "logger", MagicMock())

    result = _read_xls("dummy.xls", ignore_first_row=True)

    assert result == [(303, "Waltz", "Strauss", "dance")]


def test_read_xls_logs_error_and_continues(monkeypatch):
    rows = [
        [111, "T1", "C1", "Type1"],
        [999],  # malformed
        [222, "T2", "C2", "Type2"],
    ]
    fake_logger = MagicMock()
    monkeypatch.setattr(services.xlrd, "open_workbook", lambda _p: _FakeXlrdBook(rows))
    monkeypatch.setattr(services, "logger", fake_logger)

    result = _read_xls("dummy.xls", ignore_first_row=False)

    assert result == [
        (111, "T1", "C1", "Type1"),
        (222, "T2", "C2", "Type2"),
    ]
    assert fake_logger.error.call_count >= 1


def test_read_xlsx_reads_valid_rows_and_skips_empty_first_cell(monkeypatch):
    rows = [
        [101, " Symphony ", " Beethoven ", " classical "],
        [None, "ignored", "ignored", "ignored"],  # skipped by code
        [202, "Nocturne", "Chopin", "romantic"],
    ]
    monkeypatch.setattr(
        services.openpyxl,
        "load_workbook",
        lambda _p: _FakeOpenpyxlBook(rows),
    )
    monkeypatch.setattr(services, "logger", MagicMock())

    result = _read_xlsx("dummy.xlsx", ignore_first_row=False)

    assert result == [
        (101, "Symphony", "Beethoven", "classical"),
        (202, "Nocturne", "Chopin", "romantic"),
    ]


def test_read_xlsx_ignores_first_row(monkeypatch):
    rows = [
        ["code", "name", "composer", "type"],
        [303, " Waltz ", " Strauss ", " dance "],
    ]
    monkeypatch.setattr(
        services.openpyxl,
        "load_workbook",
        lambda _p: _FakeOpenpyxlBook(rows),
    )
    monkeypatch.setattr(services, "logger", MagicMock())

    result = _read_xlsx("dummy.xlsx", ignore_first_row=True)

    assert result == [(303, "Waltz", "Strauss", "dance")]


def test_read_xlsx_logs_error_and_continues(monkeypatch):
    rows = [
        [111, "T1", "C1", "Type1"],
        [999],  # malformed
        [222, "T2", "C2", "Type2"],
    ]
    fake_logger = MagicMock()
    monkeypatch.setattr(
        services.openpyxl,
        "load_workbook",
        lambda _p: _FakeOpenpyxlBook(rows),
    )
    monkeypatch.setattr(services, "logger", fake_logger)

    result = _read_xlsx("dummy.xlsx", ignore_first_row=False)

    assert result == [
        (111, "T1", "C1", "Type1"),
        (222, "T2", "C2", "Type2"),
    ]
    assert fake_logger.error.call_count >= 1