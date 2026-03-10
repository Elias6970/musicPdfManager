import pytest,os, tempfile, hashlib
from backend.app.files_management.file_decompressor import FileDecompressor
from backend.app.loggers.massive_importer_logger import MassiveImporterLogger

#########ALL FILES NEED TO BE IN THE ASSETS FOLDER###########

root = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(root,"assets"))

def hash_file(path):
    h = hashlib.sha256()  # create a SHA-256 hash object
    with open(path, 'rb') as f:  # open file in binary mode
        for chunk in iter(lambda: f.read(4096), b''):  # read 4KB at a time
            h.update(chunk)  # feed chunk into hash
    return h.hexdigest()  # get the hash as a hex string


@pytest.mark.parametrize(
         "zip_path, inside_files",
        [
            #You need to add the files to assets folder inside file_decomporessor
            ("decompress_zip_one_file.zip",["blank.pdf"]),
            ("decompress_zip_three_files.zip",["blank.pdf", "empty.pdf", "5_blank_pages.pdf"]),
            ("decompress_zip_with_one_pdf_in_a_subfolder.zip",["empty.pdf"]),
            ("decompress_zip_with_some_subfolders.zip", ["single_line.pdf","blank.pdf","5_blank_pages.pdf"])
        ]
)
def test_decompress_zip_without_folders(zip_path:str,inside_files:list[str]):
    path_to_extract = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())

    fd = FileDecompressor(MassiveImporterLogger())
    extracted = fd.decompress_zip_without_folders(zip_path,path_to_extract)

    assert len(extracted) == len(inside_files)
    for i in extracted:
        if os.path.basename(i) in inside_files:
            assert hash_file(i) == hash_file(os.path.basename(i)) # We can do this because we checked that i is in inside_files that are in assets
        else:
            raise AssertionError(f"Archivo {i} no encontrado en los esperados")


@pytest.mark.parametrize(
         "rar_path, inside_files",
        [
            #You need to add the files to assets folder inside file_decomporessor
            ("decompress_zip_one_file.rar",["blank.pdf"]),
            ("decompress_zip_three_files.rar",["blank.pdf", "empty.pdf", "5_blank_pages.pdf"]),
            ("decompress_zip_with_one_pdf_in_a_subfolder.rar",["empty.pdf"]),
            ("decompress_zip_with_some_subfolders.rar", ["single_line.pdf","blank.pdf","5_blank_pages.pdf"])
        ]
)
def test_decompress_rar_without_folders(rar_path:str,inside_files:list[str]):
    path_to_extract = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())

    fd = FileDecompressor(MassiveImporterLogger())
    extracted = fd.decompress_rar_without_folders(rar_path,path_to_extract)

    assert len(extracted) == len(inside_files)
    for i in extracted:
        if os.path.basename(i) in inside_files:
            assert hash_file(i) == hash_file(os.path.basename(i)) # We can do this because we checked that i is in inside_files that are in assets
        else:
            raise AssertionError(f"Archivo {i} no encontrado en los esperados")