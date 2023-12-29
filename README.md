# Music pdf manager
This gui application is a tool to manage the digital archive of a music band without using the file system. 

# Getting Started
1. Have [python 3.12.0](https://www.python.org/downloads/release/python-3120/) installed and added to the path. You can install it from their oficial website.
1.1 You can create a virtual enviroment using `python -m venv /path/to/new/virtual/environment` to have a clean installation. After creating the env you need to activate it using `/path/to/new/virtual/enviroment/Scripts/Activate`. You can check their [oficial website](https://docs.python.org/3/library/venv.html).
2. Install the requeriments using `pip install -r requeriments.txt`.
3. Execute the main file to start the program `python main.py`

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



# Versions
python 3.12.0
pip 23.1.2

# TODO
`Transale the app and add the options for languages`

`Add the option to make prefabs for selecting scores like x1 0boe,x2 flute,x4 clarinet, etc. And its name is wood wind`

`Implement a tool for getting logs to detect future errors`

`Auto time set in db_manage with CURRENT_TIMESTAMP is set to gtm=0 and it need to be set to the local computer time`

`Make a combo box in the window that shows the scores that its names are similar to another ones when you add a score`

