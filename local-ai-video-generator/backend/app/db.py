from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS photos (
    id TEXT PRIMARY KEY,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_presets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generations (
    id TEXT PRIMARY KEY,
    photo_id TEXT NOT NULL REFERENCES photos(id),
    prompt_text TEXT NOT NULL,
    model TEXT NOT NULL,
    ratio TEXT NOT NULL,
    duration INTEGER NOT NULL,
    seed INTEGER,
    status TEXT NOT NULL,
    operation_name TEXT,
    output_filename TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

SEED_PRESETS = [
    (
        "Gentle parallax",
        "Subtle cinematic parallax movement, soft camera drift, natural lighting, "
        "keep the subject sharp and the scene realistic.",
    ),
    (
        "Dreamy zoom-in",
        "Slow, dreamy zoom into the center of the frame, gentle floating particles, "
        "soft depth of field, warm cinematic color grade.",
    ),
]


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class Database:
    """Thin wrapper around a single sqlite3 connection shared across the app.

    SQLite serializes writes internally; a short-lived cursor per operation
    keeps concurrent request handling safe without a connection pool.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._conn = _connect(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        with self.transaction() as cur:
            cur.executescript(SCHEMA)
        self._seed_presets_if_empty()

    def _seed_presets_if_empty(self) -> None:
        from datetime import datetime, timezone
        from uuid import uuid4

        with self.transaction() as cur:
            cur.execute("SELECT COUNT(*) FROM prompt_presets")
            (count,) = cur.fetchone()
            if count:
                return
            now = datetime.now(timezone.utc).isoformat()
            for name, prompt_text in SEED_PRESETS:
                cur.execute(
                    "INSERT INTO prompt_presets (id, name, prompt_text, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (str(uuid4()), name, prompt_text, now, now),
                )

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Cursor]:
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    def close(self) -> None:
        self._conn.close()
