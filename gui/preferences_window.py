import sys,os
from PyQt6 import QtWidgets,QtCore
from classes.config import Configuration
from gui.abstract_windows import Pop_up_window
from gui.error_window import Error_window

#Window to set the paths of the archive and the cover to export the list of pieces
class Preferences_window(QtWidgets.QDialog):
    def __init__(self,first_time:bool,parent=None):
        super(Preferences_window,self).__init__(parent)  
        self.setWindowTitle(self.tr("Preferences")) #traducir

        self.first_time = first_time

        self.init_ui()
        self.set_field_value()

        self.exec()

    def init_ui(self):
        container_layout = QtWidgets.QVBoxLayout()

        #Fields
        fields_layout = QtWidgets.QVBoxLayout()

        self.line_archive_path = QtWidgets.QLineEdit()
        self.line_cover_path = QtWidgets.QLineEdit()


        #Browse Buttons
        archive_path_layout = QtWidgets.QHBoxLayout()
        archive_path_layout.setSpacing(0)
        archive_path_btn = QtWidgets.QPushButton(self.tr("Browse")) #traducir
        archive_path_btn.clicked.connect(lambda: self.browse("archive"))

        archive_path_layout.addWidget(QtWidgets.QLabel(self.tr("Archive path  *"))) #traducir
        archive_path_layout.addWidget(self.line_archive_path)
        archive_path_layout.addWidget(archive_path_btn)
        
        #Browse Buttons
        cover_path_btn = QtWidgets.QPushButton(self.tr("Browse")) #traducir
        cover_path_btn.clicked.connect(lambda: self.browse("cover"))

        cover_path_layout = QtWidgets.QHBoxLayout()
        cover_path_layout.setSpacing(0)
        cover_path_layout.addWidget(QtWidgets.QLabel(self.tr("Dossier cover path (.pdf)")+ "\n" + self.tr("(Don't touch pls)  "))) #traducir
        cover_path_layout.addWidget(self.line_cover_path)
        cover_path_layout.addWidget(cover_path_btn)
        
        fields_layout.addLayout(archive_path_layout)
        fields_layout.addLayout(cover_path_layout)

        #Save and close Buttons
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton(self.tr("Close")) #traducir
        save_btn = QtWidgets.QPushButton(self.tr("Save and Exit")) #traducir

        close_btn.clicked.connect(self.close)
        save_btn.clicked.connect(self.save)
        
        btns_layout.addWidget(save_btn)
        btns_layout.addWidget(close_btn)
        

        #Language Combobox
        language_layout = QtWidgets.QHBoxLayout()
        language_layout.setSpacing(0)
        self.language_combobox = QtWidgets.QComboBox()
        self.language_combobox.addItems(["Espanol","English","Valencià"])

        language_layout.addWidget(QtWidgets.QLabel(self.tr("Language")))
        language_layout.addWidget(self.language_combobox)
        


        container_layout.addLayout(fields_layout)
        container_layout.addLayout(language_layout)
        container_layout.addLayout(btns_layout)

        container_layout.setSpacing(20)
        self.setLayout(container_layout)
    

    #Set the value that have 
    def set_field_value(self):
        self.line_archive_path.setText(Configuration.get_archive_path())
        self.line_cover_path.setText(Configuration.get_dossier_cover_path())
        self.language_combobox.setCurrentText(Configuration.get_language())
    
    #Appear a file dialog to select a file or a folder. This path is saved in the correct field.
    #Two buttons use the same function
    def browse(self,type:str):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setWindowTitle(self.tr("Select a folder")) #traducir
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptOpen)  # Set the dialog to save mode
        
        
        if type == "archive":
            file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)  # Allow selecting any file type
            if file_dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
                self.line_archive_path.setText(file_dialog.selectedFiles()[0])

        else:
            file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)  # Allow selecting any file type
            if file_dialog.exec() == QtWidgets.QFileDialog.DialogCode.Accepted:
                self.line_cover_path.setText(file_dialog.selectedFiles()[0])


    def save(self):
        try:
            Configuration.save_config(self.line_archive_path.text(),self.line_cover_path.text(),Configuration.name_to_cod_language(self.language_combobox.currentText()))
            Pop_up_window(self.tr("Changes saved succesfully")+"\n"+self.tr("If you have changed the language you need to restart the app"),True,self) #translate
        
        except Exception as e:
            Error_window.print_error(e,"Error saving the changes")
        self.hide()
    

    def close(self):
        if self.first_time:
            sys.exit()
        self.hide()