from __future__ import annotations

import asyncio
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

# API contract per https://ai.google.dev/gemini-api/docs/video (Veo via the
# Gemini Developer API, google-genai SDK's async client).


class GeminiAPIError(Exception):
    pass


class GeminiNotConfiguredError(GeminiAPIError):
    def __init__(self) -> None:
        super().__init__("GEMINI_API_KEY is not configured. Add it to backend/.env and restart the server.")


class GeminiClient:
    """Thin wrapper around the Veo image-to-video flow of the Gemini API.

    Accepts a pre-built `client` for tests (a fake with the same
    `.aio.models` / `.aio.operations` / `.aio.files` surface); otherwise
    builds a real `genai.Client` from `api_key`.
    """

    def __init__(self, api_key: str | None, client: Any | None = None) -> None:
        self._client = client if client is not None else (genai.Client(api_key=api_key) if api_key else None)

    def _require_client(self) -> Any:
        if self._client is None:
            raise GeminiNotConfiguredError()
        return self._client

    async def generate_video(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt_text: str,
        model: str,
        aspect_ratio: str,
        duration_seconds: int,
        seed: int | None = None,
    ) -> Any:
        client = self._require_client()
        try:
            return await client.aio.models.generate_videos(
                model=model,
                prompt=prompt_text,
                image=types.Image(image_bytes=image_bytes, mime_type=mime_type),
                config=types.GenerateVideosConfig(
                    aspect_ratio=aspect_ratio,
                    duration_seconds=duration_seconds,
                    seed=seed,
                ),
            )
        except genai_errors.APIError as exc:
            raise GeminiAPIError(f"Gemini API error: {exc.message}") from exc

    async def wait_until_done(self, operation: Any, poll_interval: float, timeout: float) -> Any:
        client = self._require_client()
        deadline = asyncio.get_event_loop().time() + timeout
        while not operation.done:
            if asyncio.get_event_loop().time() > deadline:
                raise GeminiAPIError("Timed out waiting for Veo to finish generating the video.")
            await asyncio.sleep(poll_interval)
            try:
                operation = await client.aio.operations.get(operation)
            except genai_errors.APIError as exc:
                raise GeminiAPIError(f"Gemini API error: {exc.message}") from exc

        if getattr(operation, "error", None):
            raise GeminiAPIError(f"Veo generation failed: {operation.error}")
        return operation

    async def download_video_bytes(self, operation: Any) -> bytes:
        client = self._require_client()
        generated = operation.response.generated_videos
        if not generated:
            raise GeminiAPIError("Veo operation succeeded but returned no video.")
        video = generated[0].video
        try:
            return await client.aio.files.download(file=video)
        except genai_errors.APIError as exc:
            raise GeminiAPIError(f"Gemini API error: {exc.message}") from exc
