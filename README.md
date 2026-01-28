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

# Important details
- To work, the application need a directory called 'data' in the same folder as the main.py/executable. (Inside it has the database and a config file)
- Can be troubles if you add a piece and don't add scores.

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

# Tool for score classifying

####  Introduction
In the score classifier you need to select the pieces that you want to classify. After selecting them, they are going to appear page by page to label each one.

#### How to use it
+ **Instrument:**
    + <u>Diminutive:</u> Character/s that represent the instrument. You can see each one in the left shortcuts panel.
    + <u>Complete name:</u> If the instrument is not in the shortcuts panel you can write the complete name instead.
    + <u>*Empty*:<u> If you leave it empty the program takes the  instrument from the previous page.

    + Example (Sequence of inputs):
    `1. Input:'c' --> Output: 'clarinete'`
    `2. Input:'triangle' --> Output: 'triangle'`
    `3. Input: '' --> Output: 'triangle'`
<br />

+ **Number:**
    + Insert the number of that instrument (first, second, third, etc.)
    + You can leave it empty if there is only one score for that instrument (maybe for oboe. There is not oboe 1 and oboe 2).
    + Example:(Sequence of inputs):
    `1. Input:'c3' --> Output: 'clarinete 3'`
    `2. Input:'dulzaina 1' --> Output: 'dulzaina 1'`
    `3. Input: 'f' --> Output: 'flauta'`  
<br />


#### **Aplication logic**
+ The changes to the original scores (pdfs) are applied when you finish classifying a piece. If you select more than one piece to classify, the changes are going to be applied after finishing each one.

# **Features**
1. You can reclasify a piece
2. You can go the previous page when you are classifying
3. Label added to see the previous instrument classified
4. All translated except classifying instructions

# TODO
`Auto time set in db_manage with CURRENT_TIMESTAMP is set to gtm=0 and it need to be set to the local computer time`

`Implement a tool for getting logs to detect future errors`

`Translate classifying instructions`


