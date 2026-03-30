import io
import zipfile
from sqlmodel import Session
from backend.app.services.export_strategies.base_strategy import PresetExportStrategy
from backend.app.models.presets.resolution_preset import SolvedPreset
from backend.app.models.printers.jobs.preset_print_job import PresetPrintJobConfig

class ByElementExporter(PresetExportStrategy):
    def export(self, session: Session, solved_preset: SolvedPreset, config: PresetPrintJobConfig) -> bytes:
        """
        Iterates outer keys, merges inner keys per element into separate documents.
        Applies decorators independently to each generated element document.
        Zips all the PDFs and returns ZIP bytes.
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # TODO: Implement element merging and zipping
            pass
            
        return zip_buffer.getvalue()
