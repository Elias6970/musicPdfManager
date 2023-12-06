import sys,re
import gui.main_window as gui


#TODO: herramienta de importado de partituras que al importarlas se vayan mostrando para guardarlas por partes.
#TODO: modify window para añadir papeles, cambiar nombre, autor etc. se tiene que ver reflejado en la fecha de última modificación




def main():
    """text="r1H"
    pattern1 = r'^[gofnrcjatlprdbuGOFNRCJATLPRDBU][1-9](?:[hH])?$'
    pattern2 = r'^[poner a mano las iniciales](?:[hH])?$'
    a = re.match(pattern1,text)
    if a:
        print("Siii")
    else:
        print("NO")
    print(a)"""

    app = gui.QtWidgets.QApplication(sys.argv)
    w = gui.Main_window()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()