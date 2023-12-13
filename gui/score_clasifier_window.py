from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView

import shutil,tempfile,PyPDF2,os,re
from classes.files_manage import Dir
from classes.constants import RELATIVE_ARCHIVE_PATH,DIR_SCORES,DIR_EXTRAS


#Open the window_clasifier that clasifies one dir
class Clasifier_window(QtWidgets.QDialog):
    actual_page_num:int = 0 #actual num of page in the pdf
    actual_page:tempfile._TemporaryFileWrapper
    actual_pdf:int = 0 #actual num of pdf inside self.dir.scores
    
    temp_and_new_file_paths:list[tuple] = [] #First the temp path and second the new

    def __init__(self,dir:Dir,parent=None) -> None:
        #super(Clasifier_window,self).__init__(parent=parent)
        super(Clasifier_window,self).__init__(parent=parent)

        self.setWindowTitle("Delete score") #traducir

        self.dir = dir
        self.is_closed = False #To be detected as closed out of the class

        self.init_ui()
        
        self.next_pdf_page()
        
        print(os.path.join(self.dir.path,DIR_SCORES,self.dir.scores[0]))
                


        self.exec_()
    
    #Init all the gui interface
    def init_ui(self):
        self.init_web_view()
        
        container_layout = QtWidgets.QVBoxLayout()
        btns_layout = QtWidgets.QHBoxLayout()

        #buttons
        btn_next = QtWidgets.QPushButton("Continue") #traducir
        btn_next.clicked.connect(self.continue_btn)
        btn_close = QtWidgets.QPushButton("Close") #traducir
        btn_close.clicked.connect(self.close)
        self.line_edit = QtWidgets.QLineEdit()
        btns_layout.addWidget(btn_next)
        btns_layout.addWidget(btn_close)
        
        #Add widgets
        container_layout.addWidget(self.web_view)
        container_layout.addWidget(self.create_instructions_lbl())
        container_layout.addWidget(self.line_edit) #Create the text box to input what is the part that you are seing
        
        container_layout.addLayout(btns_layout)
        #self.setGeometry(0,0,500,400)
        
        self.setLayout(container_layout)


    #Init the widget to show the pdfs
    def init_web_view(self):
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True) #type: ignore
        self.web_view.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True) #type: ignore


    #Create the lbl with the instructions for the input
    def create_instructions_lbl(self) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel("""(g)uion (o)boe (f)lauta flauti(n) (r)equinto (c)larinete \nclarinete_ba(j)o f(a)got (t)rompa f(l)iscorno \ntrom(p)eta t(r)ombon bombar(d)ino (b)ajo t(u)ba""")
        return lbl
    

    def opener(self,path:str):
        url = QtCore.QUrl.fromLocalFile(path)
        self.web_view.load(url)


    #TODO:tratamiento del string para separarlo y alguna idea para hacer el proceso mas rápido tipo: letra de intrumento|int de posicion en banda(1,2,3)|H(si es handwritten si no nada). ejemplo(o1H = oboe primero y escrito a mano). Si un input es "" será igual que el anterior y se hará append al pdf creado en el pdf anterior. si no tiene num se guardará sin número.
    def continue_btn(self):
        input = self.line_edit.text()

        #Append the temp location and the new location to be parted at the final of the process to avoid errors
        self.temp_and_new_file_paths.append((self.actual_page.name,os.path.join(self.dir.path,DIR_SCORES,input+".pdf")))

        print(self.actual_page.name)
        self.line_edit.clear()

        self.next_pdf_page()


    #Go to the next pdf page inside the scores dir
    def next_pdf_page(self):
        reader = PyPDF2.PdfReader(os.path.join(self.dir.path,DIR_SCORES,self.dir.scores[self.actual_pdf]))
        
        #Check if there are more pages in this pdf
        if self.actual_page_num < len(reader.pages):
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[self.actual_page_num])

            temp_page = tempfile.NamedTemporaryFile(delete=False)
            writer.write(temp_page.name)

            self.opener(temp_page.name)

            self.actual_page_num += 1

            self.actual_page = temp_page

        #Check if are more pdf in this directory
        elif self.actual_pdf < len(self.dir.scores)-1:
            self.actual_page_num = 0
            self.actual_pdf += 1
            self.next_pdf_page() #Call recursively because we change of pdf and we need to display the new one
        
        #if there are no more pdf and pages
        else:
            self.actual_page_num = 0
            self.actual_pdf = 0
            self.finish()


    #Close the window setting is_clossed to true to be detected in main window    
    def close(self):
        self.is_closed = True
        self.hide()

    #Hide the window, part the pdfs and delete the temporaly files
    def finish(self):
        self.hide()

        #Copy the pdfs
        for i in self.temp_and_new_file_paths:
            shutil.copy(i[0],i[1]) #Copy the temp pdfs to the scores dir

            os.remove(i[0]) #Remove temp pdf files
        
        """#Delete original pdfs
        for i in self.dir.scores:
            os.remove(self.dir.path+"/"+DIR_SCORES+i)"""
        

    def string_maniputation(self,input:str):
        if len(input) > 0:
            #Three regular expresions
            pattern1 = r'^[poner a mano las iniciales][1-3](?:[hH])?$'
            pattern2 = r'^[poner a mano las iniciales](?:[hH])?$'
            