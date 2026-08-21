from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import Settings
from app.dependencies import get_generation_repo, get_generation_service, get_photo_repo, get_settings
from app.repositories.generation_repo import GenerationRecord, GenerationRepository
from app.repositories.photo_repo import PhotoRepository
from app.schemas import Generation, GenerationCreate, GenerationStatus
from app.services.generation_service import GenerationService

router = APIRouter(prefix="/api/generations", tags=["generations"])


def _to_schema(generation: GenerationRecord) -> Generation:
    video_url = f"/files/outputs/{generation.output_filename}" if generation.output_filename else None
    return Generation(
        id=generation.id,
        photo_id=generation.photo_id,
        prompt_text=generation.prompt_text,
        model=generation.model,
        ratio=generation.ratio,
        duration=generation.duration,
        seed=generation.seed,
        status=GenerationStatus(generation.status),
        operation_name=generation.operation_name,
        video_url=video_url,
        error_message=generation.error_message,
        created_at=generation.created_at,
        updated_at=generation.updated_at,
    )


@router.post("", response_model=Generation, status_code=status.HTTP_201_CREATED)
async def create_generation(
    payload: GenerationCreate,
    request: Request,
    settings: Settings = Depends(get_settings),
    photo_repo: PhotoRepository = Depends(get_photo_repo),
    generation_repo: GenerationRepository = Depends(get_generation_repo),
    generation_service: GenerationService = Depends(get_generation_service),
) -> Generation:
    if photo_repo.get(payload.photo_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found.")

    generation = generation_repo.create(
        photo_id=payload.photo_id,
        prompt_text=payload.prompt_text,
        model=payload.model or settings.gemini_default_model,
        ratio=payload.ratio or settings.gemini_default_aspect_ratio,
        duration=payload.duration or settings.gemini_default_duration_seconds,
        seed=payload.seed,
    )

    background_tasks: set[asyncio.Task] = request.app.state.background_tasks
    task = asyncio.create_task(generation_service.run(generation.id))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return _to_schema(generation)


@router.get("", response_model=list[Generation])
async def list_generations(generation_repo: GenerationRepository = Depends(get_generation_repo)) -> list[Generation]:
    return [_to_schema(g) for g in generation_repo.list()]


@router.get("/{generation_id}", response_model=Generation)
async def get_generation(
    generation_id: str, generation_repo: GenerationRepository = Depends(get_generation_repo)
) -> Generation:
    generation = generation_repo.get(generation_id)
    if generation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found.")
    return _to_schema(generation)
