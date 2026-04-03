from abc import ABC, abstractmethod
from sqlmodel import Session

from backend.app.models.presets.resolution_preset import SolvedPreset
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJobConfig

class PresetExportStrategy(ABC):
    @abstractmethod
    def export(self, session: Session, solved_preset: SolvedPreset, config: PresetPrintJobConfig) -> bytes:
        """
        Processes the dictionary of resolved files and exports it as bytes.
        Depending on the strategy, this returns a single PDF's bytes or a ZIP archive's bytes.
        """
        pass
