from PyQt6.QtCore import QObject, pyqtSignal, QThread
from frontend.pyqt.app.elements.previwer.previewer import Preview
import requests

class PreviewApiWorker(QThread):
    """
    QThread to fetch preview image bytes from the API without blocking the UI.
    Emits success(page_num, image_bytes, total_pages) or error(error_message).
    """
    success = pyqtSignal(int, bytes, int)
    error = pyqtSignal(str)

    def __init__(self, archive_id: int, piece_std_name: str, file: str, page_number: int, dpi: int = 150):
        super().__init__()
        self.archive_id = archive_id
        self.piece_std_name = piece_std_name
        self.file = file
        self.page_number = page_number
        self.dpi = dpi

    def run(self):
        try:
            # TODO: Configure correct API endpoint and parameters. 
            # E.g. using a predefined Base URL and adding valid auth tokens if needed.
            url = f"http://127.0.0.1:8000/api/v1/preview/?archive_id={self.archive_id}&piece_std_name={self.piece_std_name}&file={self.file}&page_number={self.page_number}&dpi={self.dpi}"
            url = "http://127.0.0.1:8000/api/v1/preview/?archive_id=1&piece_std_name=22-A&file=m.pdf&page_number=0&dpi=150&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzYwODA2OTYsInN1YiI6IjEifQ.x1B-GGyMO0dW8_NTT85-BAiyKvi7Ta92BthWrZGDmx8"

            response = requests.get(url, timeout=10) # Adjust timeout as needed
            
            if response.status_code == 200:
                # X-Total-Pages is returned by the FastAPI preview route
                total_pages = int(response.headers.get("X-Total-Pages", 1))
                self.success.emit(self.page_number, response.content, total_pages)
            else:
                self.error.emit(f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.error.emit(str(e))


class PreviewerController(QObject):
    enable_previous = pyqtSignal(bool)
    enable_next = pyqtSignal(bool)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()

    def __init__(self, preview_view: Preview):
        super().__init__()
        self.view = preview_view
        
        self._cache = {}  # Dict mapping (archive_id, piece_std_name, file, page_number, dpi) -> image_bytes
        
        self.current_archive_id = None
        self.current_piece_std_name = None
        self.current_file = None
        self.current_page = 0
        self.total_pages = 0
        self.current_dpi = 150
        
        self._worker = None

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
            self._display_bytes(self._cache[cache_key], page_num)
        else:
            self._start_api_worker(self.current_archive_id, self.current_piece_std_name, self.current_file, page_num, self.current_dpi)

    def _start_api_worker(self, archive_id: int, piece_std_name: str, file: str, page_num: int, dpi: int):
        self.loading_started.emit()
        self.view.show_loading()
        
        # Prevent old threads from overriding current view if the user clicks quickly
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait()

        self._worker = PreviewApiWorker(archive_id, piece_std_name, file, page_num, dpi)
        self._worker.success.connect(self._on_fetch_success)
        self._worker.error.connect(self._on_fetch_error)
        self._worker.finished.connect(self.loading_finished)
        self._worker.start()

    def _on_fetch_success(self, page_num: int, img_bytes: bytes, total_pages: int):
        self.total_pages = total_pages
        
        # Save to memory cache
        cache_key = (self.current_archive_id, self.current_piece_std_name, self.current_file, page_num, self.current_dpi)
        self._cache[cache_key] = img_bytes
        
        # If the user hasn't quickly navigated away, update the view
        if page_num == self.current_page:
            self._display_bytes(img_bytes, page_num)

    def _on_fetch_error(self, error_msg: str):
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