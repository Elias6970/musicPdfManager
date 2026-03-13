import pytest,os, tempfile, hashlib,shutil, sqlite3
from pathlib import Path
from backend.app.files_management.massive_importer import MassiveImporter
import backend.app.files_management.archive_file_manager
import backend.app.db_manage
from backend.app.utils.name_manager import NameManager
from backend.app.files_management.archive_file_manager import ArchiveFileManager
#########ALL FILES NEED TO BE IN THE ASSETS FOLDER###########

IMPORT_FOLDER = "imports"
DB_PIECES_TABLE = ":memory:"
TABLE_NAME = "prueba"

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

@pytest.fixture()
def db_conn():
    con = sqlite3.connect(DB_PIECES_TABLE)
    yield con
    con.close()

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
            }),
            ("test_7",IMPORT_FOLDER,{
                "7-SIETE": {
                    "expected_scores": ["blank.pdf","empty.pdf","5_blank_pages.pdf"],
                    "expected_extras": ["nada.txt"]
                }
            })
        ]
)
def test_import_only_into_archive(to_import:list[str],where_to_import:str,expected_pieces:dict[str,dict[str,list[str]]]):

    monkey_patch = pytest.MonkeyPatch()
    monkey_patch.setattr(backend.app.files_management.massive_importer, "RELATIVE_ARCHIVE_PATH", lambda: where_to_import)
    
    mi = MassiveImporter(None)
    imported = mi.import_only__into_archive(to_import,False,False)[0]

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
def test_simple_import_using_archive_names(db_conn:sqlite3.Connection,to_import:list[str],where_to_import:str,expected_pieces:dict[str,dict[str,list[str]]]):
    def open_db_with_fixture(self):
        self.con = db_conn
        self.cur = self.con.cursor()

    monkey_patch = pytest.MonkeyPatch()
    #monkey_patch.setattr(backend.app.constants.constants, "RELATIVE_ARCHIVE_PATH", lambda: where_to_import)  
    monkey_patch.setattr(backend.app.files_management.massive_importer, "RELATIVE_ARCHIVE_PATH", lambda: where_to_import)
    monkey_patch.setattr(backend.app.db_manage,"DB_PATH", lambda: DB_PIECES_TABLE)
    monkey_patch.setattr(backend.app.db_manage.Db_archive,"open_db", open_db_with_fixture)
    
    db = backend.app.db_manage.Db_archive(TABLE_NAME)
    mi = MassiveImporter(db)

    imported,not_imported,imported_db = mi.simple_import(to_import,False,False)
    assert len(not_imported) == 0

    #Check that all the pieces has been imported
    assert len(imported) == len(expected_pieces)
    assert len(imported_db) == len(expected_pieces)
    expected_pieces_list = list(expected_pieces.keys())
    expected_pieces_list.sort()
    imported.sort()
    imported_db.sort()

    for a,b,c in zip(imported,imported_db,expected_pieces_list):
        assert a == c
        assert b == c
    


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

    for i in imported_db:
        #Check the db
        getted =  db_conn.execute(f"SELECT cod,name FROM {TABLE_NAME} WHERE cod={NameManager.get_cod(i)} LIMIT 1").fetchone()
        assert i == NameManager.get_std_name(getted[0],getted[1])


#The expected_pieces dict key is the expected the name given by ArchiveFileManager.parse_name_to_file_manager
@pytest.mark.parametrize(
            "to_import, where_to_import, excel_data, expected_pieces",
        [
            ("test_1", IMPORT_FOLDER,
                [(1, "Title From Excel", "Comp", "Arr", "Inst")],
                {
                "1-TITLE FROM EXCEL": {
                    "expected_scores": ["blank.pdf", "5_blank_pages.pdf"],
                    "expected_extras": []
                }
            }),
            ("test_2", IMPORT_FOLDER,
                [(1, "Uno Title", "C", "A", "I"), (2, "Dos Title", "C", "A", "I")],
                {
                "1-UNO TITLE": {
                    "expected_scores": ["blank.pdf", "5_blank_pages.pdf"],
                    "expected_extras": []
                },
                "2-DOS TITLE": {
                    "expected_scores": ["blank.pdf"],
                    "expected_extras": ["test.txt"]
                }
            }),
            ("test_5", IMPORT_FOLDER,
                [(5, "Cinco From Excel", "C", "A", "I"), (6, "Seis From Excel", "C", "A", "I")],
                {
                "5-CINCO FROM EXCEL": {
                    "expected_scores": ["blank.pdf", "empty.pdf", "5_blank_pages.pdf"],
                    "expected_extras": []
                }
            }),

            # Case where directory name matches COD but has different name, expecting DB name to prevail
            ("test_6", IMPORT_FOLDER,
                [(6, "Correct Title From DB", "C", "A", "I")],
                {
                "6-CORRECT TITLE FROM DB": {
                    "expected_scores": ["blank.pdf", "empty.pdf", "5_blank_pages.pdf"],
                    "expected_extras": []
                }
            })
        ]
)
def test_import_with_data(db_conn: sqlite3.Connection, to_import: list[str], where_to_import: str, excel_data: list, expected_pieces: dict[str, dict[str, list[str]]]):
    def open_db_with_fixture(self):
        self.con = db_conn
        self.cur = self.con.cursor()

    monkey_patch = pytest.MonkeyPatch()
    monkey_patch.setattr(backend.app.files_management.massive_importer, "RELATIVE_ARCHIVE_PATH", lambda: where_to_import)
    monkey_patch.setattr(backend.app.db_manage, "DB_PATH", lambda: DB_PIECES_TABLE)
    monkey_patch.setattr(backend.app.db_manage.Db_archive, "open_db", open_db_with_fixture)

    # Mock ExcelController to return our test data without reading a real file
    class MockExcelController:
        def read_excel(self, path, ignore_first_row):
            return excel_data

    db = backend.app.db_manage.Db_archive(TABLE_NAME)
    mi = MassiveImporter(db)
    mi.excel_controller = MockExcelController()

    # The path "dummy.xlsx" doesn't matter because we mocked the reader
    imported_pieces, not_imported_pieces, imported_in_db = mi.import_with_data(to_import, "dummy.xlsx", overwrite=False, ignore_first_row=True)

    assert len(not_imported_pieces) == 0

    # Validate that generated keys match expected piece names (which should come from Excel/DB logic)
    assert len(imported_pieces) == len(expected_pieces)
    assert len(imported_in_db) == len(excel_data) # All excel rows should be in DB

    imported_pieces.sort()
    expected_pieces_list = list(expected_pieces.keys())
    expected_pieces_list.sort()

    for imported, expected in zip(imported_pieces, expected_pieces_list):
        assert imported == ArchiveFileManager(where_to_import).parse_name_to_file_manager(expected)
        # Also verify it exists in DB with that name
        cod = NameManager.get_cod(imported)
        db_row = db_conn.execute(f"SELECT cod, name FROM {TABLE_NAME} WHERE cod=?", (cod,)).fetchone()
        assert db_row is not None
        assert NameManager.get_std_name(db_row[0], db_row[1]) == imported

    # Compare files inside folders
    for i in imported_pieces:
        try:
            piece = expected_pieces[i]
            expected_scores = piece["expected_scores"]
            expected_extras = piece["expected_extras"]

            # Compare the scores
            scores_path = Path(os.path.join(where_to_import, i, "partituras"))
            if scores_path.exists():
                score_files = [f.name for f in scores_path.iterdir() if f.is_file()]
            else:
                score_files = []
            
            score_files.sort()
            expected_scores.sort()

            assert score_files == expected_scores

            # Compare the extras
            extras_path = Path(os.path.join(where_to_import, i, "extras"))
            if extras_path.exists():
                extras_files = [f.name for f in extras_path.iterdir() if f.is_file()]
            else:
                extras_files = []

            extras_files.sort()
            expected_extras.sort()

            assert extras_files == expected_extras

        except KeyError:
            pytest.fail(f"The piece {i} wasn't expected to be imported")
