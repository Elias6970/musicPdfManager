from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWebEngineWidgets import  QWebEngineView,QWebEngineSettings
from  classes.files_manage import Dir
from classes.constants import *
from classes.classifier import *
from classes.files_manage import Archive
from gui.abstract_windows import Score_search_bar,Status_console,Pop_up_window
from gui.error_window import Error_window
import os



class Score_classifier_window(QtWidgets.QDialog):
    def __init__(self,pieces_list:list[Dir],update_parted_flag_db_function, parent=None) -> None:
        super().__init__(parent)

        self.classifier = Classifier(pieces_list,update_parted_flag_db_function)

        self.setWindowTitle(self.tr("Score classifier")) #traducir 
        self.init_ui()

        #Open the fiirst page
        self.opener(self.classifier.first_page())
        
        self.exec_()


    #Creates the user interface
    def init_ui(self):
        container_layout = QtWidgets.QVBoxLayout()
        rotate_btns_layout = QtWidgets.QVBoxLayout()
        btns_layout = QtWidgets.QHBoxLayout()
    
        #Menu bar

        help_opt = QtWidgets.QAction(self.tr("Help"),self) #traducir
        help_opt.triggered.connect(self.help_opt_menu)

        menu = QtWidgets.QMenuBar()
        menu.addAction(help_opt)
        container_layout.setMenuBar(menu)


        #Pdf viewer
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True) #type: ignore
        self.web_view.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True) #type: ignore
        
        #Rotate area

        btn_rotate_left = QtWidgets.QPushButton()
        btn_rotate_left.clicked.connect(lambda: self.rotate(-90))
        btn_rotate_left.setToolTip(self.tr("Rotate the pdf 90º to the left"))
        btn_rotate_right = QtWidgets.QPushButton()
        btn_rotate_right.clicked.connect(lambda: self.rotate(90))
        btn_rotate_right.setToolTip(self.tr("Rotate the pdf 90º to the right"))
        
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                img_path = os.path.join(sys._MEIPASS,'data','img') #type: ignore
            else:
                img_path = os.path.join('data','img')
            btn_rotate_left.setIcon(QtGui.QIcon(os.path.join(img_path,'rotate_left.png'))) #traducir
            btn_rotate_right.setIcon(QtGui.QIcon(os.path.join(img_path,'rotate_right.png'))) #traducir
        except Exception:
            pass
        
        self.rotation_cb = QtWidgets.QCheckBox(self.tr("Keep rotation to next scores")) #traducir
        self.rotation_cb.setToolTip(self.tr("If this checkbox is checked the next pdf is going to be rotated the same as the previous")) #traducir
        rotate_btns_horizontal_layout = QtWidgets.QHBoxLayout()
        rotate_btns_horizontal_layout.addWidget(btn_rotate_left)
        rotate_btns_horizontal_layout.addWidget(btn_rotate_right)

        rotate_btns_layout.addWidget(QtWidgets.QLabel(self.tr("Rotate"),alignment=QtCore.Qt.AlignCenter)) #type:ignore #Traducir
        rotate_btns_layout.addWidget(self.rotation_cb)
        rotate_btns_layout.addLayout(rotate_btns_horizontal_layout)
        
        #buttons
        btn_prev = QtWidgets.QPushButton(self.tr("Previous")) #traducir
        btn_prev.clicked.connect(self.previous_btn)       
        btn_next = QtWidgets.QPushButton(self.tr("Continue")) #traducir
        btn_next.clicked.connect(self.continue_btn)
        btn_close = QtWidgets.QPushButton(self.tr("Close")) #traducir
        btn_close.clicked.connect(self.close)
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.returnPressed.connect(btn_next.click) #When you press enter pass to the next page
        btns_layout.addWidget(btn_prev)
        btns_layout.addWidget(btn_next)
        btns_layout.addWidget(btn_close)
        
        #Labels
        self.piece_name_lbl = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.piece_name_lbl.setFont(font)

        instructions_lbl = QtWidgets.QLabel("""(w)general  (g)uion\n(o)boe  (f)lauta  flauti(n)  (r)equinto  (c)larinete  clarinete_ba(j)o\n(s)axo  sa(x)o_tenor  saxo_(b)aritono f(a)got  (t)rompa  f(l)iscorno \ntromp(e)ta  tro(m)bon  bombar(d)ino  (z)bajo  t(u)ba  (p)ercusion""") #traducir
        font.setPointSize(12)
        instructions_lbl.setFont(font)

        self.last_classfied_lbl = QtWidgets.QLabel()

        #Add widgets
        container_layout.addWidget(self.piece_name_lbl)
        container_layout.addWidget(self.web_view)
        container_layout.addLayout(rotate_btns_layout)
        container_layout.addWidget(instructions_lbl)
        container_layout.addWidget(self.line_edit) #Create the text box to input what is the part that you are seing
        container_layout.addWidget(self.last_classfied_lbl)

        container_layout.addLayout(btns_layout)
        #self.setGeometry(0,0,500,400)
        
        self.setLayout(container_layout)


    #Open a file
    def opener(self,path):
        self.web_view.load(QtCore.QUrl.fromLocalFile(path))


    #Is called when you press enter
    def continue_btn(self):
        try:
            self.classifier.classify(self.line_edit.text())
            self.opener(self.classifier.next_page_manager(self.rotation_cb.isChecked()))
            #Set labels
            self.piece_name_lbl.setText(self.classifier.actual_piece_name)
            self.last_classfied_lbl.setText(self.classifier.last_new_name)
        except EmptyInitialInputException:
            Error_window.print_error(ValueError(),self.tr("Empty initial input"))
            return
        except ValueError as e:
            Error_window.print_error(e,self.tr("Incorrect input"))
            return
        except NoMorePiecesToClassifyException:
            self.close()

        self.line_edit.clear()

    
    def previous_btn(self):
        try:
            self.opener(self.classifier.previous_page_manager())
        except FirstPageException:
            Error_window.print_error(self.tr("You are in the first page, you can't go to a previous one")) #TRADUCIR


    def rotate(self,degrees):
        self.classifier.rotate(degrees)
        self.opener(self.classifier.last_temp_file_path)

    #Opens a pop up window with the instructions
    def help_opt_menu(self):
        Pop_up_window(INSTRUCTIONS_SCORE_CLASSIFIER,True,self)
    
    def close(self):
        self.hide()

    #For testing
    """def state(self):
        print("Actual piece index: ",self.classifier.actual_piece)
        print("Actual pdf number: ",self.classifier.pdf_controller.actual_pdf_number)
        print("Actual pdf page: ", self.classifier.pdf_controller.get_actual_pdf().actual_pdf_page)"""
    








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
        
        self.search_bar = Score_search_bar(self.archive.pieces.get_parsed_names(),self.validate_selection) #type: ignore
        self.status_area = Status_console()
        
        #Butons
        btn_layout = QtWidgets.QHBoxLayout()

        add_btn = QtWidgets.QPushButton(self.tr("Add")) #traducir
        classify_btn = QtWidgets.QPushButton(self.tr("Classify")) #traducir
        close_btn = QtWidgets.QPushButton(self.tr("Close")) #traducir
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
        error_classified:list[str] = [] #This list is of pieces that are already classified
        for i in self.pieces_to_classify:
            if self.archive.db.is_parted(str(Archive.extract_cod(i))):
                error_classified.append(i)
            else:
                to_classify.append(Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),i)))
        
        if not error_classified == "":
            for i in error_classified:
                answer = Pop_up_window(i + self.tr(" is already splited,\n")+self.tr("do you want to redo it? "),False,self) #traducir
                if answer.btn_confirm_pressed == True:
                    to_classify.append(Dir(os.path.join(RELATIVE_ARCHIVE_PATH(),i)))

        if len(to_classify) > 0:
            try:
                Score_classifier_window(to_classify,self.archive.db.update_parted)
            except PdfNotFoundException as e:
                Error_window.print_error(e,self.tr("The piece doesn't have any pdf")) #traducir
        else:
            Error_window.print_error(self.tr("Any score to classify")) #traducir
        
        self.close()

    def close(self):
        self.hide()
