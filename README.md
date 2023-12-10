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
`Modify menu`
`Classifier for scores`
`Refresh the list of scores when you add or delete one in the score selector page`
`Add an option to change the archieve path and the export cover path`
`Transale the app and add the options for languages`