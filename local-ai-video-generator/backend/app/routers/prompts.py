from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_prompt_repo
from app.repositories.prompt_repo import PromptPresetRecord, PromptPresetRepository
from app.schemas import PromptPreset, PromptPresetCreate, PromptPresetUpdate

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


def _to_schema(preset: PromptPresetRecord) -> PromptPreset:
    return PromptPreset(
        id=preset.id,
        name=preset.name,
        prompt_text=preset.prompt_text,
        created_at=preset.created_at,
        updated_at=preset.updated_at,
    )


@router.get("", response_model=list[PromptPreset])
async def list_prompts(repo: PromptPresetRepository = Depends(get_prompt_repo)) -> list[PromptPreset]:
    return [_to_schema(p) for p in repo.list()]


@router.post("", response_model=PromptPreset, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    payload: PromptPresetCreate, repo: PromptPresetRepository = Depends(get_prompt_repo)
) -> PromptPreset:
    preset = repo.create(payload.name, payload.prompt_text)
    return _to_schema(preset)


@router.put("/{preset_id}", response_model=PromptPreset)
async def update_prompt(
    preset_id: str, payload: PromptPresetUpdate, repo: PromptPresetRepository = Depends(get_prompt_repo)
) -> PromptPreset:
    if repo.get(preset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt preset not found.")
    preset = repo.update(preset_id, payload.name, payload.prompt_text)
    return _to_schema(preset)


@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_prompt(preset_id: str, repo: PromptPresetRepository = Depends(get_prompt_repo)) -> None:
    if not repo.delete(preset_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt preset not found.")
