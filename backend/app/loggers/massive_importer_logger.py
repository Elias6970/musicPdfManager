from backend.app.loggers.default_logger import DefaultLogger


class MassiveImporterLogger(DefaultLogger):
    """Logger for the MassiveImporter process"""
    def __init__(self, name="MassiveImporterLogger", level=0):
        super().__init__(name, level)