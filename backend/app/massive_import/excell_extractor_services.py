import xlrd,openpyxl, csv
from backend.app.loggers.default_logger import DefaultLogger

logger = DefaultLogger("ExcelController")

def read_data(file:str, ignore_first_row:bool=False) -> list[tuple[int,str,str,str]]:
    """
    Read an Excel file (.xls or .xlsx) and return the content of the first four columns of the first sheet as a list of tuples.
    Args:
        file (str): Path to the Excel file. Must end with .xls or .xlsx.
        ignore_first_row (bool, optional): Whether to skip the first row (e.g., header). Defaults to False.
    Returns:
        list[tuple[int, str, str, str]]: Parsed rows from the Excel file.
    Raises:
        ValueError: If the file extension is not .xls or .xlsx.
    """
    

    if file.endswith(".xlsx"):
        return _read_xlsx(file, ignore_first_row)
    elif file.endswith(".xls"):
        return _read_xls(file, ignore_first_row)
    elif file.endswith(".csv"):
        return _read_csv(file, ignore_first_row)
    return []
    

def _read_csv(file_path:str, ignore_first_row:bool=False):
    logger.info("Reading csv file %s",file_path)
    readed = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        start = 1 if ignore_first_row else 0
        for i, row in enumerate(reader):
            if i < start:
                continue 
            try:
                readed.append((int(float(row[0])),str(row[1]),str(row[2]),str(row[3])))
            except Exception as e:
                logger.error(f"Error reading row {i+1}: {str(row)}. Error: {str(e)}")

    logger.info("Finished reading csv file %s",file_path)
    return readed


def _read_xlsx(file_path:str, ignore_first_row:bool=False):
    logger.info("Reading xlsx file %s",file_path)
    excel = openpyxl.load_workbook(file_path)
    sheet = excel.worksheets[0]
    start = 1 if ignore_first_row else 0
    readed = []

    for i, row in enumerate(sheet.iter_rows()): # type: ignore    
        if i < start:
            continue 

        row_values = list(cell.value for cell in row)

        #Don't analize the empty rows 
        if row_values[0] == None:
            continue
        try:
            readed.append((int(float(row_values[0])),str(row_values[1]),str(row_values[2]),str(row_values[3])))
        except Exception as e:
            logger.error(f"Error reading row {i+1}: {str(row_values)}. Error: {str(e)}")

    logger.info("Finished reading xlsx file %s",file_path)
    return readed        


def _read_xls(file_path:str, ignore_first_row:bool=False):
    logger.info("Reading xls file %s",file_path)
    excel = xlrd.open_workbook(file_path)
    sheet = excel.sheet_by_index(0)
    start = 1 if ignore_first_row else 0
    readed = []

    for i in range(start,sheet.nrows):
        row = sheet.row_values(i)
        try:
            readed.append((int(float(row[0])),str(row[1]),str(row[2]),str(row[3])))
        except Exception as e:
            logger.error(f"Error reading row {i+1}: {str(row)}. Error: {str(e)}")

    logger.info("Finished reading xls file %s",file_path)
    return readed