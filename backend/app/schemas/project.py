from datetime import datetime

from pydantic import BaseModel

from ..models.entities import ProjectStatus


class ProjectCreate(BaseModel):
    title: str
    voice_id: int | None = None
    language: str | None = None
    style: str | None = None
    text: str | None = None


class ProjectRead(BaseModel):
    id: int
    title: str
    status: ProjectStatus
    language: str | None = None
    style: str | None = None
    voice_id: int | None = None
    audio_url: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectRead):
    source_text: str
    source_filename: str | None = None
