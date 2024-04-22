# Music pdf manager
This gui application is a tool to manage the digital archive of a music band without using the file system. 
+ [Installation](#installation)
+ [Creating the standalone](#creating-the-standalone)
+ [Important](#important)
+ [Archive file structure](#archive-file-structure)
+ [Herramienta clasificadora de partituras](#herramienta-clasificador-de-partituras)
+ [To do](#todo)

# Installation
1. Have [python 3.12.0](https://www.python.org/downloads/release/python-3120/) installed and added to the path. You can install it from their oficial website.
1.1 You can create a virtual enviroment using `python -m venv /path/to/new/virtual/environment` to have a clean installation. After creating the env you need to activate it using `/path/to/new/virtual/enviroment/Scripts/Activate`. You can check their [oficial website](https://docs.python.org/3/library/venv.html).
2. Install the requeriments using `pip install -r requeriments.txt`.
3. Execute the main file to start the program `python main.py`

# Creating the standalone
1.  Execute  in the console `pyinstaller main.spec` (pyinstaller is installed in the requeriments.txt).
2.  You have your standalone in the dist folder.

# Important
To work, the application need a directory called 'data' in the same folder as the main.py/executable. (Inside it has the database and a config file)

# Archive file structure
The file structure of the directory with the files is this:
```
.
├── 1-PIECE
│   ├── partituras
│   │   ├──clarinete_1.pdf
│   │   ├──saxo_1.pdf
│   │   └──...
│   └── extras
│       ├──audio1.mp3
│       ├──score.mscz
│       └──...
├── 2-ANOTHER PIECE
│   ├── partituras
│   │   ├──timbales.pdf
│   │   ├──oboe_1.pdf
│   │   └──...
│   └── extras
│       ├──audio2.wav
│       ├──score.musicxml
│       └──...
└── etc
```
The archive has folders with the `cod` and the `name` separated with a hyppen `-` for every piece. Every folder has two folders:
+  partituras: has the pdfs with their correct name made with [the classifier tool](#herramienta-clasificador-de-partituras).
+ extras: has the other data that is not a pdf. Now it is not possible to see the extra files with this application. You need to go to the folder and see it manually.

# Herramienta clasificador de partituras

####  Introducción
En el clasificador de partituras tendrás que seleccionar las partituras que quieres clasificar. Una vez seleccionadas irá apareciendo cada página de cada pdf de esa partitura para ponerle nombre.

#### Instrucciones
+ **Nombre:**
    + <u>Una letra:</u> se pondrá la letra entre parentesis si el instrumento aparece en el cuadro de arriba.
    + <u>Nombre Completo:</u> si el instrumento no aparece en el cuadro.
    <br />
    + Si la partitura pertenece a la obra anterior puedes dejar el recuadro en blanco. El programa le pondrá el nombre de la partitura anterior automáticamente.
    <br />
    + Ejemplo:(Introducción de una secuencia de partituras)
    `1. Entrada:'c' --> salida: 'clarinete'`
    `2. Entrada:'timbales' --> salida: 'timbales'`
    `3. Entrada: '' --> salida: 'timbales'` porque al no introducir nada se presupone que es parte de la partitura anterior.
<br />

+ **Numero:**
    + Se introduce el número de la partitura (primero, segundo, tercero, etc).
    + Puede no introducirse el número pero si hay mas de un papel de un mismo instrumento se debe hacer.
    + Ejemplo:(Introducción de una secuencia de partituras)
    `1. Entrada:'c3' --> salida: 'clarinete 3'`
    `2. Entrada:'dulzaina 1' --> salida: 'dulzaina 1'`
    `3. Entrada: '' --> salida: 'dulzaina 1'` 
    
<br />

#### **Excepción:** 
+ El clarinete principal no tiene número su nombre es **cp**.
    + Ejemplo:
    `Entrada: 'cp' --> salida: 'clariente principal'`

#### **Lógica aplicación**
+ La aplicación no efectua los cambios hasta que no se acabe de clasificar una obra entera.

# **Features**
1. You can reclasify a piece
2. You can go the previous page when you are classifying
3. Label added to see the previous instrument classified
4. All translated except classifying instructions

# TODO
`Refactor the project with Pieces not an array of strings`

`Add a refresh button next to search bar`

`Error modifying the pieces due to change_piece_dir_name function in Archive_file_manager`

`Add the option to make prefabs for selecting scores like x1 0boe,x2 flute,x4 clarinet, etc. And its name is wood wind`

`Make a checkbox in selection window to show only pieces that are in the pyshical archive`

`Make the preview for the actual selected pdf in selection window`

`Translate classifying instructions`

`Translate the line 75 of Dossier class(printer file) which is showed when you create the dossier`

`Maybe we can add a window that shows all the instruments selected  when you finish a piece in classify window`

`Implement a tool for getting logs to detect future errors`

`Import db from xlsx and xls`

`Auto time set in db_manage with CURRENT_TIMESTAMP is set to gtm=0 and it need to be set to the local computer time`



