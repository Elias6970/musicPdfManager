import sys,os

CLIENT_VERSION = "0.1.0"
APP_NAME = "Music Pdf Manager"
APP_AUTHOR = "Elías Iborra Pérez"
GITHUB = "https://github.com/Elias6970/musicPdfManager"

#The sys._MEIPASS is variable that has the path to a temp folder where data folder is created. 
#Every time you execute the application a temp folder is created
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    IMAGES_PATH = os.path.join(sys._MEIPASS,'resources','images') #type: ignore
else:
    IMAGES_PATH = os.path.join('resources','images')
    
ICON_PATH = os.path.join(IMAGES_PATH,'icon.ico')
EDIT_IMG_PATH = os.path.join(IMAGES_PATH,'edit.png')
REFRESH_IMG_PATH = os.path.join(IMAGES_PATH,'refresh.png')
ROTATE_R_IMG_PATH = os.path.join(IMAGES_PATH,'rotate_left.png')
ROTATE_L_IMG_PATH = os.path.join(IMAGES_PATH,'rotate_right.png')
TRASH_IMG_PATH = os.path.join(IMAGES_PATH,'trash.png')


INSTRUCTIONS_SCORE_CLASSIFIER = """*******Herramienta clasificador de partituras*******

Introducción
    En el clasificador de partituras tendrás que seleccionar las partituras que quieres clasificar. Una vez seleccionadas irá apareciendo cada página de cada pdf de esa partitura para ponerle nombre.

Instrucciones
    Nombre:
        Una letra: se pondrá la letra entre parentesis si el instrumento aparece en el cuadro de arriba.
        Nombre Completo: si el instrumento no aparece en el cuadro.
    
        Si la partitura pertenece a la obra anterior puedes dejar el recuadro en blanco. El programa le pondrá el nombre de la partitura anterior automáticamente.
    
        Ejemplo:(Introducción de una secuencia de partituras)
            1. Entrada:'c' --> salida: 'clarinete'
            2. Entrada:'timbales' --> salida: 'timbales'
            3. Entrada: '' --> salida: 'timbales'` (apunte: porque al no introducir nada se presupone que es parte de la partitura anterior.)


    Numero
        Se introduce el número de la partitura (primero, segundo, tercero, etc).
        Puede no introducirse el número pero si hay mas de un papel de un mismo instrumento se debe hacer.
        Ejemplo:(Introducción de una secuencia de partituras)
            1. Entrada:'c3' --> salida: 'clarinete 3'
            2. Entrada:'dulzaina 1' --> salida: 'dulzaina 1'
            3. Entrada: '' --> salida: 'dulzaina 1'


Excepción:
    El clarinete principal no tiene número su nombre es cp.
        Ejemplo:
            Entrada: 'cp' --> salida: 'clariente principal'

Lógica aplicación
    La aplicación no efectua los cambios hasta que no se acabe de clasificar una obra entera."""