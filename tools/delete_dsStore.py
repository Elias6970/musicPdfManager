import shutil,os

for root, dirs, files in os.walk("..\ArchiveDigital"):
        for file in files:
            if file == '.DS_Store':
                os.remove(os.path.join(root, file))
                print(f'Archive .DS_Store eliminado en: {root}')