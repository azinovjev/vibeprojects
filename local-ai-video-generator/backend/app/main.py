from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db import Database
from app.repositories.generation_repo import GenerationRepository
from app.repositories.photo_repo import PhotoRepository
from app.repositories.prompt_repo import PromptPresetRepository
from app.routers import generations, photos, prompts
from app.services.gemini_client import GeminiClient
from app.services.generation_service import GenerationService

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.ensure_directories()

    db = Database(settings.db_path)
    photo_repo = PhotoRepository(db)
    prompt_repo = PromptPresetRepository(db)
    generation_repo = GenerationRepository(db)
    gemini_client = GeminiClient(api_key=settings.gemini_api_key)
    generation_service = GenerationService(settings, gemini_client, generation_repo, photo_repo)

    app.state.settings = settings
    app.state.db = db
    app.state.photo_repo = photo_repo
    app.state.prompt_repo = prompt_repo
    app.state.generation_repo = generation_repo
    app.state.generation_service = generation_service
    app.state.background_tasks = set()

    app.mount("/files/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
    app.mount("/files/outputs", StaticFiles(directory=settings.outputs_dir), name="outputs")

    yield

    for task in list(app.state.background_tasks):
        task.cancel()
    db.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Gemini Photo-to-Video Workflow", lifespan=lifespan)
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(photos.router)
    app.include_router(prompts.router)
    app.include_router(generations.router)

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "gemini_configured": bool(settings.gemini_api_key)}

    return app


app = create_app()
