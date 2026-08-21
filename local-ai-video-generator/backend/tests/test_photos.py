from __future__ import annotations

import io

from tests.conftest import upload_sample_photo


def test_upload_photo_success(app_client, sample_image_bytes):
    photo = upload_sample_photo(app_client, sample_image_bytes)
    assert photo["original_filename"] == "sample.png"
    assert photo["content_type"] == "image/png"
    assert photo["url"].startswith("/files/uploads/")

    listed = app_client.get("/api/photos").json()
    assert len(listed) == 1
    assert listed[0]["id"] == photo["id"]


def test_upload_photo_rejects_bad_content_type(app_client):
    response = app_client.post(
        "/api/photos",
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 415


def test_upload_photo_rejects_oversized_file(app_client, monkeypatch):
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "max_upload_bytes", 10)

    response = app_client.post(
        "/api/photos",
        files={"file": ("sample.png", io.BytesIO(b"x" * 100), "image/png")},
    )
    assert response.status_code == 413


def test_upload_photo_rejects_empty_file(app_client):
    response = app_client.post(
        "/api/photos",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
    )
    assert response.status_code == 400
