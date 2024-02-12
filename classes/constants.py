import os,sys
from classes.config import Configuration

#Version
VERSION = "0.5"
APP_NAME = "Music pdf manager"
APP_AUTHOR = "Elías Iborra Pérez"
GITHUB = "https://github.com/Elias6970/musicPdfManager"

#Path to the file system archive
def RELATIVE_ARCHIVE_PATH():
    return Configuration.get_archive_path()
def COVER_LIST_DOSSIER():
    return Configuration.get_dossier_cover_path() 
def LANGUAGE():
    return Configuration.get_language()


DB_FILE_NAME = "archivo.db"
DB_NAME = "AMVR_archive"
DIR_SCORES = "partituras"
DIR_EXTRAS = "extras"
IGNORE_FILES  = [".DS_Store"]
HYPHEN = "-" 
MAX_COPIES = 20 #Max copies of the combo box next to the add button in select mode 

#Path to the .db file
DB_PATH = os.path.join('data',DB_FILE_NAME)

#The sys._MEIPASS is variable that has the path to a temp folder where data folder is created. 
#Every time you execute the application a temp folder is created
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    ICON_PATH = os.path.join(sys._MEIPASS,'data','img','icon.ico') #type: ignore
else:
    ICON_PATH = os.path.join('data','img','icon.ico')


#Database parameters
COD = "cod"
NAME = "name"
AUTHOR = "author"
TYPE = "type"
CREATED_DATE = "created_date"
LAST_MODIFICATION = "last_modification"
DIGITALIZED = "digitalized"
HANDWRITTEN = "handwritten"
PARTED = "parted"
#CAMBIE DIR_SCORE y DIR_EXTRAS de partituras a partituras. Alomejor luego pueden haber problemas por eso. Para tenerlo en cuenta

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