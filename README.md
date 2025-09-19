# AI Voiceover Easy

AI Voiceover Easy is a full-stack prototype that transforms uploaded manuscripts into downloadable audio narration. It provides a modern React dashboard backed by a FastAPI service with document parsing, placeholder TTS generation, and JWT authentication.

## Features

- 🔐 Email/password authentication with hashed credentials and JWT access tokens.
- 📄 Text ingestion via rich text input or document upload (`.txt`, `.pdf`, `.docx`).
- 🗣️ Voice catalogue with language, accent, and style metadata.
- 🎧 Background audio synthesis (placeholder waveform ready to be swapped for a real TTS provider).
- 📚 Project history with inline audio preview and download.
- 🧪 End-to-end backend test covering registration, login, voice retrieval, project creation, polling, and download.

## Project Structure

```
.
├── backend/             # FastAPI application
│   ├── app/
│   │   ├── api/         # Routers (auth, projects, voices)
│   │   ├── core/        # Config, database, security helpers
│   │   ├── models/      # SQLModel ORM entities
│   │   ├── schemas/     # Pydantic response/request models
│   │   ├── services/    # Audio synthesis + voice seeding
│   │   └── utils/       # Text extraction helpers
│   └── tests/           # Pytest suite
├── frontend/            # React (Vite + TypeScript) dashboard
│   └── src/
│       ├── components/  # Future component library
│       ├── hooks/       # `useAuth` hook
│       ├── lib/         # Axios client
│       └── styles/      # Global + module styles
└── docs/ARCHITECTURE.md # Detailed architecture notes
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables:

- `SECRET_KEY` – JWT signing secret (default: `change-me`).
- `DATABASE_URL` – SQLAlchemy URL (default: local SQLite file).
- `STORAGE_DIR` – Directory for generated audio files.
- `ALLOW_REGISTRATION` – (optional) set to `false` to disable `/auth/signup`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies `/api` requests to the FastAPI backend (`http://localhost:8000`). Configure a different backend host by setting `VITE_API_BASE_URL` in a `.env` file.

## Testing

```bash
cd backend
pytest
```

## Next Steps

Refer to [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for roadmap ideas including production-grade TTS integration, cloud storage, billing, and OAuth providers.
