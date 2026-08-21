from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from google.genai import errors as genai_errors

from app.services.gemini_client import GeminiAPIError, GeminiClient, GeminiNotConfiguredError


def make_api_error(message: str) -> genai_errors.APIError:
    return genai_errors.APIError(400, {"message": message, "status": "INVALID_ARGUMENT"})


def fake_operation(done: bool, name: str = "operations/abc123", error=None, video_bytes: bytes | None = None):
    response = None
    if video_bytes is not None:
        video = SimpleNamespace(video_bytes=video_bytes)
        response = SimpleNamespace(generated_videos=[SimpleNamespace(video=video)])
    return SimpleNamespace(done=done, name=name, error=error, response=response)


def make_fake_client(**overrides) -> SimpleNamespace:
    aio = SimpleNamespace(
        models=SimpleNamespace(generate_videos=overrides.get("generate_videos", AsyncMock())),
        operations=SimpleNamespace(get=overrides.get("operations_get", AsyncMock())),
        files=SimpleNamespace(download=overrides.get("files_download", AsyncMock())),
    )
    return SimpleNamespace(aio=aio)


@pytest.mark.asyncio
async def test_generate_video_without_api_key_raises_not_configured():
    client = GeminiClient(api_key=None)
    with pytest.raises(GeminiNotConfiguredError):
        await client.generate_video(b"bytes", "image/png", "prompt", "veo-3.0-fast-generate-001", "16:9", 8)


@pytest.mark.asyncio
async def test_generate_video_success_returns_operation():
    operation = fake_operation(done=False)
    fake_client = make_fake_client(generate_videos=AsyncMock(return_value=operation))
    client = GeminiClient(api_key=None, client=fake_client)

    result = await client.generate_video(b"bytes", "image/png", "prompt", "veo-3.0-fast-generate-001", "16:9", 8)

    assert result is operation
    fake_client.aio.models.generate_videos.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_video_wraps_api_error():
    fake_client = make_fake_client(generate_videos=AsyncMock(side_effect=make_api_error("invalid API key")))
    client = GeminiClient(api_key=None, client=fake_client)

    with pytest.raises(GeminiAPIError, match="invalid API key"):
        await client.generate_video(b"bytes", "image/png", "prompt", "veo-3.0-fast-generate-001", "16:9", 8)


@pytest.mark.asyncio
async def test_wait_until_done_polls_until_operation_completes():
    running = fake_operation(done=False)
    completed = fake_operation(done=True)
    fake_client = make_fake_client(operations_get=AsyncMock(return_value=completed))
    client = GeminiClient(api_key=None, client=fake_client)

    result = await client.wait_until_done(running, poll_interval=0.01, timeout=5)

    assert result is completed


@pytest.mark.asyncio
async def test_wait_until_done_raises_on_operation_error():
    running = fake_operation(done=False)
    failed = fake_operation(done=True, error={"message": "content policy violation"})
    fake_client = make_fake_client(operations_get=AsyncMock(return_value=failed))
    client = GeminiClient(api_key=None, client=fake_client)

    with pytest.raises(GeminiAPIError, match="content policy violation"):
        await client.wait_until_done(running, poll_interval=0.01, timeout=5)


@pytest.mark.asyncio
async def test_wait_until_done_times_out():
    running = fake_operation(done=False)
    fake_client = make_fake_client(operations_get=AsyncMock(return_value=fake_operation(done=False)))
    client = GeminiClient(api_key=None, client=fake_client)

    with pytest.raises(GeminiAPIError, match="Timed out"):
        await client.wait_until_done(running, poll_interval=0.02, timeout=0.05)


@pytest.mark.asyncio
async def test_download_video_bytes_returns_bytes():
    operation = fake_operation(done=True, video_bytes=b"placeholder")
    fake_client = make_fake_client(files_download=AsyncMock(return_value=b"fake-video-bytes"))
    client = GeminiClient(api_key=None, client=fake_client)

    result = await client.download_video_bytes(operation)

    assert result == b"fake-video-bytes"
    fake_client.aio.files.download.assert_awaited_once()


@pytest.mark.asyncio
async def test_download_video_bytes_raises_when_no_videos():
    operation = fake_operation(done=True)
    operation.response = SimpleNamespace(generated_videos=[])
    fake_client = make_fake_client()
    client = GeminiClient(api_key=None, client=fake_client)

    with pytest.raises(GeminiAPIError, match="no video"):
        await client.download_video_bytes(operation)
