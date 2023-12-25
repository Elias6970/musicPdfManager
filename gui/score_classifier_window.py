from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWebEngineWidgets import  QWebEngineView,QWebEngineSettings
import sys
from  classes.files_manage import Dir
from classes.constants import *
from classes.classifier import *
from classes.files_manage import Archive
from gui.error_window import Error
import PyPDF2,tempfile,os,shutil
from typing import List,Tuple

#TODO: falta todo lo de abrir pdfs

class Score_classifier_window(QtWidgets.QDialog):
    actual_piece:int = -1#is the number of the piece in peices_list
    last_temp_file_path:str
    last_new_name:str = ""

    def __init__(self,pieces_list:list[Dir],update_parted_flag_db_function, parent=None) -> None:
        super().__init__(parent)

        self.pieces_list = pieces_list
        self.update_parted_flag_db_function = update_parted_flag_db_function

        self.setWindowTitle("Score classifier") #traducir 
        self.init_ui()

        #Classifer manage
        self.next_piece()
        
        self.exec_()


    #Creates the user interface
    def init_ui(self):
        container_layout = QtWidgets.QVBoxLayout()
        btns_layout = QtWidgets.QHBoxLayout()

        #Pdf viewer
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True) #type: ignore
        self.web_view.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True) #type: ignore

        #buttons
        btn_next = QtWidgets.QPushButton("Continue") #traducir
        btn_next.clicked.connect(self.continue_btn)
        btn_close = QtWidgets.QPushButton("Close") #traducir
        btn_close.clicked.connect(self.close)
        self.line_edit = QtWidgets.QLineEdit()
        btns_layout.addWidget(btn_next)
        btns_layout.addWidget(btn_close)
        
        #Label
        self.score_lbl = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.score_lbl.setFont(font)

        instructions_lbl = QtWidgets.QLabel("""(w)general  (g)uion\n(o)boe  (f)lauta  flauti(n)  (r)equinto  (c)larinete  clarinete_ba(j)o\n(s)axo  sa(x)o_tenor  saxo_(b)aritono f(a)got  (t)rompa  f(l)iscorno \ntromp(e)ta  tro(m)bon  bombar(d)ino  (d)bajo  t(u)ba  (p)ercusion""") #traducir
        font.setPointSize(12)
        instructions_lbl.setFont(font)

        #Add widgets
        container_layout.addWidget(self.score_lbl)
        container_layout.addWidget(self.web_view)
        container_layout.addWidget(instructions_lbl)
        container_layout.addWidget(self.line_edit) #Create the text box to input what is the part that you are seing
        
        container_layout.addLayout(btns_layout)
        #self.setGeometry(0,0,500,400)
        
        self.setLayout(container_layout)


    #Open a file
    def opener(self,path):
        self.web_view.load(QtCore.QUrl.fromLocalFile(path))


    #Generates a temp file path
    def generate_temp(self) -> str:
        path = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        self.last_temp_file_path = path
        return path
    
    #Pass the page to the next one
    def next_page(self):
        temp_path = self.generate_temp()
        reader = PyPDF2.PdfReader(self.pdf_controller.get_actual_pdf().path)
        writer = PyPDF2.PdfWriter()
        writer.add_page(reader.pages[self.pdf_controller.get_actual_pdf().actual_pdf_page])
        writer.write(temp_path)

        self.opener(temp_path)


    #Jump to the next piece
    def next_piece(self):
        self.actual_piece += 1
        self.pdf_controller = Pdf_controller(self.pieces_list[self.actual_piece])
        self.score_lbl.setText(os.path.basename(self.pieces_list[self.actual_piece].path))
        self.next_page()

    #Is called when you press enter
    def continue_btn(self):
        if self.line_edit.text() == "" and self.last_new_name == "":
            Error.print_error(ValueError(),"Empty initial input")
            return
        if self.line_edit.text() == "":
            input_analized = self.last_new_name
        else:
            try:
                input_analized = Text_analizer.analize(self.line_edit.text())
                self.last_new_name = input_analized
            except ValueError as e:
                Error.print_error(e,"Incorrect input")
                return

        self.pdf_controller.get_actual_pdf().add_pdf_page(self.last_temp_file_path,input_analized)

        self.pdf_controller.get_actual_pdf().actual_pdf_page += 1

        if self.pdf_controller.get_actual_pdf().actual_pdf_page < self.pdf_controller.get_actual_pdf().num_pages:
            self.next_page()
        
        elif self.pdf_controller.actual_pdf_number+1 < len(self.pdf_controller.pdfs):
            self.pdf_controller.actual_pdf_number += 1
            self.next_page()
        
        elif self.actual_piece+1 < len(self.pieces_list):
            #Update the parted flag to 1 in the db
            self.update_parted_flag_db_function(Archive.extract_cod(self.pieces_list[self.actual_piece].name),True)
            
            self.pdf_controller.export()
            self.next_piece()
        else:
            self.pdf_controller.export()

            self.close()
            
        self.line_edit.clear()


    def close(self):
        self.hide()
        exit(0)
