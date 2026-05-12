from PyQt6.QtCore import QObject, pyqtSignal
from app.elements.previwer.previewer import Preview
from app.api_client.preview_api_client import PreviewApiClient


class PreviewerController(QObject):
    enable_previous = pyqtSignal(bool)
    enable_next = pyqtSignal(bool)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()

    def __init__(self, preview_view: Preview, preview_api_client: PreviewApiClient):
        super().__init__()
        self.view = preview_view
        self.api_client = preview_api_client
        
        # Connect API signals directly to the UI
        self.api_client.preview_loaded.connect(self._on_fetch_success)
        self.api_client.preview_error.connect(self._on_fetch_error)
        
        self._cache = {}  # Dict mapping (archive_id, piece_std_name, file, page_number, dpi) -> (image_bytes, total_pages)
        
        self.current_archive_id = None
        self.current_piece_std_name = None
        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.current_dpi = 150

    def load_document(self, archive_id: int, piece_std_name: str, file: str, dpi: int = 150):
        """
        Loads a new document, resetting the page count and view.
        """
        self.current_archive_id = archive_id
        self.current_piece_std_name = piece_std_name
        self.current_file = file
        self.current_dpi = dpi
        self.total_pages = 0
        self.current_page = 0
        self.view.clear()
        
        self.enable_previous.emit(False)
        self.enable_next.emit(False)
        
        self._fetch_and_display_page(self.current_page)

    def _fetch_and_display_page(self, page_num: int):
        if self.current_archive_id is None or not self.current_piece_std_name or not self.current_file:
            return

        cache_key = (self.current_archive_id, self.current_piece_std_name, self.current_file, page_num, self.current_dpi)
        
        if cache_key in self._cache:
            # Hit cache! Display instantly.
            img_bytes, total_pages = self._cache[cache_key]
            self.total_pages = total_pages  # Update total pages from cache
            self._display_bytes(img_bytes, page_num)
        else:
            self._start_api_worker(self.current_archive_id, self.current_piece_std_name, self.current_file, page_num, self.current_dpi)

    def _start_api_worker(self, archive_id: int, piece_std_name: str, file: str, page_num: int, dpi: int):
        self.loading_started.emit()
        self.view.show_loading()
        
        # Fetching new previews will automatically abort the old running ones in the PreviewApiClient
        self.api_client.fetch_preview(
            archive_id=archive_id,
            piece_std_name=piece_std_name,
            file=file,
            page_number=page_num,
            dpi=dpi
        )

    def _on_fetch_success(self, piece_std_name: str, file_name: str, img_bytes: bytes, page_number: int, total_pages: int):
        self.loading_finished.emit()
        self.total_pages = total_pages
        
        # Save to memory cache
        cache_key = (self.current_archive_id, self.current_piece_std_name, self.current_file, page_number, self.current_dpi)
        self._cache[cache_key] = (img_bytes, total_pages)
        
        # If the user hasn't quickly navigated away, update the view
        if page_number == self.current_page:
            self._display_bytes(img_bytes, page_number)

    def _on_fetch_error(self, error_msg: str):
        self.loading_finished.emit()
        print(f"Error fetching preview: {error_msg}")
        self.view.show_error(error_msg)
        self.enable_previous.emit(False)
        self.enable_next.emit(False)

    def _display_bytes(self, img_bytes: bytes, page_num: int):
        if img_bytes:
            self.view.set_image_from_bytes(img_bytes)
        
        # Emit signals so parent UI can disable/enable the arrows
        self.enable_previous.emit(self.current_page > 0)
        
        # A bit of a guard to prevent next page if total_pages is known and reached
        if self.total_pages > 0:
            self.enable_next.emit(self.current_page < self.total_pages - 1)
        else:
            self.enable_next.emit(False)

    def next_page(self):
        if self.total_pages == 0 or self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._fetch_and_display_page(self.current_page)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._fetch_and_display_page(self.current_page)
    
    def clear(self, cache:bool=False):
        """
        Clear the previewer state. If cache is True, also clear the images in memory cache.
        """
        self.current_archive_id = None
        self.current_piece_std_name = None
        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.view.clear()
        
        if cache:
            self._cache.clear()