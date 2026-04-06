from PyQt6 import QtWidgets,QtCore

#Search bar + autocompleter that shows the score selected
class ScoreSearchBar(QtWidgets.QLineEdit):
    def __init__(self, parent = None) -> None:
        super(ScoreSearchBar,self).__init__(parent)

        self.setContentsMargins(0,0,0,0)
        self.setPlaceholderText(self.tr("Search score")) #traducir
        #self.textChanged.connect(lambda: self.text_changed.emit(identifier, self.text()))
        
        self.pieces_parsed_names =  []  # List to hold the names for autocompletion

        #Auto Completer
        self.auto_completer = QtWidgets.QCompleter(self.pieces_parsed_names)
        self.auto_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.auto_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        
        self.setCompleter(self.auto_completer)

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self,pieces_parsed_names:list[str]):
        self.pieces_parsed_names =  pieces_parsed_names
        self.auto_completer.setModel(QtCore.QStringListModel(self.pieces_parsed_names))

    def keyPressEvent(self, event):
        """Override keyPressEvent to handle Enter key."""
        if event.key() == QtCore.Qt.Key.Key_Enter or event.key() == QtCore.Qt.Key.Key_Return:
            completer = self.auto_completer
            
            if completer and completer.model().rowCount() > 0:  # Check if there are suggestions
                # Select the first suggestion
                completer.setCurrentRow(0)  # First suggestion
                self.setText(completer.currentCompletion())  # Set text to the first suggestion

        # Call the base class to ensure default event processing
        super().keyPressEvent(event)