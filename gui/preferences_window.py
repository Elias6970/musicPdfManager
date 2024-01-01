import sys
from PyQt5 import QtWidgets,QtCore
from classes.config import Configuration,Configuration_setter
from gui.abstract_windows import Pop_up_window

#Window to set the paths of the archive and the cover to export the list of pieces
class Preferences_window(QtWidgets.QDialog):
    def __init__(self,first_time:bool,parent=None):
        super(Preferences_window,self).__init__(parent)  
        self.setWindowTitle("Preferences") #traducir

        self.first_time = first_time

        self.init_ui()
        self.set_field_value()

        self.exec_()

    def init_ui(self):
        container_layout = QtWidgets.QVBoxLayout()

        #Fields
        fields_layout = QtWidgets.QVBoxLayout()

        self.line_archive_path = QtWidgets.QLineEdit()
        self.line_cover_path = QtWidgets.QLineEdit()


        #Browse Buttons
        archive_path_layout = QtWidgets.QHBoxLayout()
        archive_path_btn = QtWidgets.QPushButton("Browse") #traducir
        archive_path_btn.clicked.connect(lambda: self.browse("archive"))

        archive_path_layout.addWidget(QtWidgets.QLabel("Archive path  *")) #traducir
        archive_path_layout.addWidget(self.line_archive_path)
        archive_path_layout.addWidget(archive_path_btn)

        #Browse Buttons
        cover_path_btn = QtWidgets.QPushButton("Browse") #traducir
        cover_path_btn.clicked.connect(lambda: self.browse("cover"))

        cover_path_layout = QtWidgets.QHBoxLayout()
        cover_path_layout.addWidget(QtWidgets.QLabel("Dossier cover path  ")) #traducir
        cover_path_layout.addWidget(self.line_cover_path)
        cover_path_layout.addWidget(cover_path_btn)

        fields_layout.addLayout(archive_path_layout)
        fields_layout.addLayout(cover_path_layout)

        #Buttons
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        save_btn = QtWidgets.QPushButton("Save & Exit") #traducir

        close_btn.clicked.connect(self.close)
        save_btn.clicked.connect(self.save)
        
        btns_layout.addWidget(save_btn)
        btns_layout.addWidget(close_btn)
        
        #Add Layouts
        container_layout.addLayout(fields_layout)
        container_layout.addLayout(btns_layout)

        self.setLayout(container_layout)
    

    #Set the value that have 
    def set_field_value(self):
        self.line_archive_path.setText(Configuration.get_archive_path())
        self.line_cover_path.setText(Configuration.get_dossier_cover())

    
    #Appear a file dialog to select a file or a folder. This path is saved in the correct field.
    #Two buttons use the same function
    def browse(self,type:str):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setWindowTitle("Select a folder") #traducir
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)  # Set the dialog to save mode
        
        
        if type == "archive":
            file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)  # Allow selecting any file type
            if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
                self.line_archive_path.setText(file_dialog.selectedFiles()[0])

        else:
            file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)  # Allow selecting any file type
            if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
                self.line_cover_path.setText(file_dialog.selectedFiles()[0])


    def save(self):
        Configuration_setter.export_paths(self.line_archive_path.text(),self.line_cover_path.text())
        Pop_up_window("Changes saved succesfully",True,self) #translate
        self.hide()
    

    def close(self):
        if self.first_time:
            sys.exit()
        self.hide()