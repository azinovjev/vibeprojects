from __future__ import annotations

from fastapi import Request

from app.config import Settings
from app.db import Database
from app.repositories.generation_repo import GenerationRepository
from app.repositories.photo_repo import PhotoRepository
from app.repositories.prompt_repo import PromptPresetRepository
from app.services.generation_service import GenerationService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_photo_repo(request: Request) -> PhotoRepository:
    return request.app.state.photo_repo


def get_prompt_repo(request: Request) -> PromptPresetRepository:
    return request.app.state.prompt_repo


def get_generation_repo(request: Request) -> GenerationRepository:
    return request.app.state.generation_repo


def get_generation_service(request: Request) -> GenerationService:
    return request.app.state.generation_service
