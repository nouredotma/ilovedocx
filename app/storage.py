import uuid
import os
import time
from pathlib import Path
import shutil

# STORAGE_DIR is at the root level, two levels up from this file (app/storage.py)
STORAGE_DIR = Path(__file__).parent.parent.absolute() / "storage"

# Ensure storage directory exists
STORAGE_DIR.mkdir(exist_ok=True)

def create_session() -> str:
    """Generates and returns a new UUID string."""
    return str(uuid.uuid4())

def get_file_path(session_id: str) -> Path:
    """Returns the path to the .docx file for a given session."""
    return STORAGE_DIR / f"{session_id}.docx"

def save_upload(session_id: str, file_bytes: bytes):
    """Writes the uploaded file bytes to the storage directory."""
    with open(get_file_path(session_id), "wb") as f:
        f.write(file_bytes)

def file_exists(session_id: str) -> bool:
    """Checks if the document for a session exists."""
    return get_file_path(session_id).exists()

def cleanup_old_files():
    """Deletes files older than 2 hours (7200 seconds)."""
    current_time = time.time()
    for file_path in STORAGE_DIR.glob("*.docx"):
        if current_time - file_path.stat().st_mtime > 7200:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
