from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.config import Settings
from app.dependencies import get_photo_repo, get_settings
from app.repositories.photo_repo import PhotoRecord, PhotoRepository
from app.schemas import Photo

router = APIRouter(prefix="/api/photos", tags=["photos"])

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _to_schema(photo: PhotoRecord) -> Photo:
    return Photo(
        id=photo.id,
        original_filename=photo.original_filename,
        content_type=photo.content_type,
        size_bytes=photo.size_bytes,
        url=f"/files/uploads/{photo.stored_filename}",
        created_at=photo.created_at,
    )


@router.post("", response_model=Photo, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile,
    settings: Settings = Depends(get_settings),
    photo_repo: PhotoRepository = Depends(get_photo_repo),
) -> Photo:
    extension = ALLOWED_CONTENT_TYPES.get(file.content_type)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: jpeg, png, webp.",
        )

    contents = await file.read()
    if len(contents) > settings.max_upload_bytes:
        max_mb = settings.max_upload_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {max_mb:.0f}MB upload limit.",
        )
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    stored_filename = f"{uuid4()}{extension}"
    destination = settings.uploads_dir / stored_filename
    Path(destination).write_bytes(contents)

    photo = photo_repo.create(
        original_filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        size_bytes=len(contents),
    )
    return _to_schema(photo)


@router.get("", response_model=list[Photo])
async def list_photos(photo_repo: PhotoRepository = Depends(get_photo_repo)) -> list[Photo]:
    return [_to_schema(photo) for photo in photo_repo.list()]
