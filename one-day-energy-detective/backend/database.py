"""
JSON File-Based Database Layer.
Replaces SQLite with plain JSON files to avoid _sqlite3.dll dependency.
Uses Python's built-in json module with file locking via threading.Lock().
Data directory: data/
Files: users.json, sessions.json, households.json, appliances.json
"""

import json
import os
import threading
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from backend.config import DATABASE_PATH

# ── Storage paths ──────────────────────────────────────────────────────────────
DATA_DIR = os.path.dirname(DATABASE_PATH)

_PATHS = {
    "users":       os.path.join(DATA_DIR, "users.json"),
    "sessions":    os.path.join(DATA_DIR, "sessions.json"),
    "households":  os.path.join(DATA_DIR, "households.json"),
    "appliances":  os.path.join(DATA_DIR, "appliances.json"),
}

# One lock per collection – prevents concurrent write corruption
_LOCKS: Dict[str, threading.Lock] = {k: threading.Lock() for k in _PATHS}


# ── Low-level read / write ─────────────────────────────────────────────────────

def _read(collection: str) -> List[Dict[str, Any]]:
    path = _PATHS[collection]
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return []


def _write(collection: str, records: List[Dict[str, Any]]) -> None:
    path = _PATHS[collection]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2, default=str)


# ── Public helpers used by models ──────────────────────────────────────────────

def _next_id(records: List[Dict[str, Any]]) -> int:
    """Returns auto-increment integer id (1-based)."""
    if not records:
        return 1
    return max(r.get("id", 0) for r in records) + 1


class _JsonDB:
    """
    Minimal transactional-style context manager around a single collection.
    Usage:
        with JsonDB("users") as db:
            db.records   <- list of dicts
            db.append({...})
            db.save()   <- automatically called on __exit__ if no exception
    """
    def __init__(self, collection: str):
        self.collection = collection
        self._lock = _LOCKS[collection]
        self.records: List[Dict[str, Any]] = []
        self._dirty = False

    def __enter__(self):
        self._lock.acquire()
        self.records = _read(self.collection)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None and self._dirty:
                _write(self.collection, self.records)
        finally:
            self._lock.release()

    def append(self, record: Dict[str, Any]) -> int:
        new_id = _next_id(self.records)
        record["id"] = new_id
        self.records.append(record)
        self._dirty = True
        return new_id

    def save(self) -> None:
        self._dirty = True


def JsonDB(collection: str) -> _JsonDB:
    """Factory so callers can write `with JsonDB('users') as db:`."""
    return _JsonDB(collection)


# ── Compatibility shim (get_db is not used by new models but kept for tests) ──

@contextmanager
def get_db():
    """Legacy stub – JSON models don't use this but test imports may reference it."""
    yield None


def init_db() -> None:
    """Creates the data directory and empty JSON files if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    for path in _PATHS.values():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump([], fh)
