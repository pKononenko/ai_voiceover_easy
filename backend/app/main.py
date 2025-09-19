from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, projects, voices
from .core.config import get_settings
from .core.database import get_session, init_db
from .services.voices import ensure_default_voices


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    with get_session() as session:
        ensure_default_voices(session)


app.include_router(auth.router)
app.include_router(voices.router)
app.include_router(projects.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "AI Voiceover Easy API", "version": "0.1.0"}
