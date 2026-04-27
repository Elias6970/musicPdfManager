from PyQt6 import QtCore, QtWidgets, QtGui
from frontend.pyqt.app.api_client.base_api_client_factory import get_base_client
from frontend.pyqt.app.api_client.instruments_names_api_client import InstrumentsNamesApiClient
from frontend.pyqt.app.api_client.preview_api_client import PreviewApiClient
from frontend.pyqt.app.score_classifier.score_classifier_view import ScoreClassifierView
from frontend.pyqt.app.config.session_manager import SessionManager
from frontend.pyqt.app.models.generated_models import SourcePage
from frontend.pyqt.app.score_classifier.text_analizer import TextAnalizer
from frontend.pyqt.app.pop_up_windows.error.error_window import ShowError

class SourcePageWithResolution(SourcePage):
    resolution: str|None = None

class ScoreClassifierController(QtCore.QObject):
    DPI = 150
    _LOAD_SHORTCUTS = "load_shortcuts"
    _LOAD_PAGES = "load_first_page"

    def __init__(self, view: ScoreClassifierView, piece_std_name: str, scores_and_page_counts: list[tuple[str,int]] = []):
        """
        Args:
            view (ScoreClassifierView): The view associated with this controller.
            piece_std_name (str): The standardized name of the piece being classified.
            scores_and_page_counts (list[tuple[str,int]], optional): A list of tuples containing score names and their corresponding page numbers. Defaults to an empty list.
        """
        super().__init__()
        #List of tasks needed to show the first page.
        self._tasks:list[str] = [self._LOAD_SHORTCUTS, self._LOAD_PAGES] 
        self.view = view
        self.session = SessionManager()
        
        self.archive_id = self.session.get_archive_id()
        self.piece: str = piece_std_name

        self.current_score_index = 0 # Start before the first score, so that the first call to next_page() loads the first score
        self.pages:list[SourcePageWithResolution] = self._create_pages_from_scores(scores_and_page_counts) # List with all the pages need to show in order. Each element is a tuple (score_name, page_number)
        self._images_cache: dict[tuple[str, int], QtGui.QPixmap] = {}  # Cache for storing fetched images, key: (file, page_number)

        self.instruments_names_api_client = InstrumentsNamesApiClient(get_base_client())
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated_success.connect(self.on_get_instrument_shortcuts_success)
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated_error.connect(lambda error: QtWidgets.QMessageBox.critical(self.view, self.view.tr("Error"), self.view.tr(f"Failed to load instrument shortcuts: {error}")))

        self.preview_api_client = PreviewApiClient(get_base_client())
        self.preview_api_client.preview_loaded.connect(self._on_image_fetched)

        # self.view.rotate_clockwise_signal.connect(lambda: self.rotate(90))
        # self.view.rotate_counterclockwise_signal.connect(lambda: self.rotate(-90))
        self.view.continue_btn_signal.connect(self.next_page)
        # self.view.previous_btn_signal.connect(self.go_to_previous_score)
        # self.view.line_edit_text_changed_signal.connect(self.update_interpreted_instrument_label)
        

        self.text_analizer = TextAnalizer()
        self.view.line_edit_text_changed_signal.connect(self.update_interpreted_instrument_label)
        
        self.get_instrument_shortcuts()

        while self._tasks: # Wait until all tasks are done before loading the first page
            QtCore.QCoreApplication.processEvents()
        
        self.load_image_page(self.current_score_index) # Load the first page

    def _create_pages_from_scores(self, scores_and_page_counts: list[tuple[str,int]]) -> list[SourcePageWithResolution]:
        """
        Creates a list of pages to be displayed based on the scores and their corresponding page counts.
        Args:
            scores_and_page_counts (list[tuple[str,int]]): A list of tuples where each tuple contains a score name and its corresponding page count.
        Returns:
            list[SourcePageWithResolution]: A list of SourcePageWithResolution objects representing the pages to be displayed in order.
        """
        pages = []
        for score_name, page_count in scores_and_page_counts:
            for page_number in range(page_count):
                pages.append(SourcePageWithResolution(file_name=score_name,
                                        page=page_number,
                                        rotation=None,
                                        corners=None))

        self._tasks.remove(self._LOAD_PAGES) # Remove the task of loading the first page, since it is already done in the constructor

        return pages
    

    def next_page(self, instrument_name:str, keep_rotation:bool, corners:list[tuple[float, float]]):
        """Navigate to the next page in the classification process."""
        parsed_instrument_name = self.text_analizer.analyze(instrument_name)
        if not parsed_instrument_name or parsed_instrument_name.isspace():
            ShowError.show_tooltip_error(self.view.tr("Please enter a valid instrument name."), 5000, self.view.line_edit)
            return
        
        self.pages[self.current_score_index].resolution = instrument_name # Save the interpreted instrument name in the page object, so it can be used later when saving the classification
        self.pages[self.current_score_index].corners = corners

        if self.current_score_index < len(self.pages) - 1:
            self.load_image_page(self.current_score_index)
            self.load_image_page(self.current_score_index+1) # Preload the next page for smoother navigation
            self.current_score_index += 1
            self.view.change_to_continue_btn() # In case the button was changed to finish in the previous page, change it back to continue
        if self.current_score_index == len(self.pages) - 1:
            self.view.change_to_finish_btn()
        else:
            QtWidgets.QMessageBox.information(self.view, self.view.tr("End"), self.view.tr("You have reached the end of the scores."))


    def load_image_page(self, index: int):
        """
        Load the image for the given page index.
        Args:
            index (int): The index of the page to load in the pages list.
        """
        if index < 0 or index >= len(self.pages):
            return
        
        page = self.pages[index]
        if not isinstance(page.page, int):
            QtWidgets.QMessageBox.warning(self.view, self.view.tr("Invalid page"), self.view.tr("The requested page does not have a valid page number."))
            return
        cache_key:tuple[str,int] = (page.file_name, page.page)
        
        if cache_key in self._images_cache:
            pixmap = self._images_cache[cache_key]
            self.view.interactive_previewer.load_img(pixmap)
        else:
            self.preview_api_client.fetch_preview(self.archive_id, self.piece, page.file_name, page.page, self.DPI)

    def _on_image_fetched(self, page_num: int, img_bytes: bytes, total_pages: int):
        """
        Handle the event when an image is fetched from the API.
        It saves the image in a cache and displays it if it corresponds to the currently displayed page.
        If not, it is saved in the cache.
        """
        print(f"Image fetched for page {page_num}, total pages: {total_pages}")
        if self.current_score_index >= len(self.pages):
            QtWidgets.QMessageBox.warning(self.view, self.view.tr("Invalid page"), self.view.tr("Received an image for a page index that is out of range."))
            return
        print(f"Current page index: {self.current_score_index}")
        page = self.pages[self.current_score_index]
        
        if not isinstance(page.page, int):
            QtWidgets.QMessageBox.warning(self.view, self.view.tr("Invalid page"), self.view.tr("The fetched page number is invalid."))
            return
        cache_key = (page.file_name, page.page)
        if cache_key in self._images_cache:
            return  # Image already cached, no need to process it again
        
        self._images_cache[cache_key] = QtGui.QPixmap()
        self._images_cache[cache_key].loadFromData(img_bytes)

        #TODO: ERROR IN THE PREVIEW API BECAUSE IT CANT GET THE SCORE NAME AND THE PIECE NAME. IT NEED TO BE CHANGED IN THE API
        if self.pages[self.current_score_index].page == page_num: # Ensure that the fetched image corresponds to the currently displayed page
            self.view.interactive_previewer.load_img(self._images_cache[cache_key])


    def get_instrument_shortcuts(self):
        """Fetch instrument shortcuts and names from the API."""
        language_code = self.session.get_language()
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated(language_code)

    def on_get_instrument_shortcuts_success(self, shortcuts: list[tuple[str, str]]):
        """Handle successful retrieval of instrument shortcuts."""
        self.view.set_shortcuts(shortcuts)
        self._tasks.remove(self._LOAD_SHORTCUTS)


    def update_interpreted_instrument_label(self, text:str):
        """Update the interpreted instrument label in real time as the user types in the line edit."""
        self.view.interpreted_instrument_lbl.setText(self.text_analizer.analyze(text))