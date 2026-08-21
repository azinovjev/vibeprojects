# Photo → Video with Gemini

Upload a photo, pick (or write) a prompt, and generate a short video from it using
Google's [Veo](https://ai.google.dev/gemini-api/docs/video) model via the Gemini
API. Prompts are managed as configurable presets from the UI — no code changes
or redeploys needed to add, edit, or remove them.

## Architecture

```
backend/    FastAPI + SQLite (Python) — photo storage, prompt presets, Gemini/Veo integration
frontend/   React + TypeScript (Vite) — upload UI, prompt manager, generation status/history
```

- Uploaded photos and generated videos are stored on local disk (`backend/data/`),
  indexed in a small SQLite database (`backend/data/app.db`).
- When you submit a generation, the backend sends the photo bytes straight to
  Veo along with the prompt, using the `google-genai` SDK's async client. Veo
  runs as a long-running operation; the backend polls it until done, then
  downloads the resulting video locally.
- The one module that talks to Gemini (`backend/app/services/gemini_client.py`)
  is isolated behind a small interface (and accepts an injected client), so
  it's easy to unit test without hitting the real API, and easy to swap later.

## Prerequisites

- Python 3.9+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/apikey) (optional to start the
  app; required to actually generate a video)

## Backend setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
cp .env.example .env
# edit .env and set GEMINI_API_KEY=...
.venv/bin/uvicorn app.main:app --reload
```

The API serves on `http://localhost:8000`. `GET /api/health` reports whether a
Gemini key is configured. Without one, everything works except the final Veo
call, which fails with a clear "GEMINI_API_KEY is not configured" error
surfaced in the UI.

Run the backend test suite:

```bash
.venv/bin/pytest
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app serves on `http://localhost:5173` and proxies `/api` and `/files` to the
backend on port 8000 (see `vite.config.ts`).

Run the frontend tests:

```bash
npm test
```

## Configuring prompts

Prompt presets are managed entirely from the "Configure your prompt" section of
the UI — create, edit, or delete them there. A couple of example presets are
seeded automatically the first time the backend starts. Each generation can also
use a fully custom, one-off prompt instead of a saved preset.

## Configuration reference (`backend/.env`)

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | _(unset)_ | Your Gemini API key. Required to actually generate videos. |
| `GEMINI_DEFAULT_MODEL` | `veo-3.1-fast-generate-preview` | Default Veo model. Run `client.models.list()` against your key to see which Veo models it has access to — availability varies by account. |
| `GEMINI_DEFAULT_ASPECT_RATIO` | `16:9` | Default output aspect ratio (Veo supports `16:9` and `9:16`). |
| `GEMINI_DEFAULT_DURATION_SECONDS` | `8` | Default video duration in seconds. |
| `GEMINI_POLL_INTERVAL_SECONDS` | `10` | How often the backend polls the Veo operation for completion. |
| `GEMINI_POLL_TIMEOUT_SECONDS` | `600` | Give up waiting for Veo after this long. |
| `DATA_DIR` | `./data` | Where uploads, outputs, and the SQLite DB live. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed frontend origins. |
| `MAX_UPLOAD_BYTES` | `20971520` (20MB) | Max photo upload size. |

## Notes

- Verified end-to-end during development: photo upload, prompt preset
  selection, and generation submission all work. The backend was confirmed
  against the live Gemini API (listing available Veo models for the
  configured key, and validating the `generate_videos` / operation-polling /
  file-download call shapes against the installed `google-genai` SDK).
- Veo model availability and valid `duration_seconds` values can vary by
  account and change over time — if generation fails immediately with a model
  or parameter error, check `client.models.list()` / `client.models.get(...)`
  against your own key.
