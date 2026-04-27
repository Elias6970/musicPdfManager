from PyQt6 import QtCore, QtWidgets, QtGui
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.instruments_names_api_client import InstrumentsNamesApiClient
from frontend.pyqt.app.api_client.preview_api_client import PreviewApiClient
from frontend.pyqt.app.score_classifier.score_classifier_view import ScoreClassifierView
from frontend.pyqt.app.config.session_manager import SessionManager

class ScoreClassifierController(QtCore.QObject):
    def __init__(self, view: ScoreClassifierView):
        super().__init__()
        self.view = view
        self.session = SessionManager()

        self.instruments_names_api_client = InstrumentsNamesApiClient(get_base_client())
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated_success.connect(self.view.set_shortcuts)
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated_error.connect(lambda error: QtWidgets.QMessageBox.critical(self.view, self.view.tr("Error"), self.view.tr(f"Failed to load instrument shortcuts: {error}")))

        self.preview_api_client = PreviewApiClient(get_base_client())
        self.preview_api_client.preview_loaded.connect(self._on_image_fetched)
        # self.view.rotate_clockwise_signal.connect(lambda: self.rotate(90))
        # self.view.rotate_counterclockwise_signal.connect(lambda: self.rotate(-90))
        # self.view.continue_btn_signal.connect(self.continue_to_next_score)
        # self.view.previous_btn_signal.connect(self.go_to_previous_score)
        # self.view.line_edit_text_changed_signal.connect(self.update_interpreted_instrument_label)


    def load_image(self):
        self.preview_api_client.fetch_preview(
            archive_id=2,  # Example ID, replace with actual
            piece_std_name="231-Gitana",
            file="oboe.pdf",
            page_number=0,
            dpi=150
        )

    def _on_image_fetched(self, page_num: int, img_bytes: bytes, total_pages: int):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(img_bytes)
        if pixmap:
            self.view.view.load_img(pixmap)
        else:
            print("Failed to load image from data")

    def get_instrument_shortcuts(self):
        """Fetch instrument shortcuts and names from the API."""
        language_code = self.session.get_language()
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated(language_code)