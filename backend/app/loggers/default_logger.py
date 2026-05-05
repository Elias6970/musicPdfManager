import logging,os
from backend.app.utils.settings import get_server_settings


class DefaultLogger(logging.Logger):
    def __init__(self, name="DefaultLogger", level = 0):
        super().__init__(name, level)
        logs_folder = get_server_settings().log_path
        # Try to create the dir if doesn't exist
        os.makedirs(logs_folder, exist_ok=True)
        log_path = os.path.join(logs_folder,name.lower()+".log")

        self.setLevel(logging.DEBUG)  # Guardar todo en archivo, aunque filtres en consola

        # Formato de logs
        formato = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # Handler para consola (solo INFO+)
        consola = logging.StreamHandler()
        consola.setLevel(logging.INFO)
        consola.setFormatter(formato)

        # Handler para archivo (DEBUG+)
        archivo = logging.FileHandler(log_path, encoding="utf-8")
        archivo.setLevel(logging.DEBUG)
        archivo.setFormatter(formato)

        # Evitar duplicados
        if not self.hasHandlers():
            self.addHandler(consola)
            self.addHandler(archivo)
