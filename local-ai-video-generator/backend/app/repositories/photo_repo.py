from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.db import Database


class PhotoRecord:
    def __init__(self, row) -> None:
        self.id: str = row["id"]
        self.original_filename: str = row["original_filename"]
        self.stored_filename: str = row["stored_filename"]
        self.content_type: str = row["content_type"]
        self.size_bytes: int = row["size_bytes"]
        self.created_at: str = row["created_at"]


class PhotoRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create(self, original_filename: str, stored_filename: str, content_type: str, size_bytes: int) -> PhotoRecord:
        photo_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._db.transaction() as cur:
            cur.execute(
                "INSERT INTO photos (id, original_filename, stored_filename, content_type, size_bytes, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (photo_id, original_filename, stored_filename, content_type, size_bytes, now),
            )
        return self.get(photo_id)

    def get(self, photo_id: str) -> PhotoRecord | None:
        with self._db.transaction() as cur:
            cur.execute("SELECT * FROM photos WHERE id = ?", (photo_id,))
            row = cur.fetchone()
        return PhotoRecord(row) if row else None

    def list(self) -> list[PhotoRecord]:
        with self._db.transaction() as cur:
            cur.execute("SELECT * FROM photos ORDER BY created_at DESC")
            rows = cur.fetchall()
        return [PhotoRecord(row) for row in rows]
