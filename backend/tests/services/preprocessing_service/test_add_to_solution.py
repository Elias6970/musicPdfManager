import pytest
from backend.app.models.presets.resolution_preset import SolvedPreset, SolvedInstrument
from backend.app.services.preset_preprocessing_services import _add_to_solution

def test_add_to_solution_by_instrument_new_key():
    preset = SolvedPreset(solution={})
    
    _add_to_solution(preset, archive_id=1, piece_std_name="01-PIECE", instrument="Violin", file_name="file.pdf", copies=2, by_instrument=True)
    
    assert "Violin" in preset.solution
    assert "01-PIECE" in preset.solution["Violin"]
    
    instrument_obj = preset.solution["Violin"]["01-PIECE"]
    assert isinstance(instrument_obj, SolvedInstrument)
    assert instrument_obj.archive_id == 1
    assert instrument_obj.piece_std_name == "01-PIECE"
    assert instrument_obj.file == "file.pdf"
    assert instrument_obj.copies == 2

def test_add_to_solution_by_instrument_existing_key():
    preset = SolvedPreset(solution={})
    
    _add_to_solution(preset, archive_id=1, piece_std_name="01-PIECE", instrument="Violin", file_name="file1.pdf", copies=1, by_instrument=True)
    _add_to_solution(preset, archive_id=1, piece_std_name="02-PIECE", instrument="Violin", file_name="file2.pdf", copies=1, by_instrument=True)
    
    assert list(preset.solution.keys()) == ["Violin"]
    assert "01-PIECE" in preset.solution["Violin"]
    assert "02-PIECE" in preset.solution["Violin"]
    assert preset.solution["Violin"]["01-PIECE"].file == "file1.pdf"
    assert preset.solution["Violin"]["02-PIECE"].file == "file2.pdf"

def test_add_to_solution_by_piece_new_key():
    preset = SolvedPreset(solution={})
    
    _add_to_solution(preset, archive_id=1, piece_std_name="01-PIECE", instrument="Violin", file_name="file.pdf", copies=2, by_instrument=False)
    
    assert "01-PIECE" in preset.solution
    assert "Violin" in preset.solution["01-PIECE"]
    
    instrument_obj = preset.solution["01-PIECE"]["Violin"]
    assert isinstance(instrument_obj, SolvedInstrument)
    assert instrument_obj.archive_id == 1
    assert instrument_obj.piece_std_name == "01-PIECE"
    assert instrument_obj.file == "file.pdf"
    assert instrument_obj.copies == 2

def test_add_to_solution_by_piece_existing_key():
    preset = SolvedPreset(solution={})
    
    _add_to_solution(preset, archive_id=1, piece_std_name="01-PIECE", instrument="Violin", file_name="viol.pdf", copies=1, by_instrument=False)
    _add_to_solution(preset, archive_id=1, piece_std_name="01-PIECE", instrument="Cello", file_name="cel.pdf", copies=1, by_instrument=False)
    
    assert list(preset.solution.keys()) == ["01-PIECE"]
    assert "Violin" in preset.solution["01-PIECE"]
    assert "Cello" in preset.solution["01-PIECE"]
    assert preset.solution["01-PIECE"]["Violin"].file == "viol.pdf"
    assert preset.solution["01-PIECE"]["Cello"].file == "cel.pdf"

def test_add_to_solution_overwrite_existing_entry():
    preset = SolvedPreset(solution={})
    
    _add_to_solution(preset, archive_id=1, piece_std_name="01-PIECE", instrument="Violin", file_name="old.pdf", copies=1, by_instrument=True)
    # Overwrite the exact same position
    _add_to_solution(preset, archive_id=1, piece_std_name="01-PIECE", instrument="Violin", file_name="new.pdf", copies=5, by_instrument=True)
    
    assert len(preset.solution["Violin"]) == 1
    updated_obj = preset.solution["Violin"]["01-PIECE"]
    assert updated_obj.file == "new.pdf"
    assert updated_obj.copies == 5
