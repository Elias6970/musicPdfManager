from PyQt6 import QtCore

from app.pop_up_windows.type_of_export.type_of_export_view import TypeOfExportView
from app.models.generated_models import ExportStrategyType, PresetPrintJobConfig

class TypeOfExportController(QtCore.QObject):
    export_signal = QtCore.pyqtSignal(PresetPrintJobConfig)

    def __init__(self, view:TypeOfExportView):
        super().__init__()
        self.view = view

        self.view.confirmed.connect(self.confirm)

    def show(self):
        self.view.exec()

    def confirm(self):
        config_kwargs = {
            "export_strategy": self.view.export_strategy,
            "group_by_instrument": self.view.is_by_instruments,
            "ignore_preset_copies": self.view.ignore_preset_copies,
            "sorted_export": self.view.sort_alphabetically,
            "add_cover_page": self.view.add_cover_page,
            "add_index": self.view.add_index,
            "add_blank_page_after_index": self.view.add_blank_page_after_index,
            "add_piece_number": self.view.add_piece_numbers,
        }
        
        if self.view.cover_title:
            config_kwargs["cover_title"] = self.view.cover_title
        if self.view.index_title:
            config_kwargs["index_title"] = self.view.index_title
        if self.view.index_subtitle:
            config_kwargs["index_subtitle"] = self.view.index_subtitle

        config = PresetPrintJobConfig(**config_kwargs)
        self.export_signal.emit(config)
