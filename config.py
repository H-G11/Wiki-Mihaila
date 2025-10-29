import os
from pathlib import Path

BASE_DIR = Path(file).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change-this-secret"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR/'wiki.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or str(BASE_DIR / "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB