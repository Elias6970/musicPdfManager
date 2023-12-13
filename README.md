# Activate the enviroment:
  `source "~/archivo_app/bin/activate"` 

The ~ symbol is "Alt Gr + ñ" in spanish keyboard in mac

# Librerias instaladas
`pip3 install Pillow` 

`pip3 install pytesseract`

`pip3 install opencv-python`

`pip3 install thefuzz[speedup]`

# Versions
python 3.10.1
pip 23.1.2


# Automatic detection of instruments with tesseract

Its important to remember that i have added the files, when i create the build, these files will be needed:
  - /usr/local/Cellar/tesseract/5.3.1/share/tessdata/spa.user-words
  - /usr/local/Cellar/tesseract/5.3.1/share/tessdata/spa.user-patterns
  - /usr/local/Cellar/tesseract/5.3.1/share/tessdata/configs/instruments

# TODO
`Change names from score add or like that to piece add. When we add a new piece change to piece, score is only for the music sheet`

`Creates a window to add scores to pieces that already exists in the db or the archive directory`

`Create an abstract class of add score for modify score`

`Modify menu`

`Classifier for scores`

`Add an option to change the archieve path and the export cover path`

`Transale the app and add the options for languages`

`Option for: When you add a score pop ups the window to classify the score`

`Add the option to make prefabs for selecting scores like x1 0boe,x2 flute,x4 clarinet, etc. And its name is wood wind`

`Format errors like printing errors without using error class`

`Make a combo box in the window that shows the scores that its names are similar to another ones when you add a score`