from PyQt6 import QtWidgets, QtCore

class MassiveImportView(QtWidgets.QDialog):
    import_data_file_signal = QtCore.pyqtSignal()
    import_archive_signal = QtCore.pyqtSignal()
    confirm_signal = QtCore.pyqtSignal()

    """View for the massive import of pieces from a folder. It is used in the CreateArchiveView when the user wants to import a folder as an archive."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Import Archive"))
        self.setModal(True)
        self.resize(400, 200)

        self._layout = QtWidgets.QVBoxLayout(self)

        _data_layout = QtWidgets.QVBoxLayout()
        _data_btn_layout = QtWidgets.QHBoxLayout()
        self.excel_lbl = QtWidgets.QLabel(self.tr("Import the data"))
        self.data_file_button = QtWidgets.QPushButton(self.tr("Select Data File"), self)
        self.data_file_button.setToolTip(self.tr("Select the xls, xlsx or csv file that contains the metadata of the pieces in the archive. The format of the data is |code|title|composer|type"))
        self.data_file_button.clicked.connect(self.import_data_file_signal.emit)
        self.data_file_selcted_lbl = QtWidgets.QLabel(self.tr("No file selected"))
        _data_btn_layout.addWidget(self.excel_lbl)
        _data_btn_layout.addWidget(self.data_file_button)
        _data_layout.addLayout(_data_btn_layout)
        _data_layout.addWidget(self.data_file_selcted_lbl)

        _files_layout = QtWidgets.QVBoxLayout()
        _files_btn_layout = QtWidgets.QHBoxLayout()
        self.import_lbl = QtWidgets.QLabel(self.tr("Import an Archive"), self)
        self.import_button = QtWidgets.QPushButton(self.tr("Select Folder"), self)
        self.import_button.setToolTip(self.tr("Select the folder that contains the pieces to import. Each subfolder will be imported as a piece in the archive. Each subfolder need to start with the code-title of the piece, for example: 01-Piece1, 02-Piece2, etc. The cod is going to be used to link the piece with the data. A folder with no data it is not going to be imported."))
        self.import_button.clicked.connect(self.import_archive_signal.emit)
        self.archive_path_selected_lbl = QtWidgets.QLabel(self.tr("No folder selected"))
        _files_btn_layout.addWidget(self.import_lbl)
        _files_btn_layout.addWidget(self.import_button)
        _files_layout.addLayout(_files_btn_layout)
        _files_layout.addWidget(self.archive_path_selected_lbl)

        self.confirm_button = QtWidgets.QPushButton(self.tr("Confirm"), self)
        self.confirm_button.clicked.connect(self.confirm_signal.emit)

        self.skip_button = QtWidgets.QPushButton(self.tr("Skip"), self)
        self.skip_button.clicked.connect(self.reject)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat(self.tr("Uploading files")+ " ... %p%")
        
        self.processing_lbl = QtWidgets.QLabel(self.tr("Importing the files into the archive... This can take a few minutes. Please wait."), self)
        self.processing_lbl.setVisible(False)
        
        _action_btn_layout = QtWidgets.QHBoxLayout()
        _action_btn_layout.addWidget(self.skip_button)
        _action_btn_layout.addWidget(self.confirm_button)

        self._layout.addLayout(_data_layout)
        self._layout.addLayout(_files_layout)
        self._layout.addLayout(_action_btn_layout)
        self._layout.addWidget(self.progress_bar)
        self._layout.addWidget(self.processing_lbl)

        self.setLayout(self._layout)

    
    def set_progress(self, value: int):
        self.progress_bar.setValue(value)
        if not self.progress_bar.isVisible():
            self.progress_bar.setVisible(True)
    
    def set_finished_uploading(self):
        self.set_progress(100)
        self.processing_lbl.setVisible(True)
    
    def set_data_file_lbl(self, file_name: str):
        self.data_file_selcted_lbl.setText(self.tr("Data file: ") + file_name)
    
    def set_archive_path_lbl(self, folder_path: str):
        self.archive_path_selected_lbl.setText(self.tr("Archive folder: ") + folder_path)