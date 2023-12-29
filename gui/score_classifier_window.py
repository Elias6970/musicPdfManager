from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWebEngineWidgets import  QWebEngineView,QWebEngineSettings
from  classes.files_manage import Dir
from classes.constants import *
from classes.classifier import *
from classes.files_manage import Archive
from gui.abstract_windows import Score_search_bar,Status_console,Pop_up_window
from gui.error_window import Error_window
import PyPDF2,tempfile,os



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
        
        #Menu bar

        help_opt = QtWidgets.QAction("Help",self) #traducir
        help_opt.triggered.connect(self.help_opt_menu)

        menu = QtWidgets.QMenuBar()
        menu.addAction(help_opt)
        container_layout.setMenuBar(menu)


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

        instructions_lbl = QtWidgets.QLabel("""(w)general  (g)uion\n(o)boe  (f)lauta  flauti(n)  (r)equinto  (c)larinete  clarinete_ba(j)o\n(s)axo  sa(x)o_tenor  saxo_(b)aritono f(a)got  (t)rompa  f(l)iscorno \ntromp(e)ta  tro(m)bon  bombar(d)ino  (n)bajo  t(u)ba  (p)ercusion""") #traducir
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
            Error_window.print_error(ValueError(),"Empty initial input")
            return
        if self.line_edit.text() == "":
            input_analized = self.last_new_name
        else:
            try:
                input_analized = Text_analizer.analize(self.line_edit.text())
                self.last_new_name = input_analized
            except ValueError as e:
                Error_window.print_error(e,"Incorrect input")
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
            #Update the parted flag to 1 in the db
            self.update_parted_flag_db_function(Archive.extract_cod(self.pieces_list[self.actual_piece].name),True)
            self.pdf_controller.export()

            self.close()
            
        self.line_edit.clear()

    #Opens a pop up window with the instructions
    def help_opt_menu(self):
        Pop_up_window(INSTRUCTIONS_SCORE_CLASSIFIER,True,self)
    
    def close(self):
        self.hide()



#Window to select the pieces to classify with the score_classifier tool:
#   pieces_in_dirs: list of Dir objects with the pieces in the file system archive
#   update_parted_flag_db_function: pointer to the function that update the flag 
#           parted in the db. This function is used in the score_classifier_window
class Piece_selector_to_classify_window(QtWidgets.QDialog):
    def __init__(self,archive:Archive,parent=None) -> None:
        super().__init__(parent)
        
        self.pieces_to_classify:list[str] = []
        self.archive = archive
        

        #Gui
        container_layout = QtWidgets.QVBoxLayout()
        
        self.search_bar = Score_search_bar(self.archive.pieces_in_dirs,self.validate_selection)
        self.status_area = Status_console()
        
        #Butons
        btn_layout = QtWidgets.QHBoxLayout()

        add_btn = QtWidgets.QPushButton("Add") #traducir
        classify_btn = QtWidgets.QPushButton("Classify") #traducir
        close_btn = QtWidgets.QPushButton("Close") #traducir
        add_btn.clicked.connect(self.btn_add)
        classify_btn.clicked.connect(self.btn_classify)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(classify_btn)
        btn_layout.addWidget(close_btn)

        container_layout.addWidget(self.search_bar)
        container_layout.addLayout(btn_layout)
        container_layout.addWidget(self.status_area)
        
        self.setLayout(container_layout)

        self.exec_()


    #Check if the piece selected is equals to one on the list
    def validate_selection(self,text):
        for i in self.search_bar.pieces_names:
            if text == i:
                return True
        return False
    

    def btn_add(self):
        if self.validate_selection(self.search_bar.text()):
            self.status_area.add_lbl(QtWidgets.QLabel(self.search_bar.text()))
            self.pieces_to_classify.append(self.search_bar.text())

            self.search_bar.clear()


    #Button that opens the classify window.
    #   This function checks if the pieces have the parted flag = 1 in the db
    def btn_classify(self):
        to_classify:list[Dir] = [] 
        error_classified:str = "" #This list is of pieces that are already classified
        for i in self.pieces_to_classify:
            if self.archive.is_parted(str(Archive.extract_cod(i))):
                error_classified += i+"\n"
            else:
                to_classify.append(Dir(os.path.join(RELATIVE_ARCHIVE_PATH,i)))
        
        if not error_classified == "":
            Pop_up_window(error_classified+"\n Were already split ",True,self) #traducir
        
        if len(to_classify) > 0:
            print(to_classify[0].scores)
            try:
                Score_classifier_window(to_classify,self.archive.update_parted)
            except PdfNotFoundException as e:
                Error_window.print_error(e,"The piece doesn't have any pdf") #traducir
        else:
            Error_window.print_error("Any score to classify") #traducir
        
        self.hide()

    def close(self):
        self.hide()
