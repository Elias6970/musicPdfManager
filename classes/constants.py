import os 
from classes.config import Configuration

#Version
VERSION = "0.1"
APP_NAME = "Music pdf manager"
APP_AUTHOR = "Elías Iborra Pérez"
GITHUB = "https://github.com/Elias6970/musicPdfManager"

RELATIVE_ARCHIVE_PATH = Configuration.archive_path
RELATIVE_NEW_PATH = os.path.join("..","newArchivo")
DB_FILE_NAME = "archivo.db"
DB_NAME = "AMVR_archive"
OPTIONS_OF_INSTRUMENTS_NUMBERED = ["GENERAL","OBOE 1","OBOE 2","FLAUTÍN","FLAUTA 1","FLAUTA 2","REQUINTO","CLARINETE PRAL","CLARINETE 1","CLARINETE 2","CLARINETE 3","CLARINETE BAJO","FAGOT 1","FAGOT 2","SAXOFÓN 1","SAXOFÓN 2","SAXOFÓN TENOR 1","SAXOFÓN TENOR 2","SAXOFÓN BARÍTONO","TROMPA 1","TROMPA 2","TROMPA 3","TROMPA 4","FLISCORNO 1","FLISCORNO 2","TROMPETA 1","TROMPETA 2","TROMPETA 3","TROMBÓN 1","TROMBÓN 2","TROMBÓN 3","BOMBARDINO 1","BOMBARDINO 2","TUBA 1","TUBA 2","PERCUSIÓN 1","PERCUSIÓN 2","PERCUSIÓN 3","BOMBO","CAJA","PLATOS"]
OPTIONS_OF_INSTRUMENTS_ESP = ["GENERAL","OBOE","FLAUTIN","FLAUTA","REQUINTO","PRINCIPAL","CLARINETE","CLARINETE BAJO","FAGOT","SAXOFON","SAXOFON TENOR","SAXOFON BARITONO","TROMPA","FLISCORNO","TROMPETA","TROMBON","BOMBARDINO","TUBA","PERCUSION","BOMBO","CAJA","PLATOS"]
OPTIONS_OF_INSTRUMENTS_VAL = ["GENERAL","OBOE","FLAUTI","FLAUTA","REQUINT","PRINCIPAL","CLARINET","CLARINET BAIX","FAGOT","SAXOFON","SAXOFON TENOR","SAXOFON BARITON","TROMPA","FLISCORN","TROMPETA","TROMBO","BOMBARDI","TUBA","PERCUSIO","BOMBO","CAIXA","PLATS"]
DIR_SCORES = "partituras"
DIR_EXTRAS = "extras"
IGNORE_FILES  = [".DS_Store"]
HYPHEN = "-" 
MAX_COPIES = 20 #Max copies of the combo box next to the add button in select mode 
COVER_DOSSIER_LIST = Configuration.dossier_cover 

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