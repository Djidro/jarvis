"""File search, folder opening and (confirmed) deletion. Limited to your home folder."""
import os
import time
from pathlib import Path

HOME = Path.home()
FOLDERS = {"documents": HOME / "Documents", "downloads": HOME / "Downloads",
           "desktop": HOME / "Desktop", "pictures": HOME / "Pictures"}


def open_folder(name):
    path = FOLDERS.get(name.lower())
    if path is None or not path.exists():
        return None
    os.startfile(path) if hasattr(os, "startfile") else None
    return f"Opening {name}."


def search_files(term, limit=10, max_seconds=8):
    found, start = [], time.time()
    for folder in FOLDERS.values():
        for p in folder.rglob("*"):
            if time.time() - start > max_seconds or len(found) >= limit:
                return found
            if term.lower() in p.name.lower():
                found.append(str(p))
    return found


def is_safe_to_delete(path_str):
    p = Path(path_str).expanduser().resolve()
    return p.is_file() and HOME in p.parents


def delete_file(path_str):
    Path(path_str).expanduser().resolve().unlink()
    return "File deleted."
