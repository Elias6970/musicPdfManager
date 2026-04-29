import os,sys
from backend.app.config import Configuration

#Version
VERSION = "0.5.52"
APP_NAME = "Music Pdf Manager"
APP_AUTHOR = "Elías Iborra Pérez"
GITHUB = "https://github.com/Elias6970/musicPdfManager"

#Path to the file system archive
def RELATIVE_ARCHIVE_PATH():
    return Configuration.get_archive_path()
def COVER_LIST_DOSSIER():
    return Configuration.get_dossier_cover_path() 
def LANGUAGE():
    return Configuration.get_language()
def PRESETS_PATH():
    return Configuration.get_presets_path()
def PIECES_PRESETS_PATH():
    return Configuration.get_pieces_presets_path()
def INSTRUMENTS_PATH():
    return Configuration.get_instruments_path()
def LOGS_PATH():
    return Configuration.get_logs_path()
def DB_PATH():
    return Configuration.get_db_path()

DB_PIECES_TABLE = "pieces"
DIR_SCORES = "partituras"
DIR_EXTRAS = "extras"
IGNORE_FILES  = [".DS_Store"]
HYPHEN = "-" 
MAX_COPIES = 20 #Max copies of the combo box next to the add button in select mode 


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

#Special const to don't add scores when you add a piece
DONT_ADD_SCORES = "dont_add_scores" 
DONT_CLASSIFY_NOW = "dont_classify_now"

#Presets constants
PRESETS_COPIES = "copies"
PRESETS_OTHER_OPTIONS = "other_options"

#Pieces preset constants
PIECES_PRESETS_PRESET = "preset" 
PIECES_PRESETS_PIECES = "pieces"
PIECES_PRESETS_COPIES = "copies"