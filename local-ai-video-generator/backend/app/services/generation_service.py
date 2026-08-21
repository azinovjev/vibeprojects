from __future__ import annotations

import logging

from app.config import Settings
from app.repositories.generation_repo import GenerationRepository
from app.repositories.photo_repo import PhotoRepository
from app.schemas import GenerationStatus
from app.services.gemini_client import GeminiAPIError, GeminiClient

logger = logging.getLogger(__name__)


class GenerationService:
    def __init__(
        self,
        settings: Settings,
        gemini_client: GeminiClient,
        generation_repo: GenerationRepository,
        photo_repo: PhotoRepository,
    ) -> None:
        self._settings = settings
        self._gemini = gemini_client
        self._generations = generation_repo
        self._photos = photo_repo

    async def run(self, generation_id: str) -> None:
        """Drive one generation from PENDING through to a terminal state.

        Intended to be scheduled as a fire-and-forget asyncio task right after
        the generation row is created, so the HTTP request that created it can
        return immediately and the client polls for progress separately.
        """
        generation = self._generations.get(generation_id)
        if generation is None:
            logger.error("generation %s not found when starting run", generation_id)
            return

        try:
            photo = self._photos.get(generation.photo_id)
            image_path = self._settings.uploads_dir / photo.stored_filename
            image_bytes = image_path.read_bytes()

            operation = await self._gemini.generate_video(
                image_bytes=image_bytes,
                mime_type=photo.content_type,
                prompt_text=generation.prompt_text,
                model=generation.model,
                aspect_ratio=generation.ratio,
                duration_seconds=generation.duration,
                seed=generation.seed,
            )
            self._generations.update_status(
                generation_id, GenerationStatus.RUNNING, operation_name=getattr(operation, "name", None)
            )

            completed = await self._gemini.wait_until_done(
                operation,
                poll_interval=self._settings.gemini_poll_interval_seconds,
                timeout=self._settings.gemini_poll_timeout_seconds,
            )
            video_bytes = await self._gemini.download_video_bytes(completed)

            output_filename = f"{generation_id}.mp4"
            (self._settings.outputs_dir / output_filename).write_bytes(video_bytes)

            self._generations.update_status(
                generation_id, GenerationStatus.SUCCEEDED, output_filename=output_filename
            )
        except GeminiAPIError as exc:
            logger.warning("generation %s failed: %s", generation_id, exc)
            self._generations.update_status(generation_id, GenerationStatus.FAILED, error_message=str(exc))
        except Exception as exc:  # noqa: BLE001 - surface any unexpected failure to the user
            logger.exception("generation %s failed unexpectedly", generation_id)
            self._generations.update_status(
                generation_id, GenerationStatus.FAILED, error_message=f"Unexpected error: {exc}"
            )
