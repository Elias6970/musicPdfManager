import sys
import gui.main_window as gui


#TODO: herramienta de importado de partituras que al importarlas se vayan mostrando para guardarlas por partes.
#TODO: modify window para añadir papeles, cambiar nombre, autor etc. se tiene que ver reflejado en la fecha de última modificación




def main():
    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()