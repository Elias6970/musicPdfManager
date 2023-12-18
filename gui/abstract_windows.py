from PyQt5 import QtCore, QtWidgets
import os,shutil
from classes.files_manage import Archive,File,Dir
from classes.error import Error
from classes.constants import RELATIVE_ARCHIVE_PATH,DIR_SCORES,DIR_EXTRAS


#Abstract window that have: (Is a false abstract window but it used like that)
#   a search bar linked to all scores in the archive directory
#   a lbl with the score selected
#   btn1 that you can select the lbl and you set the function
#   cancel btn that exits
class Abstract_serch_bar_and_two_buttons_window(QtWidgets.QDialog):

    def __init__(self,archive:Archive,window_title:str,btn_lbl:str,parent=None):
        super(Abstract_serch_bar_and_two_buttons_window,self).__init__(parent)
        
        self.setWindowTitle(window_title) #traducir

        self.archive = archive
        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore
        
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        
        self.search_bar = Score_search_bar(self.archive.pieces_in_dirs,self.validate_selection)
        self.piece_lbl = QtWidgets.QLabel()
        
        container_layout.addWidget(self.search_bar)
        container_layout.addWidget(self.piece_lbl)
        container_layout.addLayout(self.create_buttons_layout(btn_lbl))
        
        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        self.exec_()

    def create_buttons_layout(self,btn1_lbl:str):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        func_btn = QtWidgets.QPushButton(btn1_lbl) #traducir

        close_btn.clicked.connect(self.close)
        func_btn.clicked.connect(self.btn_function)
        
        btns_layout.addWidget(func_btn)
        btns_layout.addWidget(close_btn)
        
        return btns_layout

    
    #Update the autocompleter list of the search
    def update_autocompleter_scores(self):
        self.archive.update_pieces_in_dirs()
        self.search_bar.update_autocompleter_scores(self.archive.pieces_in_dirs)
    
    
    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        for i in self.search_bar.pieces_names:
            if text == i:
                self.piece_lbl.setText(text)
                return True

    def close(self):
        self.hide()

    #Acts like an abstract method
    def btn_function(self):
        pass


#Abstract class that shows a window with:
#   4 camps to fill(cod,name,author,type)
#   handwritten checkbox
#   A button that you can choose its function
#   Close button
class Abstract_fields_window(QtWidgets.QDialog):
    def __init__(self,archive:Archive,window_title:str,btn_lbl:str,checkboxes_names:list[str],parent=None):
        super(Abstract_fields_window,self).__init__(parent=parent)
        
        self.setWindowTitle(window_title) #traducir

        self.archive = archive
        
        
        self.checkboxes_names = checkboxes_names #names of the checkboxes
        
        self.setWindowModality(QtCore.Qt.WindowModal) #type: ignore

        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addLayout(self.create_fields_layout())
        container_layout.addLayout(self.create_checkboxes_layout(checkboxes_names))
        container_layout.addLayout(self.create_buttons_layout(btn_lbl))
        

        self.setGeometry(0,0,400,200)
        self.setLayout(container_layout)

        self.exec_()


    #Create the fields layout that is returned and added as a layout(not as a widget)
    def create_fields_layout(self):
        fields_layout = QtWidgets.QVBoxLayout()

        
        self.line_cod = QtWidgets.QLineEdit()

        self.line_cod.setText(str(self.archive.get_next_cod()))#cambiar

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
    

    #Create the checkboxes handwritten,parted and digitalized
    def create_checkboxes_layout(self,names:list[str]):
        self.checkboxes_dict:dict = {}
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft) #type: ignore

        for i in names:
            self.checkboxes_dict[i] = QtWidgets.QCheckBox(i)
            layout.addWidget(self.checkboxes_dict[i])
            #self.checkboxes_dict.setToolTip("You must check this checkbox if the score is handwritten")#traducir
        
        return layout


    #Create the buttons layout
    def create_buttons_layout(self,btn_lbl:str):
        btns_layout = QtWidgets.QHBoxLayout()
        close_btn = QtWidgets.QPushButton("Close") #traducir
        add_btn = QtWidgets.QPushButton(btn_lbl) #traducir

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
    #Checks:
    #   if the cod is in the db
    #   if the name is not empty
    #   if its name in in the db --> ONLY APPEAR A WINDOW SHOWING THE NAMES SIMILARS(YOU CAN CHOOSE YES OR NO TO ADD IT)
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
        self.hide()



























#Search bar + autocompleter + label that shows the score selected
class Score_search_bar(QtWidgets.QWidget):
    def __init__(self, pieces_in_dirs:list[Dir],verify_function:callable,parent=None) -> None:
        super(Score_search_bar,self).__init__(parent)

        search_bar_layout = QtWidgets.QVBoxLayout()
        
        #Space
        search_bar_layout.setContentsMargins(0,0,0,0)

        self.piece_search_bar = QtWidgets.QLineEdit()
        self.piece_search_bar.setPlaceholderText("Search score") #traducir
        #self.piece_search_bar.textChanged.connect(lambda: self.validate_selection(self.piece_search_bar.text(),False)) #type: ignore
        self.piece_search_bar.textChanged.connect(lambda: verify_function(self.piece_search_bar.text()))

        self.pieces_names:list[str] = [os.path.basename(i.path) for i in pieces_in_dirs]

        #Auto Completer
        self.completer = QtWidgets.QCompleter(self.pieces_names)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive) #type: ignore
        self.completer.setFilterMode(QtCore.Qt.MatchContains) #type: ignore

        self.piece_search_bar.setCompleter(self.completer)


        search_bar_layout.addWidget(self.piece_search_bar)

        self.setLayout(search_bar_layout)

    #Update the autocompleter list of the search bar
    def update_autocompleter_scores(self,pieces_in_dirs:list[Dir]):
        self.pieces_names = [os.path.basename(i.path) for i in pieces_in_dirs]
        self.completer.setModel(QtCore.QStringListModel(self.pieces_names))


