from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.db import Database
from app.schemas import GenerationStatus


class GenerationRecord:
    def __init__(self, row) -> None:
        self.id: str = row["id"]
        self.photo_id: str = row["photo_id"]
        self.prompt_text: str = row["prompt_text"]
        self.model: str = row["model"]
        self.ratio: str = row["ratio"]
        self.duration: int = row["duration"]
        self.seed: int | None = row["seed"]
        self.status: str = row["status"]
        self.operation_name: str | None = row["operation_name"]
        self.output_filename: str | None = row["output_filename"]
        self.error_message: str | None = row["error_message"]
        self.created_at: str = row["created_at"]
        self.updated_at: str = row["updated_at"]


class GenerationRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create(
        self,
        photo_id: str,
        prompt_text: str,
        model: str,
        ratio: str,
        duration: int,
        seed: int | None,
    ) -> GenerationRecord:
        generation_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._db.transaction() as cur:
            cur.execute(
                """
                INSERT INTO generations
                    (id, photo_id, prompt_text, model, ratio, duration, seed, status,
                     operation_name, output_filename, error_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?)
                """,
                (
                    generation_id,
                    photo_id,
                    prompt_text,
                    model,
                    ratio,
                    duration,
                    seed,
                    GenerationStatus.PENDING.value,
                    now,
                    now,
                ),
            )
        return self.get(generation_id)

    def get(self, generation_id: str) -> GenerationRecord | None:
        with self._db.transaction() as cur:
            cur.execute("SELECT * FROM generations WHERE id = ?", (generation_id,))
            row = cur.fetchone()
        return GenerationRecord(row) if row else None

    def list(self) -> list[GenerationRecord]:
        with self._db.transaction() as cur:
            cur.execute("SELECT * FROM generations ORDER BY created_at DESC")
            rows = cur.fetchall()
        return [GenerationRecord(row) for row in rows]

    def update_status(
        self,
        generation_id: str,
        status: GenerationStatus,
        operation_name: str | None = None,
        output_filename: str | None = None,
        error_message: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._db.transaction() as cur:
            cur.execute(
                """
                UPDATE generations
                SET status = ?,
                    operation_name = COALESCE(?, operation_name),
                    output_filename = COALESCE(?, output_filename),
                    error_message = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (status.value, operation_name, output_filename, error_message, now, generation_id),
            )
