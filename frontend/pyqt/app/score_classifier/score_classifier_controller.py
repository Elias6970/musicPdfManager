from PyQt6 import QtCore, QtWidgets, QtGui
from app.api_client.base_api_client_factory import get_base_client
from app.api_client.classification_api_client import ClassificationApiClient
from app.api_client.instruments_names_api_client import InstrumentsNamesApiClient
from app.api_client.preview_api_client import PreviewApiClient
from app.score_classifier.score_classifier_view import ScoreClassifierView
from app.config.session_manager import SessionManager
from app.models.generated_models import SourcePage, ClassificationJob, ClassifiedDocument, ClassifiedDocumentConfig
from app.score_classifier.text_analizer import TextAnalizer
from app.pop_up_windows.error.error_window import ShowError
from app.pop_up_windows.collision_resolution_window import CollisionResolutionWindow

class SourcePageWithResolution(SourcePage):
    resolution: str|None = None
    user_input: str|None = None

class ScoreClassifierController(QtCore.QObject):
    DPI = 150
    _LOAD_SHORTCUTS = "load_shortcuts"
    _LOAD_PAGES = "load_first_page"

    def __init__(self, view: ScoreClassifierView, piece_std_name: str, scores_and_page_counts: list[tuple[str,int]] = []):
        """
        Args:
            view (ScoreClassifierView): The view associated with this controller.
            piece_std_name (str): The standardized name of the piece being classified.
            scores_and_page_counts (list[tuple[str,int]], optional): A list of tuples containing score names and their page_counts.
        """
        super().__init__()
        #List of tasks needed to show the first page.
        self._tasks:list[str] = [self._LOAD_SHORTCUTS, self._LOAD_PAGES] 
        self.view = view
        self.session = SessionManager()
        
        self.archive_id = self.session.get_archive_id()
        self.piece_std_name: str = piece_std_name
        self.view.piece_name_lbl.setText(piece_std_name)
        self.source_files: set[str] = set(score_name for score_name, _ in scores_and_page_counts) # Set with the names of the source files, to be sent when finishing the classification

        self.current_score_index = 0 # Start before the first score, so that the first call to next_page() loads the first score
        self.pages:list[SourcePageWithResolution] = self._create_pages_from_scores(scores_and_page_counts) # List with all the pages need to show in order. Each element is a tuple (score_name, page_number)
        self._images_cache: dict[tuple[str, int], QtGui.QPixmap] = {}  # Cache for storing fetched images, key: (file, page_number)
        self._last_rotation = 0 # Track the last rotation applied in degress
        self.job:ClassificationJob|None = None # Will be created when finishing the classification

        self.classifier_api_client = ClassificationApiClient(get_base_client())
        self.classifier_api_client.classification_success.connect(self._on_finish_classification_success)
        self.classifier_api_client.classification_file_exists_error.connect(self._on_finish_classification_file_exists_error)
        self.classifier_api_client.classification_error.connect(self._on_finish_classification_error)

        self.instruments_names_api_client = InstrumentsNamesApiClient(get_base_client())
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated_success.connect(self.on_get_instrument_shortcuts_success)
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated_error.connect(lambda error: QtWidgets.QMessageBox.critical(self.view, self.view.tr("Error"), self.view.tr(f"Failed to load instrument shortcuts: {error}")))

        self.preview_api_client = PreviewApiClient(get_base_client())
        self.preview_api_client.preview_loaded.connect(self._on_image_fetched)

        self.view.rotate_clockwise_signal.connect(lambda: self.rotate_and_load(90))
        self.view.rotate_counterclockwise_signal.connect(lambda: self.rotate_and_load(-90))
        self.view.continue_btn_signal.connect(self.next_page)
        self.view.previous_btn_signal.connect(self.previous_page)

        self.text_analizer = TextAnalizer()
        self.view.line_edit_text_changed_signal.connect(self.update_interpreted_instrument_label)

        self.get_instrument_shortcuts()

        while self._tasks: # Wait until all tasks are done before loading the first page
            QtCore.QCoreApplication.processEvents()
        
        self.load_image_page(self.current_score_index) # Load the first page
        if len(self.pages) > 1:
            self.load_image_page(self.current_score_index+1) # Preload the second page for smoother navigation


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
                                        rotation=0,
                                        corners=None))

        self._tasks.remove(self._LOAD_PAGES) # Remove the task of loading the first page, since it is already done in the constructor
        print(pages)
        print(scores_and_page_counts)
        return pages
    

    def next_page(self, user_input:str, keep_rotation:bool, corners:list[tuple[float, float]]):
        """Navigate to the next page in the classification process."""
        parsed_instrument_name = self.get_instrument_from_input(user_input)
        if parsed_instrument_name is None:
            ShowError.show_tooltip_error(self.view.tr("The first page can't be left empty."), 5000, self.view.line_edit)
            return
                
        self.pages[self.current_score_index].user_input = user_input
        self.pages[self.current_score_index].resolution = parsed_instrument_name # Save the interpreted instrument name in the page object, so it can be used later when saving the classification
        self.pages[self.current_score_index].corners = corners
        self.view.set_last_classified(parsed_instrument_name)

        if self.current_score_index < len(self.pages) - 1:
            self.load_image_page(self.current_score_index+1)
            self.load_image_page(self.current_score_index+2) # Preload the next page for smoother navigation
            self.current_score_index += 1
            self.view.change_to_continue_btn() # In case the button was changed to finish in the previous page, change it back to continue
            self.view.clear_line_edit() # Clear the line edit for the next input
            self.view.btn_back.setEnabled(True) # Enable the back button, since we are no longer in the first page
        else:
            self.finish_classification()
        
        if self.current_score_index == len(self.pages) - 1:
            self.view.change_to_finish_btn()
    
    def previous_page(self):
        """Navigate to the previous page in the classification process."""
        if self.current_score_index > 0:
            self.current_score_index -= 1
            self.load_image_page(self.current_score_index)
            self.view.change_to_continue_btn() # In case the button was changed to finish in the next page, change it back to continue
            # Load the user input for the previous page in the line edit, so it can be edited if needed
            previous_user_input = self.pages[self.current_score_index].user_input
            if previous_user_input is not None:
                self.view.line_edit.setText(previous_user_input)
            try:
                self.view.set_last_classified(self.pages[self.current_score_index-1].resolution or "")
            except IndexError:
                self.view.set_last_classified("")
            
            if self.current_score_index == 0:
                self.view.btn_back.setEnabled(False) # Disable the back button, since we are in the first page
        else:
            ShowError.show_tooltip_error(self.view.tr("You are already in the first page."), 5000, self.view.btn_back)
            self.view.btn_back.setEnabled(False)

    def finish_classification(self):
        """
        Finish the classification and send the results to the backend or save them as needed.
        """
        dict_pages: dict[str, list[SourcePage]] = {}
        for page in self.pages:
            if page.resolution is not None:
                dict_pages.setdefault(page.resolution, []).append(SourcePage(**page.model_dump()))
        
        dict_documents = {instrument: ClassifiedDocument(config=ClassifiedDocumentConfig(overwrite=False, rename = None), pages=pages) for instrument, pages in dict_pages.items()}
        
        self.job = ClassificationJob(
            archive_id=self.archive_id,
            piece_std_name=self.piece_std_name,
            classifications=dict_documents,
            source_files=list(self.source_files)
        )

        self.classifier_api_client.execute_classification(self.archive_id, self.job)
            

    def _on_finish_classification_success(self):
        """Handle the successful completion of the classification by showing a success message and emitting a signal to notify other parts of the application."""
        QtWidgets.QMessageBox.information(self.view, self.view.tr("Success"), self.view.tr("Classification completed successfully."))
        self.view.accept()
    
    def _on_finish_classification_file_exists_error(self, missing_names:list[str]):
        """Handle the case when the classification fails because some of the output files already exist in the backend. It opens a collision resolution window where the user can choose to rename the new files or overwrite the existing ones."""
        if missing_names:
            self.collision_window = CollisionResolutionWindow(missing_names, self.view)
            self.collision_window.resolved_signal.connect(self._on_collision_resolved)
            self.collision_window.exec()
        
    def _on_collision_resolved(self, resolution_dict: dict[str, str | None]):
        """Handle the resolution of filename collisions by updating the classification job configs with the new names or overwrite flags, and then re-executing the classification."""
        if not self.job or not self.job.classifications:
            return
            
        for missing_name, new_name in resolution_dict.items():
            if missing_name in self.job.classifications:
                if new_name is None:
                    self.job.classifications[missing_name].config.overwrite = True #type: ignore
                else:
                    self.job.classifications[missing_name].config.rename = new_name #type: ignore
                    
        self.classifier_api_client.execute_classification(self.archive_id, self.job)

    def _on_finish_classification_error(self, error:str):
        """Handle unexpected errors during classification by showing an error message to the user."""
        QtWidgets.QMessageBox.critical(self.view, self.view.tr("Error"), self.view.tr(f"An error occurred while finishing the classification: {error}"))

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
            if self.view.keep_rotation_cb.isChecked(): # Keep rotation
                pixmap = self._rotate(self._last_rotation, self._images_cache[cache_key])
                self._images_cache[cache_key] = pixmap # Update the cache with the rotated pixmap, so if the user goes back to this page it will be shown with the correct rotation
            else:
                pixmap = self._images_cache[cache_key]
            self.view.interactive_previewer.load_img(pixmap)
        else:
            self.preview_api_client.fetch_preview(self.archive_id, self.piece_std_name, page.file_name, page.page, self.DPI, abort_previous=False)

    def _on_image_fetched(self, piece_std_name: str, file_name: str, img_bytes: bytes, page_number: int, total_pages: int):
        """
        Handle the event when an image is fetched from the API.
        It saves the image in a cache and displays it if it corresponds to the currently displayed page.
        If not, it is saved in the cache.
        """
        if self.current_score_index >= len(self.pages):
            QtWidgets.QMessageBox.warning(self.view, self.view.tr("Invalid page"), self.view.tr("Received an image for a page index that is out of range."))
            return
        
        if not isinstance(page_number, int):
            QtWidgets.QMessageBox.warning(self.view, self.view.tr("Invalid page"), self.view.tr("The fetched page number is invalid."))
            return
        cache_key = (file_name, page_number)
        if cache_key in self._images_cache:
            return  # Image already cached, no need to process it again

        self._images_cache[cache_key] = QtGui.QPixmap()
        self._images_cache[cache_key].loadFromData(img_bytes)
        
        #Ensure that the fetched image corresponds to the currently displayed page
        if self.pages[self.current_score_index].file_name == file_name and self.pages[self.current_score_index].page == page_number:
            self.view.interactive_previewer.load_img(self._images_cache[cache_key])


    def get_instrument_shortcuts(self):
        """Fetch instrument shortcuts and names from the API."""
        language_code = self.session.get_language()
        self.instruments_names_api_client.get_instruments_and_shortcuts_translated(language_code)

    def on_get_instrument_shortcuts_success(self, shortcuts: list[tuple[str, str]]):
        """Handle successful retrieval of instrument shortcuts."""
        self.view.set_shortcuts(shortcuts)
        self._tasks.remove(self._LOAD_SHORTCUTS)

    def get_instrument_from_input(self, text:str) -> str | None:
        """
        Get the interpreted instrument name from a text input.
        If the text is empty it return the last interpreted instrument.
        Returns:
            String with the interpreted isntrument.
            None is interpreted as the first empty input that is invalid.
        """
        try:
            if text.strip() == "":
                if self.current_score_index > 0:
                    return self.pages[self.current_score_index-1].resolution or ""
                else:
                    return None
            else:
                return self.text_analizer.analyze(text)
        except ValueError:
            return self.view.tr("Invalid characters.")
        
    def update_interpreted_instrument_label(self, text:str):
        """Update the interpreted instrument label in real time as the user types in the line edit."""
        self.view.interpreted_instrument_lbl.setText(self.get_instrument_from_input(text))
    

    def _rotate(self, angle: int, pixmap: QtGui.QPixmap) -> QtGui.QPixmap:
        """Rotate a pixmap by the given angle and return the rotated pixmap."""
        transform = QtGui.QTransform().rotate(angle)
        return pixmap.transformed(transform, QtCore.Qt.TransformationMode.SmoothTransformation)
    

    def rotate_and_load(self, angle: int):
        """
        Rotate the currently displayed image by the given angle.
        It is rotated by rotating the cached pixmap and loading it in the previewer.
        Args:
            angle (int): The angle in degrees to rotate the image. Positive values rotate clockwise, negative values rotate counterclockwise.
        """
        if self.current_score_index >= len(self.pages):
            QtWidgets.QMessageBox.warning(self.view, self.view.tr("Invalid page"), self.view.tr("Cannot rotate an image for a page index that is out of range."))
            return
        
        current_page = self.pages[self.current_score_index]
        if not isinstance(current_page.page, int):
            QtWidgets.QMessageBox.warning(self.view, self.view.tr("Invalid page"), self.view.tr("The current page does not have a valid page number, cannot perform rotation."))
            return
        
        
        self._last_rotation = (self._last_rotation + angle) % 360

        # Update the rotation in the page object
        if current_page.rotation is None:
            current_page.rotation = angle
        else:
            current_page.rotation = (current_page.rotation + angle) % 360

        # Rotate the pixmap in the cache
        cache_key = (current_page.file_name, current_page.page)
        if cache_key in self._images_cache:
            self._images_cache[cache_key] = self._rotate(angle, self._images_cache[cache_key])
            self.view.interactive_previewer.load_img(self._images_cache[cache_key])