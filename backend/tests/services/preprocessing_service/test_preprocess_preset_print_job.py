import pytest
from unittest.mock import patch, MagicMock
from backend.app.models.presets.resolution_preset import SolvedPreset, UnresolvedInstrumentResponse
from backend.app.services.preset_preprocessing_services import _preprocess_preset_print_job

@pytest.fixture
def base_mocks():
    """Provides common mocks for the preprocessor tests."""
    with patch("backend.app.services.preset_preprocessing_services.get_archive_path") as mock_path, \
         patch("backend.app.services.preset_preprocessing_services.ArchiveFileManager") as mock_manager, \
         patch("backend.app.services.preset_preprocessing_services.get_scores") as mock_get_scores, \
         patch("backend.app.services.preset_preprocessing_services.InstrumentSorter.sort_instruments") as mock_sorter:
        
        mock_path.return_value = "dummy/path"
        mock_sorter.side_effect = lambda x: x  # Just return the same list to simplify testing
        
        yield mock_get_scores

def _create_mock_job_and_preset():
    session = MagicMock()
    
    job = MagicMock()
    job.archive_id = 1
    piece = MagicMock()
    piece.std_name = "01-TEST"
    piece.copies = 1
    job.pieces = [piece]
    job.solved_fails = {}
    job.config = MagicMock()
    job.config.group_by_instrument = True
    job.config.ignore_preset_copies = False
    
    preset = MagicMock()
    instrument_config = MagicMock()
    instrument_config.other_options = []
    instrument_config.copies = 1
    preset.instruments = {"Violin I": instrument_config}
    
    return session, job, preset

def test_preprocess_direct_match(base_mocks):
    session, job, preset = _create_mock_job_and_preset()
    base_mocks.return_value = ["Violin I", "Cello"]
    
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    assert len(unresolved) == 0
    assert "Violin I" in solved.solution
    assert "01-TEST" in solved.solution["Violin I"]
    assert solved.solution["Violin I"]["01-TEST"].file == "Violin I.pdf"

def test_preprocess_other_options_match(base_mocks):
    session, job, preset = _create_mock_job_and_preset()
    preset.instruments["Violin I"].other_options = ["Vln 1", "Vn 1"]
    base_mocks.return_value = ["Vn 1", "Cello"]  # Exact "Violin I" is missing, but "Vn 1" is there
    
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    assert len(unresolved) == 0
    assert "Violin I" in solved.solution
    assert solved.solution["Violin I"]["01-TEST"].file == "Vn 1.pdf"

def test_preprocess_solved_fails_match(base_mocks):
    session, job, preset = _create_mock_job_and_preset()
    base_mocks.return_value = []  # No files found on disk normally
    job.solved_fails = {"01-TEST": {"Violin I": "custom_override"}}
    
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    assert len(unresolved) == 0
    assert "Violin I" in solved.solution
    assert solved.solution["Violin I"]["01-TEST"].file == "custom_override.pdf"

def test_preprocess_unresolved(base_mocks):
    session, job, preset = _create_mock_job_and_preset()
    base_mocks.return_value = ["Viola"]  # Completely unrelated files available
    
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    assert len(solved.solution) == 0
    assert len(unresolved) == 1
    
    unresolved_item = unresolved[0]
    assert isinstance(unresolved_item, UnresolvedInstrumentResponse)
    assert unresolved_item.archive_id == 1
    assert unresolved_item.piece_std_name == "01-TEST"
    assert unresolved_item.missing_instrument == "Violin I"
    assert unresolved_item.options == ["Viola"]

def test_preprocess_by_piece(base_mocks):
    session, job, preset = _create_mock_job_and_preset()
    job.config.group_by_instrument = False
    base_mocks.return_value = ["Violin I", "Cello"]
    
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    assert len(unresolved) == 0
    assert "01-TEST" in solved.solution
    assert "Violin I" in solved.solution["01-TEST"]
    assert solved.solution["01-TEST"]["Violin I"].file == "Violin I.pdf"

def test_preprocess_ignore_copies(base_mocks):
    session, job, preset = _create_mock_job_and_preset()
    job.pieces[0].copies = 2
    job.config.ignore_preset_copies = True
    preset.instruments["Violin I"].copies = 5
    base_mocks.return_value = ["Violin I", "Cello"]
    
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    assert len(unresolved) == 0
    # Even if instrument copies are ignored (set to 1), piece copies are still applied
    assert solved.solution["Violin I"]["01-TEST"].copies == 2

def test_preprocess_applies_piece_copies(base_mocks):
    session, job, preset = _create_mock_job_and_preset()
    job.pieces[0].copies = 3
    preset.instruments["Violin I"].copies = 4
    base_mocks.return_value = ["Violin I"]
    
    solved, unresolved = _preprocess_preset_print_job(session, job, preset)
    
    assert len(unresolved) == 0
    assert "Violin I" in solved.solution
    # 3 copies of piece * 4 copies of instrument = 12 copies total
    assert solved.solution["Violin I"]["01-TEST"].copies == 12
