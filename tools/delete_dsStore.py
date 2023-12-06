import shutil,os

for root, dirs, files in os.walk("..\ArchivoDigital"):
        for file in files:
            if file == '.DS_Store':
                os.remove(os.path.join(root, file))
                print(f'Archivo .DS_Store eliminado en: {root}')