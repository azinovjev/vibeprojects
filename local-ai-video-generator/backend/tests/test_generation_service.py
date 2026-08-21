from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import Settings
from app.db import Database
from app.repositories.generation_repo import GenerationRepository
from app.repositories.photo_repo import PhotoRepository
from app.schemas import GenerationStatus
from app.services.generation_service import GenerationService
from app.services.gemini_client import GeminiAPIError


class FakeGeminiClient:
    def __init__(self, outcome: str, video_bytes: bytes = b"fake-video-bytes") -> None:
        self.outcome = outcome
        self.video_bytes = video_bytes

    async def generate_video(self, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(name="operations/abc123", done=False)

    async def wait_until_done(self, operation, poll_interval, timeout) -> SimpleNamespace:
        if self.outcome == "FAILED":
            raise GeminiAPIError("Veo generation failed: content policy violation")
        return SimpleNamespace(done=True)

    async def download_video_bytes(self, operation) -> bytes:
        return self.video_bytes


class ErroringGeminiClient:
    async def generate_video(self, **kwargs):
        raise GeminiAPIError("Gemini API error: invalid API key")

    async def wait_until_done(self, operation, poll_interval, timeout):
        raise AssertionError("should not be called")

    async def download_video_bytes(self, operation):
        raise AssertionError("should not be called")


def _build_service(tmp_path: Path, gemini_client):
    settings = Settings(data_dir=tmp_path / "data", gemini_poll_interval_seconds=0.01)
    settings.ensure_directories()
    db = Database(settings.db_path)
    photo_repo = PhotoRepository(db)
    generation_repo = GenerationRepository(db)
    service = GenerationService(settings, gemini_client, generation_repo, photo_repo)
    return settings, photo_repo, generation_repo, service


def _create_photo(settings: Settings, photo_repo: PhotoRepository):
    (settings.uploads_dir / "photo.png").write_bytes(b"fake-image-bytes")
    return photo_repo.create("photo.png", "photo.png", "image/png", 17)


@pytest.mark.asyncio
async def test_generation_succeeds_and_saves_video(tmp_path: Path):
    settings, photo_repo, generation_repo, service = _build_service(
        tmp_path, FakeGeminiClient(outcome="SUCCEEDED")
    )
    photo = _create_photo(settings, photo_repo)
    generation = generation_repo.create(photo.id, "make it move", "veo-3.0-fast-generate-001", "16:9", 8, None)

    await service.run(generation.id)

    result = generation_repo.get(generation.id)
    assert result.status == GenerationStatus.SUCCEEDED.value
    assert result.operation_name == "operations/abc123"
    assert result.output_filename == f"{generation.id}.mp4"
    assert (settings.outputs_dir / result.output_filename).read_bytes() == b"fake-video-bytes"


@pytest.mark.asyncio
async def test_generation_records_failure_from_gemini_operation(tmp_path: Path):
    settings, photo_repo, generation_repo, service = _build_service(tmp_path, FakeGeminiClient(outcome="FAILED"))
    photo = _create_photo(settings, photo_repo)
    generation = generation_repo.create(photo.id, "make it move", "veo-3.0-fast-generate-001", "16:9", 8, None)

    await service.run(generation.id)

    result = generation_repo.get(generation.id)
    assert result.status == GenerationStatus.FAILED.value
    assert "content policy violation" in result.error_message


@pytest.mark.asyncio
async def test_generation_records_failure_when_gemini_not_configured(tmp_path: Path):
    settings, photo_repo, generation_repo, service = _build_service(tmp_path, ErroringGeminiClient())
    photo = _create_photo(settings, photo_repo)
    generation = generation_repo.create(photo.id, "make it move", "veo-3.0-fast-generate-001", "16:9", 8, None)

    await service.run(generation.id)

    result = generation_repo.get(generation.id)
    assert result.status == GenerationStatus.FAILED.value
    assert "invalid API key" in result.error_message
