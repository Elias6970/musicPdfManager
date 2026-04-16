from PyQt6.QtCore import QObject, pyqtSignal

from frontend.pyqt.app.pop_up_windows.resolve_unmached_presets.resolve_unmatched_presets_view import ResolveUnmatchedPresetsView
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError

class ResolveUnmatchedPresetsController(QObject):
    resolved_signal = pyqtSignal(list) #Tuple is (piece,preset_instrument,score_selected)
    def __init__(self,view:ResolveUnmatchedPresetsView) -> None:
        super().__init__()
        self.view = view
        self.view.confirm_signal.connect(self.confirm)
    
    def confirm(self):
        valid_items:list[tuple[str,str,str]] = []
        for i in self.view.items:
            if i.get_selection() is None:
                ShowError.show_tooltip_error(self.view.tr("Please select a score for this piece"),5000,i)
                return
            valid_items.append(i.get_selection())

        self.resolved_signal.emit(valid_items)
        self.view.accept()

    def set_unresolved_instruments(self, unresolved:list[tuple[str,str,list[str]]]):
        """
        Load the unresolved instruments in the view.
        The unresolved parameter is a list of tuples with the following structure:
        (piece_std_name, missing_instrument, options)
        where options is a list of strings with the format "file_name (copies)".
        """
        self.view.clear_items()
        for i in unresolved:
            self.view.add_item(i[0],i[1],i[2])
    
    def show(self):
        self.view.exec()
