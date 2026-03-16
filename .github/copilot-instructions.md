# musicPdfManager Guidelines

## Code Style
- **Language**: Python 3.12.
- **Frontend Framework**: Built strictly with **PyQt6** (`frontend_pyqt/`). 
- **Backend ORM**: Uses **SQLModel** (built on SQLAlchemy) for SQLite database interactions (`backend/app/models/`, `backend/app/crud/`).
- **PDF & Image Processing**: Relies heavily on `PyMuPDF` (fitz), `reportlab`, and `opencv-python`/`numpy`.

## Architecture
- **Paradigm Migration**: The architecture is currently a monolith but is actively migrating to a stateless client-server model using **FastAPI**.
- **Separation of Concerns**: Clean separation between UI presentation (`frontend_pyqt/`), business/data logic (`backend/`), and heuristics/processing layer (`autodetect/`) (Deprecated, don't use it).
- **`frontend_pyqt/`**: Manages user input, routes UI interactions to the backend, and renders PDFs natively. Includes a dedicated `interactive_previewer/` subsystem with custom graphical scenes.
- **`backend/`**: Handles data persistence (SQLModel), strict file management, and document processing (PDF rotation/splitting/preview).
- **Entry Point**: `main.py` is the application entry point, which initializes the PyQt6 UI.

## Build and Test
- **Setup Environment**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r backend/requirements.txt -r frontend_pyqt/requirements.txt
  ```
- **Run Development**: `python main.py`
- **Build Executable**: `pyinstaller main.spec` (Outputs a standalone binary to the `dist/` directory). Note that the executable expects a `data/` directory to be placed next to it at runtime to function correctly.
- **Testing**: Run tests located in `backend/tests/` using `pytest backend/tests/`.

## Conventions
- **Strict Physical Directory Structure**: The application enforces a strict file hierarchy on disk (e.g., `[id]-[PIECE_NAME]/partituras/[instrument]_[number].pdf` and `extras/`). File paths are highly deterministic and managed in `backend/app/files_management/`.
- **PyQt Abstraction**: Instead of generating UI tightly coupled to logic, the frontend utilizes an `abstract_windows/` module (e.g., `abstract_fields_window.py`) to inherit common window behaviors, reducing boilerplate for CRUD screens.
- **The `data/` Dependency**: The app strictly requires a `data/` folder in its execution directory containing `config.yml`, SQLite database, `instruments.json`, and preset schemas.
- **Score Classifying Paradigm**: The app has a dedicated workflow in `backend/app/classifier/` and `frontend_pyqt/score_classifier/` built to ingest untagged PDF pages, present them in a loop, accept shorthand strings (e.g., "c3" -> "clarinete 3"), and slice/rename the master PDF into individual instrument files.
