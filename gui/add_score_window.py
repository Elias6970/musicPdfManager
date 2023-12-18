
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget
import shutil,os
from classes.score import Score
from classes.files_manage import Archive,File
from classes.constants import RELATIVE_ARCHIVE_PATH,DIR_EXTRAS,DIR_SCORES
from classes.error import Error


class Add_score_window(QtWidgets.QDialog):
    def __init__(self,archive:Archive,parent=None):
        super(Add_score_window,self).__init__(parent=parent)
        
        self.setWindowTitle("Add new score") #traducir

        self.archive = archive
        self.next_cod = self.archive.get_next_cod()

        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addLayout(self.create_fields_layout(self.next_cod))
        container_layout.addLayout(self.create_checkbox_layout(["handwritten","digitalized"]))
        container_layout.addLayout(self.create_buttons_layout())
        

        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        self.exec_()

    def update_next_cod(self):
        pass
    #Create the fields layout that is returned and added as a layout(not as a widget)
    def create_fields_layout(self,next_cod):
        fields_layout = QtWidgets.QVBoxLayout()

        
        self.line_cod = QtWidgets.QLineEdit()
        #self.line_cod.setPlaceholderText(f"next in the archive will be: {next_cod}") #traducir
        self.line_cod.setText(str(next_cod))
        self.line_name = QtWidgets.QLineEdit()
        self.line_author = QtWidgets.QLineEdit()
        self.line_type = QtWidgets.QLineEdit()

        
        cod_layout = QtWidgets.QHBoxLayout()
        cod_layout.addWidget(QtWidgets.QLabel("Cod  ")) #traducir
        cod_layout.addWidget(self.line_cod)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(QtWidgets.QLabel("Name *  ")) #traducir
        name_layout.addWidget(self.line_name)

        author_layout = QtWidgets.QHBoxLayout()
        author_layout.addWidget(QtWidgets.QLabel("Author  ")) #traducir
        author_layout.addWidget(self.line_author)
        
        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel("Type  ")) #traducir
        type_layout.addWidget(self.line_type)

        fields_layout.addLayout(cod_layout)
        fields_layout.addLayout(name_layout)
        fields_layout.addLayout(author_layout)
        fields_layout.addLayout(type_layout)

        return fields_layout
    

    """#Create the checkboxes handwritten,parted and digitalized
    def create_checkbox_layout(self):
        layout = QtWidgets.QHBoxLayout()

        self.handwritten_cbox = QtWidgets.QCheckBox("Handwritten") #traducir
        

        self.handwritten_cbox.setToolTip("You must check this checkbox if the score is handwritten")#traducir
        
        layout.setAlignment(QtCore.Qt.AlignLeft) #type: ignore
        layout.addWidget(self.handwritten_cbox)

        return layout
    """
        #Create the checkboxes handwritten,parted and digitalized
    def create_checkbox_layout(self,names:list[str]):
        self.checkboxes_dict:dict = {}
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft) #type: ignore

        for i in names:
            self.checkboxes_dict[i] = QtWidgets.QCheckBox(i)
            layout.addWidget(self.checkboxes_dict[i])
            #self.checkboxes_dict.setToolTip("You must check this checkbox if the score is handwritten")#traducir
        
        return layout
    
    #Create the buttons layout
    def create_buttons_layout(self):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        add_btn = QtWidgets.QPushButton("Add") #traducir

        close_btn.clicked.connect(self.close)
        add_btn.clicked.connect(self.add_score)
        
        btns_layout.addWidget(add_btn)
        btns_layout.addWidget(close_btn)
        
        return btns_layout
    
    def add_score(self):
        cod = self.line_cod.text()
        name = self.line_name.text()
        parsed_name = Archive.get_parsed_name(cod,name)
        
        if self.verifications(cod,name):
            
            #Open a dialog to select the files to be putted in the directory
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)  # Allow selecting any file type
            file_dialog.setWindowTitle("Select a folder or a file") #traducir
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)  # Set the dialog to save mode


            
            
            if file_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
                Archive.make_dir(RELATIVE_ARCHIVE_PATH,parsed_name)
                
                if self.move_files(parsed_name,file_dialog.selectedFiles()) and self.archive.insert(int(cod),name,self.line_author.text(),self.line_type.text(),handwritten=int(self.handwritten_cbox.isChecked()),parted=0):
                    self.alert_import(parsed_name,True)
                    self.reset_fields()
                else:
                    self.alert_import(parsed_name,False)
                
                



    #Check if the input adding the score is correct 
    def verifications(self,cod,name:str):
        try:
            checked_cod = self.archive.get_with_equals("cod",cod,"cod") #Check if the cod is in the db
            
            if checked_cod == [] and len(name.strip()) != 0:
                    name_matches = self.archive.get_with_like("name",name,"cod,name")
                    
                    
                    if name_matches != []:
                        warning_text = "This score is called something like these:\n" #traducir
                        for i in name_matches:
                            warning_text = warning_text + Archive.get_parsed_name(i[0],i[1]) + "\n"
                        
                        #Pop up the scores matched
                        warning_window = Pop_up_window(warning_text,self)
                        warning_window.exec_()
                    
                    try:
                        return warning_window.btn_yes_pressed #type:ignore
                    except UnboundLocalError as e: #if the pop up warning is not being showed(not similar names)
                        return True
            else:
                alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"Warning","Already exists a score with this cod or \nname can't be empty",QtWidgets.QMessageBox.Ok,self) #traducir
                alert.exec_()
            

        except Exception as e:
            Error.print_error(e)
            #print("Error: ",type(e),e)
        
        return False

    #Move the files to the internal archive deppending if there are scores or extras
    def move_files(self,score_path,files):
        try:
            for i in files:
                if File.is_pdf(i):
                    shutil.copy(i,os.path.join(RELATIVE_ARCHIVE_PATH,score_path,DIR_SCORES,os.path.basename(i)))
                else:
                    shutil.copy(i,os.path.join(RELATIVE_ARCHIVE_PATH,score_path,DIR_EXTRAS,os.path.basename(i)))
            return True
        
        except Exception as e:
            Error.print_error(e)
            #print("Error: ",type(e),e)
        
        return False

    #Show a pop up when the import is correct
    def alert_import(self,score:str,correct:bool):
        if correct:
            alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"","{} has been correctly imported".format(score),QtWidgets.QMessageBox.Ok,self) #traducir
        else:
            alert = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon,"","There has been an error importing {}".format(score),QtWidgets.QMessageBox.Ok,self) #traducir
        alert.exec_()

    #Clear the text in all the fiels
    def reset_fields(self):
        self.line_cod.setText(str(self.archive.get_next_cod()))
        self.line_name.clear()
        self.line_author.clear()
        self.line_type.clear()

        
    def close(self):
        print(self.checkboxes_dict["handwritten"].isChecked()," ",self.checkboxes_dict["digitalized"].isChecked())
        self.hide()


#Pop up a window that shows a message with yes,no buttons
class Pop_up_window(QtWidgets.QDialog):
    def __init__(self,text:str,parent: QWidget) -> None:
        super(Pop_up_window,self).__init__(parent)

        self.btn_yes_pressed = False #This values become true when no button is pressed

        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()

        #labels
        warning_lbl = QtWidgets.QLabel(text)
        confirmation_lbl = QtWidgets.QLabel("Do you want to keep adding it?")#traducir
        
        #signals to comunicate with the class that call this class
        self.yes_btn_clicked = QtCore.pyqtSignal()
        self.no_btn_clicked = QtCore.pyqtSignal()

        #Two buttons
        btn_layout = QtWidgets.QHBoxLayout()
        yes_btn = QtWidgets.QPushButton("Yes") #traducir
        no_btn = QtWidgets.QPushButton("No") #traducir
        yes_btn.clicked.connect(self.yes)
        no_btn.clicked.connect(self.no)
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)

        
        container_layout.addWidget(warning_lbl)
        container_layout.addWidget(confirmation_lbl)
        container_layout.addLayout(btn_layout)


        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

    def yes(self):
        self.btn_yes_pressed = True
        self.hide()
    
    def no(self):
        self.hide()
