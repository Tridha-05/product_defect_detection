"""All settings in one place. Values come from environment variables / .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # the "backend" folder
load_dotenv(BASE_DIR / ".env")


def _fix_db_url(url: str) -> str:
    # Some hosts give "postgres://..." but SQLAlchemy wants "postgresql://..."
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


# Default = a SQLite file inside backend/ (zero installation needed)
_default_db = f"sqlite:///{(BASE_DIR / 'defect_detection.db').as_posix()}"
DATABASE_URL = _fix_db_url(os.getenv("DATABASE_URL") or _default_db)

MODEL_PATH = Path(os.getenv("MODEL_PATH") or (BASE_DIR / "saved_models" / "resnet50_defect.pth"))
if not MODEL_PATH.is_absolute():
    MODEL_PATH = BASE_DIR / MODEL_PATH
MODEL_URL = os.getenv("MODEL_URL", "")  # optional, used in deployment

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/bmp", "image/webp"}
