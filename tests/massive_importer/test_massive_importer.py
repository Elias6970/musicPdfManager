import pytest,os, tempfile, hashlib,shutil
from pathlib import Path
from classes.files_management.massive_importer import MassiveImporter
from classes.loggers.massive_importer_logger import MassiveImporterLogger
import classes.constants.constants
import classes.files_management.archive_file_manager
#########ALL FILES NEED TO BE IN THE ASSETS FOLDER###########

IMPORT_FOLDER = "imports"

root = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(root,"assets"))

def hash_file(path):
    h = hashlib.sha256()  # create a SHA-256 hash object
    with open(path, 'rb') as f:  # open file in binary mode
        for chunk in iter(lambda: f.read(4096), b''):  # read 4KB at a time
            h.update(chunk)  # feed chunk into hash
    return h.hexdigest()  # get the hash as a hex string

@pytest.fixture(autouse=True)
def clean_where_to_import():
    shutil.rmtree(IMPORT_FOLDER)
    # Recreate the empty folder
    os.makedirs(IMPORT_FOLDER)

@pytest.mark.parametrize(
         "to_import, where_to_import, expected_pieces",
        [
            #You need to add the files to assets folder inside file_decomporessor
            ("test_1",IMPORT_FOLDER,{
                "1-UNO": {
                    "expected_scores": ["blank.pdf","5_blank_pages.pdf"],
                    "expected_extras": []
                }
            }),
            ("test_2",IMPORT_FOLDER,{
                "1-UNO": {
                    "expected_scores": ["blank.pdf","5_blank_pages.pdf"],
                    "expected_extras": []
                },
                "2-DOS": {
                    "expected_scores": ["blank.pdf"],
                    "expected_extras": ["test.txt"]
                }
            }),
            ("test_3",IMPORT_FOLDER,{
                "3-TRES": {
                    "expected_scores": ["single_line.pdf","blank.pdf","5_blank_pages.pdf"],
                    "expected_extras": []
                }
            }),
            ("test_4",IMPORT_FOLDER,{
                "4-CUATRO": {
                    "expected_scores": ["blank.pdf"],
                    "expected_extras": []
                }
            }),
            ("test_5",IMPORT_FOLDER,{
                "5-CINCO": {
                    "expected_scores": ["blank.pdf","empty.pdf","5_blank_pages.pdf"],
                    "expected_extras": []
                }
            }),
            ("test_6",IMPORT_FOLDER,{
                "6-SEIS": {
                    "expected_scores": ["blank.pdf","empty.pdf","5_blank_pages.pdf"],
                    "expected_extras": []
                }
            })
        ]
)
def test_massive_importer(to_import:list[str],where_to_import:str,expected_pieces:dict[str,dict[str,list[str]]]):
    mi = MassiveImporter(None)

    monkey_patch = pytest.MonkeyPatch()
    #monkey_patch.setattr(classes.constants.constants, "RELATIVE_ARCHIVE_PATH", lambda: where_to_import)  
    monkey_patch.setattr(classes.files_management.archive_file_manager, "RELATIVE_ARCHIVE_PATH", lambda: where_to_import)
    imported = mi.import_only__into_archive(to_import,False,False)

    #Check that all the pieces has been imported
    assert len(imported) == len(expected_pieces)
    expected_pieces_list = list(expected_pieces.keys())
    expected_pieces_list.sort()
    imported.sort()

    for a,b in zip(imported,expected_pieces_list):
        assert a == b


    #Compare the files for each piece imported
    for i in imported:
        try:
            piece = expected_pieces[i]
            expected_scores = piece["expected_scores"]
            expected_extras = piece["expected_extras"]

            #Compare the scores
            scores = Path(os.path.join(where_to_import,i,"partituras"))
            score_files = [f.name for f in scores.iterdir() if f.is_file()]
            score_files.sort()
            expected_scores.sort()

            assert len(score_files) == len(expected_scores)
            for a,b in zip(score_files,expected_scores):
                assert a == b

            #Compare the extras
            extras = Path(os.path.join(where_to_import,i,"extras"))
            extras_files = [f.name for f in extras.iterdir() if f.is_file()]
            extras_files.sort()
            expected_extras.sort()

            assert len(extras_files) == len(expected_extras)
            for a,b in zip(extras_files,expected_extras):
                assert a == b            

        except KeyError:
            pytest.fail(f"The piece {i} wasn't expected to be imported")



