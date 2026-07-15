from pathlib import Path



APP_NAME = "Ecrin Efe Mobilya Cari Hesap"
APP_VERSION = "1.0.0"


DOCUMENTS_DIR = Path.home() / "Documents"


APP_DATA_DIR = DOCUMENTS_DIR / "MobilyaCari"


DATABASE_PATH = APP_DATA_DIR / "cari.db"


BACKUP_DIR = APP_DATA_DIR / "yedekler"
REPORTS_DIR = APP_DATA_DIR / "raporlar"



WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 600


def create_application_directories() -> None:

    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)