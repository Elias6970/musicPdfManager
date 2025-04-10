from PyQt6 import QtWidgets,QtCore,QtGui
from  classes.files_management.dir import Dir
from classes.constants.constants import *
from classes.error import EmptyInitialInputException,FirstPageException,NoMorePiecesToClassifyException
from classes.classifier.text_analizer import TextAnalizer
from classes.classifier.classifier import Classifier
from classes.interactive_preview_conversor import InterctivePreviewConversor
from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.error_window import Error_window
from gui.interactive_previewer.interactive_previewer import InteractivePreviewer


#Throw StopClassifyingException if the classification doesn't finish
class ScoreClassifierWindow(QtWidgets.QDialog):
    def __init__(self,pieces_list:list[Dir],update_parted_flag_db_function, parent=None) -> None:
        super().__init__(parent)

        self.classifier = Classifier(pieces_list,update_parted_flag_db_function)

        self.setWindowTitle(self.tr("Score classifier")) #traducir 
        self.init_ui()

        #Open the fiirst page
        self.opener(self.classifier.first_page())
        self.piece_name_lbl.setText(self.classifier.actual_piece_name)

        self.exec()


    #Creates the user interface
    def init_ui(self):
        container_layout = QtWidgets.QVBoxLayout()
        rotate_btns_layout = QtWidgets.QVBoxLayout()
        btns_layout = QtWidgets.QHBoxLayout()
    
        #Menu bar
        help_opt = QtGui.QAction(self.tr("Help"),self) #traducir
        help_opt.triggered.connect(self.help_opt_menu)

        menu = QtWidgets.QMenuBar()
        menu.addAction(help_opt)
        container_layout.setMenuBar(menu)


        #Pdf viewer
        self.view = InteractivePreviewer()


        #Rotate area
        btn_rotate_left = QtWidgets.QPushButton()
        btn_rotate_left.clicked.connect(lambda: self.rotate(-90))
        btn_rotate_left.setToolTip(self.tr("Rotate the pdf 90º to the left"))
        btn_rotate_left.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        btn_rotate_right = QtWidgets.QPushButton()
        btn_rotate_right.clicked.connect(lambda: self.rotate(90))
        btn_rotate_right.setToolTip(self.tr("Rotate the pdf 90º to the right"))
        btn_rotate_right.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        
        try:
            btn_rotate_left.setIcon(QtGui.QIcon(ROTATE_L_IMG_PATH)) #traducir
            btn_rotate_right.setIcon(QtGui.QIcon(ROTATE_R_IMG_PATH)) #traducir
        except Exception:
            pass
        
        self.rotation_cb = QtWidgets.QCheckBox(self.tr("Keep rotation to next scores")) #traducir
        self.rotation_cb.setToolTip(self.tr("If this checkbox is checked the next pdf page is going to be rotated like the previous")) #traducir
        self.rotation_cb.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        rotate_btns_horizontal_layout = QtWidgets.QHBoxLayout()
        rotate_btns_horizontal_layout.addWidget(btn_rotate_left)
        rotate_btns_horizontal_layout.addWidget(btn_rotate_right)

        rotate_btns_layout.addWidget(self.rotation_cb)
        rotate_btns_layout.addLayout(rotate_btns_horizontal_layout)
        
        #buttons
        btn_prev = QtWidgets.QPushButton(self.tr("Previous")) #traducir
        btn_prev.clicked.connect(self.previous_btn)      
        btn_prev.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus) 
        btn_next = QtWidgets.QPushButton(self.tr("Continue")) #traducir
        btn_next.clicked.connect(self.continue_btn)
        btn_close = QtWidgets.QPushButton(self.tr("Close")) #traducir
        btn_close.clicked.connect(self.close)
        btn_close.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        btns_layout.addWidget(btn_prev)
        btns_layout.addWidget(btn_next)
        btns_layout.addWidget(btn_close)
        
        #Labels
        self.piece_name_lbl = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.piece_name_lbl.setFont(font)

        instructions_lbl = QtWidgets.QLabel("""(w)general  (g)uion (cp)clarinete principal\n(o)boe  (f)lauta  flauti(n)  (r)equinto  (c)larinete  clarinete_ba(j)o\n(s)axo  sa(x)o_tenor  saxo_(b)aritono f(a)got  (t)rompa  f(l)iscorno \ntromp(e)ta  tro(m)bon  bombar(d)ino  (z)bajo  t(u)ba  (p)ercusion""") #traducir
        font.setPointSize(12)
        instructions_lbl.setFont(font)

        #Last classified
        self.last_classfied_lbl = QtWidgets.QLabel()
        self.last_classfied_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.last_classfied_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        last_classfied_fixed_txt = QtWidgets.QLabel(self.tr("Last Name: ")) #traducir
        last_classfied_fixed_txt.setFont(font)
        last_classfied_fixed_txt.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        last_classfied_fixed_txt.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)


        last_classfied_h_layout = QtWidgets.QHBoxLayout()
        last_classfied_h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        last_classfied_h_layout.addWidget(last_classfied_fixed_txt)
        last_classfied_h_layout.addWidget(self.last_classfied_lbl)


        #Writing line and instrument interpreter
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.returnPressed.connect(btn_next.click) #When you press enter pass to the next page
        self.line_edit.textChanged.connect(lambda: self.update_real_time_interpreted_txt(self.line_edit.text()))

        self.interpreted_instrument_lbl = QtWidgets.QLabel()
        self.interpreted_instrument_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        writing_line_h_layout = QtWidgets.QHBoxLayout()
        writing_line_h_layout.addWidget(self.line_edit,3)
        writing_line_h_layout.addWidget(self.interpreted_instrument_lbl,1)

        #Add widgets
        container_layout.addWidget(self.piece_name_lbl)
        container_layout.addWidget(self.view)
        container_layout.addLayout(rotate_btns_layout)
        container_layout.addWidget(instructions_lbl)
        container_layout.addLayout(writing_line_h_layout)
        container_layout.addLayout(last_classfied_h_layout)

        container_layout.addLayout(btns_layout)
        #self.setGeometry(0,0,500,400)

        self.setLayout(container_layout)


    #Open a file
    def opener(self,path):
        self.view.load_img(InterctivePreviewConversor.pdf_to_qpixmap(path),
                           InterctivePreviewConversor.get_pdf_rect(path))


    #Is called when you press enter
    def continue_btn(self):
        try:
            self.classifier.classify(self.line_edit.text(),self.view.get_rectangle_selection())
            self.opener(self.classifier.next_page_manager(self.rotation_cb.isChecked()))
            #Set labels
            self.piece_name_lbl.setText(self.classifier.actual_piece_name)
            self.last_classfied_lbl.setText(self.classifier.last_new_name)
        except EmptyInitialInputException:
            Error_window.print_error(ValueError(),self.tr("The first time the input can't be empty"))
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

    #Update the in real time QLabel interpreted text
    def update_real_time_interpreted_txt(self,text:str):
        #Last classified
        if text == "" or text == " ":
            self.interpreted_instrument_lbl.setText(self.classifier.last_new_name)
        else:
            try:
                txt = TextAnalizer.analize(text)
                self.interpreted_instrument_lbl.setText(txt)
            except ValueError as e:
                self.interpreted_instrument_lbl.setText(self.tr(str(e)))


    #Opens a pop up window with the instructions
    def help_opt_menu(self):
        YesNoWindow(INSTRUCTIONS_SCORE_CLASSIFIER,True,self)
    
    def close(self):
        self.hide()
        exit(0)


    def closeEvent(self,event):
        event.accept()
        exit(0)

    #For testing
    """def state(self):
        print("Actual piece index: ",self.classifier.actual_piece)
        print("Actual pdf number: ",self.classifier.pdf_controller.actual_pdf_number)
        print("Actual pdf page: ", self.classifier.pdf_controller.get_actual_pdf().actual_pdf_page)"""
    
