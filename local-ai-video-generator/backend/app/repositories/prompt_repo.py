from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.db import Database


class PromptPresetRecord:
    def __init__(self, row) -> None:
        self.id: str = row["id"]
        self.name: str = row["name"]
        self.prompt_text: str = row["prompt_text"]
        self.created_at: str = row["created_at"]
        self.updated_at: str = row["updated_at"]


class PromptPresetRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def list(self) -> list[PromptPresetRecord]:
        with self._db.transaction() as cur:
            cur.execute("SELECT * FROM prompt_presets ORDER BY created_at ASC")
            rows = cur.fetchall()
        return [PromptPresetRecord(row) for row in rows]

    def get(self, preset_id: str) -> PromptPresetRecord | None:
        with self._db.transaction() as cur:
            cur.execute("SELECT * FROM prompt_presets WHERE id = ?", (preset_id,))
            row = cur.fetchone()
        return PromptPresetRecord(row) if row else None

    def create(self, name: str, prompt_text: str) -> PromptPresetRecord:
        preset_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._db.transaction() as cur:
            cur.execute(
                "INSERT INTO prompt_presets (id, name, prompt_text, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (preset_id, name, prompt_text, now, now),
            )
        return self.get(preset_id)

    def update(self, preset_id: str, name: str, prompt_text: str) -> PromptPresetRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self._db.transaction() as cur:
            cur.execute(
                "UPDATE prompt_presets SET name = ?, prompt_text = ?, updated_at = ? WHERE id = ?",
                (name, prompt_text, now, preset_id),
            )
        return self.get(preset_id)

    def delete(self, preset_id: str) -> bool:
        with self._db.transaction() as cur:
            cur.execute("DELETE FROM prompt_presets WHERE id = ?", (preset_id,))
            return cur.rowcount > 0
