from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Photo(BaseModel):
    id: str
    original_filename: str
    content_type: str
    size_bytes: int
    url: str
    created_at: str


class PromptPreset(BaseModel):
    id: str
    name: str
    prompt_text: str
    created_at: str
    updated_at: str


class PromptPresetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    prompt_text: str = Field(min_length=1, max_length=2000)


class PromptPresetUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    prompt_text: str = Field(min_length=1, max_length=2000)


class GenerationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class GenerationCreate(BaseModel):
    photo_id: str
    prompt_text: str = Field(min_length=1, max_length=2000)
    model: str | None = None
    ratio: str | None = None
    duration: int | None = None
    seed: int | None = None


class Generation(BaseModel):
    id: str
    photo_id: str
    prompt_text: str
    model: str
    ratio: str
    duration: int
    seed: int | None
    status: GenerationStatus
    operation_name: str | None
    video_url: str | None
    error_message: str | None
    created_at: str
    updated_at: str
