# AI Voiceover Easy – System Overview

## High-level Architecture

```
[React Frontend (Vite + TypeScript)] --HTTP--> [FastAPI Backend]
                                           |
                                           +--> [SQLite (development) / PostgreSQL (production)]
                                           |
                                           +--> [Object storage (local placeholder, S3/Supabase in production)]
```

The frontend communicates with the FastAPI backend via a JSON/REST interface. File uploads and audio downloads use multipart/form-data and streaming responses respectively. Authentication is handled using JWT bearer tokens issued by the backend.

## Backend Components

- **FastAPI application** (`backend/app/main.py`)
  - Applies CORS middleware, registers routers, and initialises the database.
- **Authentication** (`backend/app/api/auth.py`)
  - Email/password registration and login with hashed passwords (bcrypt) and JWT access tokens.
- **Projects** (`backend/app/api/projects.py`)
  - Handles uploads, text extraction (TXT/PDF/DOCX), background audio generation, history, and download endpoints.
- **Voices** (`backend/app/api/voices.py`)
  - Serves a curated catalogue of demo voices; seeds default voices on startup.
- **Services**
  - `audio.py` – generates placeholder waveform audio (to be swapped for a real TTS provider).
  - `voices.py` – seeds the voice catalogue.
  - `text_extraction.py` – extracts text from uploaded documents.
- **Data Models** (`backend/app/models/entities.py`)
  - SQLModel ORM models with relationships for users, voices, and projects.
- **Database** (`backend/app/core/database.py`)
  - SQLite for local development; easily swapped for Postgres via `DATABASE_URL` env variable.
- **Configuration** (`backend/app/core/config.py`)
  - Centralises environment configuration via Pydantic BaseSettings.

## Frontend Components

- **React application shell** (`frontend/src/App.tsx`)
  - Implements authentication flow, project upload form, history view, and inline audio playback.
- **State and hooks**
  - `useAuth` hook persists JWT tokens in localStorage and exposes authentication helpers.
- **API client** (`frontend/src/lib/api.ts`)
  - Axios instance with configurable base URL (`VITE_API_BASE_URL`).
- **Styling** (`frontend/src/styles/*.css`)
  - Lightweight custom CSS inspired by Tailwind's spacing/colour system.

## Local Development Workflow

1. **Backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Visit `http://localhost:5173` — requests are proxied to the FastAPI backend at `http://localhost:8000`.

## Testing

- `pytest` under `backend/` exercises the primary happy-path workflow: registration, login, project creation, polling, and audio download.

## Future Enhancements

- Replace placeholder waveform generator with production-grade TTS (OpenAI, ElevenLabs, etc.).
- Swap SQLite for managed Postgres and configure Alembic migrations.
- Integrate real file/object storage (Supabase Storage or S3) and signed download URLs.
- Implement usage metering and billing (Stripe) with quotas and reporting.
- Add OAuth providers (Supabase Auth / Firebase) and rate limiting via Redis.
- Expand frontend with progress indicators, pagination, and in-app payments.
