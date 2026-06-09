from PyQt6 import QtWidgets,QtCore, QtGui
import unicodedata

def strip_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

class AccentInsensitiveProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_text = ""

    def setFilterText(self, text: str):
        self.filter_text = text
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        source_model = self.sourceModel()
        if source_model is None:
            return False
        
        index = source_model.index(source_row, self.filterKeyColumn(), source_parent)
        data = source_model.data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if data is None:
            return False
            
        if not self.filter_text:
            return True
            
        data_stripped = strip_accents(str(data)).lower()
        search_term_stripped = strip_accents(self.filter_text).lower()
        
        return search_term_stripped in data_stripped

class AccentInsensitiveCompleter(QtWidgets.QCompleter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_model = AccentInsensitiveProxyModel(self)
        
    def setModel(self, c):
        self.proxy_model.setSourceModel(c)
        super().setModel(self.proxy_model)

    def splitPath(self, path: str | None) -> list[str]:
        self.proxy_model.setFilterText(path or "")
        return [""]

#Search bar + autocompleter that shows the score selected
class ScoreSearchBar(QtWidgets.QLineEdit):
    def __init__(self, parent = None) -> None:
        super(ScoreSearchBar,self).__init__(parent)

        self.setContentsMargins(0,0,0,0)
        self.setPlaceholderText(self.tr("Search score")) #traducir
        #self.textChanged.connect(lambda: self.text_changed.emit(identifier, self.text()))
        
        self.pieces_parsed_names =  []  # List to hold the names for autocompletion

        #Auto Completer
        self.auto_completer = AccentInsensitiveCompleter(self)
        self.auto_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.auto_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        
        self.setCompleter(self.auto_completer)

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self,pieces_parsed_names:list[str]):
        self.pieces_parsed_names =  pieces_parsed_names
        self.auto_completer.setModel(QtCore.QStringListModel(self.pieces_parsed_names))

    def keyPressEvent(self, a0):
        """Override keyPressEvent to handle Enter key."""
        if isinstance(a0, QtGui.QKeyEvent):
            if a0.key() == QtCore.Qt.Key.Key_Enter or a0.key() == QtCore.Qt.Key.Key_Return:
                completer = self.auto_completer
                model = completer.model()
                if completer and model and model.rowCount() > 0:  # Check if there are suggestions
                    # Select the first suggestion
                    completer.setCurrentRow(0)  # First suggestion
                    self.setText(completer.currentCompletion())  # Set text to the first suggestion

            # Call the base class to ensure default event processing
            super().keyPressEvent(a0)