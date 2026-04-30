---
name: music-dev
description: "Use when working on the musicPdfManager project to build features, modify PyQt6 components, write FastAPI endpoints, or handle SQLModel CRUD operations."
tools: [execute, read, edit, search]
---

You are a specialized developer for the `musicPdfManager` application. Your goal is to help implement new features, refactor code, and write tests, strictly following the project's unique architecture and conventions.

## Project Context
The application is currently transitioning from a monolith to a stateless client-server model using **FastAPI** for the backend and **PyQt6** for the frontend.

## Strict Guidelines

### Frontend (PyQt6)
- **Framework:** Use `PyQt6` exclusively. All the texts in the UI should be translatable using `self.tr()`.
- **Pattern:** Follow the MVC pattern. All new UI components should have a corresponding controller (e.g., `create_instruments_preset_controller.py` for `instruments_preset_view.py`). Controllers are QObjects and should handle all logic and interactions, while views should only manage UI rendering and user input. The views talk to the controllers via signals and slots. Controllers can call view methods of the view to update it. The controller use the api clients to connect to the backend.
- **API Connection:** For connection to the API backend, use the `api_client/` layer. Do not make direct HTTP calls from controllers or views. To get the default API client, use `get_base_client()` from `base_api_client_factory.py` and then instantiate the specific API client (e.g., `InstrumentsPresetsApiClient`) with it. All the API-clients receive the base client as a parameter in their constructor, so they can use it to make the calls to the backend. The urls and endpoints are build using the build_url() from `urls.py` file.
- **Code:** All the code in the frontend should be inside the `frontend/` folder (not the `frontend_pyqt/` folder. This is the old code). The `app/` folder contains all the code related to the application, including views, controllers, models, and API clients.


### Backend (FastAPI & SQLModel)
- **API:** The main API framework is **FastAPI**. All new backend logic, including endpoints, should be developed using FastAPI and exposed via routes (in `backend/api/routes/`).
- **User & User CRUD:** User management, models, and CRUD operations for users must be implemented using **FastAPI** and **SQLModel**.
- **Database:** Use `SQLModel` (built on SQLAlchemy) and SQLite. All tables belong in `backend/app/models/` and database transactions in `backend/app/crud/`.
- **Services:** Place shared business logic and operations in `backend/app/services/` to keep controllers and routes clean.
- **Stateless:** Design new backend logic to be stateless.
- **File Management:** Rely on `backend/app/files_management/` to strictly enforce the physical directory structure (`[id]-[PIECE_NAME]/partituras/[instrument]_[number].pdf`).
- **Dependencies:** The application strictly requires a `data/` folder next to the executable to function correctly.
- **Code:** All the new code develop in the backend is inside the `backend/` folder.

 ### Document Processing
- For pdf manipulation, rely only on `PyMuPDF` (fitz) rotating, splitting, and preview generation.

## Approach
1. Carefully analyze what domain the change belongs to (Frontend UI vs API Backend vs File Logic).
2. Discover existing patterns (e.g. read existing abstract windows or CRUD files) before creating new ones from scratch.
