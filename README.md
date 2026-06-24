# Music PDF Manager

Music PDF Manager is a comprehensive client-server application designed to manage, classify, and organize music scores and related files. It uses a **FastAPI** backend and a **PyQt6** frontend client.

- [Installation](#installation)
  - [Server Installation](#server-installation)
  - [Client Installation](#client-installation)
- [Running via Docker (Server)](#running-via-docker-server)
- [Creating the Standalone Client](#creating-the-standalone-client)
- [Important Details](#important-details)
- [Archive File Structure](#archive-file-structure)
- [Tool for Score Classifying](#tool-for-score-classifying)

## Installation

The system is divided into two parts: the backend server and the frontend client. To run the application natively in a development environment, you need to set up both.
**Requirements:** [Python 3.12](https://www.python.org/downloads/release/python-3120/) installed and added to your system PATH.

### Server Installation
2. Create and activate a virtual environment:
   - Linux/macOS: `python -m venv venv && source venv/bin/activate`
   - Windows: `python -m venv venv` and `.\venv\Scripts\Activate.ps1`
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Move to backend folder: `cd backend`
5. Run the server: `fastapi dev main.py`. You can run it also using uvicorn

### Client Installation
1. Open a new terminal and navigate to the frontend folder: `cd frontend/pyqt`
2. Create and activate a virtual environment (same routine as the server).
3. Install dependencies: `pip install -r requirements.txt`
4. Run the client: `python main.py`

## Running via Docker (Server)

You can easily launch the backend server using the provided Docker setup. The configuration automatically mounts your local `data` directory.

1. Navigate to the backend directory: `cd backend`
2. Run Docker Compose in detached mode: `docker compose up -d`
3. The server will now be accessible on `localhost:8000`.

## Creating the Standalone Client

To create an executable binary for the client, you can use PyInstaller:
1. Navigate to the frontend directory: `cd frontend/pyqt`
2. Execute the PyInstaller build spec: `pyinstaller main.spec`
3. The standalone application will be generated inside the `dist/` folder.

## Important Details

- **`data/` Directory Requirement:** The **server** strictly requires a directory called `data` to function. It reads from the global `data/` at the root of the project.

## Archive File Structure

The file structure inside the storage directory (typically `data/archives/`) is highly deterministic and enforced by the system backend:

```text
.
├── 1-PIECE-NAME
│   ├── partituras
│   │   ├── clarinete_1.pdf
│   │   ├── saxo_1.pdf
│   │   └── ...
│   └── extras
│       ├── audio1.mp3
│       ├── score.mscz
│       └── ...
├── 2-ANOTHER-PIECE
│   ├── partituras
│   │   ├── timbales.pdf
│   │   ├── oboe_1.pdf
│   │   └── ...
│   └── extras
│       ├── audio2.wav
│       ├── score.musicxml
│       └── ...
└── etc
```

Every piece folder uses the `[id]-[PIECE_NAME]` format. Inside each piece's folder:
+ **partituras**: Contains individual instrument PDF scores, named systematically via the Score Classifier tool.
+ **extras**: Contains other related media (audio files, original `.mscz`/`.musicxml` sources, etc.).

## Tool for Score Classifying

#### Introduction
The Score Classifier is a specialized workflow built to ingest untagged PDF pages. It presents them page by page, allowing you to accept shorthand strings, slice the pages, and rename the master PDF into individual properly-named instrument files.

#### How to use it
+ **Instrument:**
    + **Diminutive:** Character/s that represent the instrument. You can see each one in the left shortcuts panel.
    + **Complete name:** If the instrument is not in the shortcuts panel, you can type the complete name instead.
    + **Empty:** If you leave it empty, the program inherits the instrument from the previous page.

    + Examples (Sequence of inputs):
      `1. Input:'c' --> Output: 'clarinete'`
      `2. Input:'triangle' --> Output: 'triangle'`
      `3. Input: '' --> Output: 'triangle'`

+ **Number:**
    + Insert the part number of that instrument (first, second, third, etc.)
    + You can leave it empty if there is only one score for that instrument.
    + Examples (Sequence of inputs):
      `1. Input:'c3' --> Output: 'clarinete 3'`
      `2. Input:'dulzaina 1' --> Output: 'dulzaina 1'`
      `3. Input: 'f' --> Output: 'flauta'`  

#### Application Logic
PDF transformations are applied sequentially as you finish classifying each given piece. If you batch-process multiple pieces directly in the app, changes are processed immediately piece by piece once each classification iteration successfully concludes.
