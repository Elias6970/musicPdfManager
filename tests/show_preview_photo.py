from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication,QWidget,QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys,os

class Label(QLabel):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap(os.path.join("data","portada_dossier_partituras.jpg"))
        self.setPixmap(pixmap)
        self.resize(pixmap.height(), pixmap.width())




class Menu(QMainWindow):
    def __init__(self) -> None:
        super(Menu,self).__init__()
        self.setWindowTitle("Title")

        #self.setGeometry(200,200,200,200)
        lay = QVBoxLayout()
        label = Label()
        lay.addWidget(label)

        self.setLayout(lay)

        self.show()


class Main_window(QtWidgets.QMainWindow):
    def __init__(self):

        super(Main_window,self).__init__() #Create the Main_window Object callin QMainWindow constructor(i think)
        
        #Check if there is the config file and the paths exitsts
        #IMPORTANTE: Solo comprueba que exista el archivo, el dossier no lo  mira
        while(not os.path.exists(PLAIN_TEXT_CONFIG_PATH) or not os.path.exists(Configuration.get_archive_path()) or not os.path.exists(Configuration.get_dossier_cover())):
            Preferences_window(True,self)

        #Init the Archive 
        self.archive = Archive(DB_NAME,RELATIVE_ARCHIVE_PATH())
        
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))

        self.setMenuBar(self.create_menu_bar())        

        up_zone = self.create_up_zone()

        self.scroll = Status_console()

        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout()
        
        #Space
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(20,0,20,20)

        container_layout.addWidget(up_zone)
        container_layout.addWidget(self.scroll)
        
        container.setLayout(container_layout)


        self.setCentralWidget(container)
        self.setGeometry(100,80,200,200)
        self.setWindowTitle("AMRV archive manager") #traducir





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    
    sys.exit(app.exec_())


