import io
import zipfile
from sqlmodel import Session
from backend.app.services.export_strategies.base_strategy import PresetExportStrategy
from backend.app.models.presets.resolution_preset import SolvedPreset
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJobConfig

class SplittedExporter(PresetExportStrategy):
    def export(self, session: Session, solved_preset: SolvedPreset, config: PresetPrintJobConfig) -> bytes:
        """
        Bypasses document merging and decorators. Iterates all keys and copies 
        individual PDFs into an organized folder tree inside a ZIP archive.
        Returns ZIP bytes.
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # TODO: Implement plain extraction to zip folders
            pass
            
        return zip_buffer.getvalue()
