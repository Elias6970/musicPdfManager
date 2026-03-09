import pytest
from unittest.mock import MagicMock, patch
from backend.app.files_management.excel_controller import ExcelController

@pytest.fixture
def excel_controller():
    return ExcelController()

class TestExcelController:
    
    @patch('backend.app.files_management.excel_controller.xlrd.open_workbook')
    def test_read_xls(self, mock_open_workbook, excel_controller):
        # Setup mock for .xls
        mock_sheet = MagicMock()
        mock_sheet.nrows = 2
        mock_sheet.row_values.side_effect = [
            [1.0, 'Title 1', 'Author 1', 'Genre 1'],
            [2.0, 'Title 2', 'Author 2', 'Genre 2']
        ]
        
        mock_workbook = MagicMock()
        mock_workbook.sheet_by_index.return_value = mock_sheet
        mock_open_workbook.return_value = mock_workbook

        result = excel_controller.read_excel('test_files/test.xls')

        assert len(result) == 2
        assert result[0] == (1, 'Title 1', 'Author 1', 'Genre 1')
        assert result[1] == (2, 'Title 2', 'Author 2', 'Genre 2')
        mock_open_workbook.assert_called_once_with('test_files/test.xls')

    @patch('backend.app.files_management.excel_controller.openpyxl.load_workbook')
    def test_read_xlsx(self, mock_load_workbook, excel_controller):
        # Setup mock for .xlsx behavior
        mock_sheet = MagicMock()
        
        # Simulate cells
        def create_mock_row(values):
            cells = []
            for val in values:
                cell = MagicMock()
                cell.value = val
                cells.append(cell)
            return cells

        mock_sheet.iter_rows.return_value = [
            create_mock_row([1, 'Title A', 'Author A', 'Genre A']),
            create_mock_row([2, 'Title B', 'Author B', 'Genre B']),
        ]
        
        mock_workbook = MagicMock()
        mock_workbook.worksheets = [mock_sheet]
        mock_load_workbook.return_value = mock_workbook

        result = excel_controller.read_excel('test_files/test.xlsx')

        assert len(result) == 2
        assert result[0] == (1, 'Title A', 'Author A', 'Genre A')
        assert result[1] == (2, 'Title B', 'Author B', 'Genre B')
        mock_load_workbook.assert_called_once_with('test_files/test.xlsx')

    @pytest.mark.parametrize("file_name, ignore_first, row_data, expected_result", [
        (
            "test.xlsx", 
            True, 
            [
               ["Header ID", "Header Title", "Header Auth", "Header Genre"],
               [10, "Song X", "Artist X", "Rock"]
            ], 
            [(10, "Song X", "Artist X", "Rock")]
        ),
        (
            "test.xlsx", 
            False, 
            [
               [20, "Song Y", "Artist Y", "Pop"]
            ], 
            [(20, "Song Y", "Artist Y", "Pop")]
        ),
    ])
    def test_read_excel_parametrized_xlsx(self, file_name, ignore_first, row_data, expected_result, excel_controller):
        with patch('backend.app.files_management.excel_controller.openpyxl.load_workbook') as mock_load_wb:
            mock_sheet = MagicMock()
            
            # Helper to create mock cells
            rows_objects = []
            for r_data in row_data:
                row_cells = []
                for cell_val in r_data:
                    c = MagicMock()
                    c.value = cell_val
                    row_cells.append(c)
                rows_objects.append(row_cells)
            
            mock_sheet.iter_rows.return_value = rows_objects
            
            mock_wb = MagicMock()
            mock_wb.worksheets = [mock_sheet]
            mock_load_wb.return_value = mock_wb

            result = excel_controller.read_excel(file_name, ignore_first_row=ignore_first)
            
            assert result == expected_result

    def test_read_excel_invalid_extension(self, excel_controller):
        result = excel_controller.read_excel("test.txt")
        assert result == []

    @patch('backend.app.files_management.excel_controller.xlrd.open_workbook')
    def test_read_xls_logging_error(self, mock_open_workbook, excel_controller):
        # Simulate bad data in the second row causing a ValueError or similar
        mock_sheet = MagicMock()
        mock_sheet.nrows = 2
        mock_sheet.row_values.side_effect = [
            [1.0, 'Ok', 'Ok', 'Ok'],
            ['NOT_AN_INT', 'Bad', 'Bad', 'Bad']
        ]
        
        mock_workbook = MagicMock()
        mock_workbook.sheet_by_index.return_value = mock_sheet
        mock_open_workbook.return_value = mock_workbook

        # Spy on the logger
        with patch.object(excel_controller.logger, 'error') as mock_log_error:
            result = excel_controller.read_excel('test.xls')
            
            # Only the valid row should be returned
            assert len(result) == 1
            assert result[0] == (1, 'Ok', 'Ok', 'Ok')
            
            # Logger should have been called for the second row
            mock_log_error.assert_called()
            args, _ = mock_log_error.call_args
            assert "Error reading row 2" in args[0]