#PyQt6 pdfviewer
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
import os
import sys

class PdfDialog(QDialog):
    def __init__(self, parent=None):
        super(PdfDialog, self).__init__(parent)

        # Create QPdfView
        self.view = QPdfView()
        self.view.setPageMode(QPdfView.PageMode.MultiPage)

        # Load PDF document
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "a.pdf")) # replace with your pdf file path
        self.document = QPdfDocument(self.view)
        self.document.load(file_path)
        self.view.setDocument(self.document)

        # Create QLineEdit
        self.line_edit = QLineEdit()

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = PdfDialog()
    dialog.show()

    sys.exit(app.exec())
