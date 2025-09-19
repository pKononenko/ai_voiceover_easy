from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ProjectStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)



class Voice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    language: str
    accent: Optional[str] = None
    gender: Optional[str] = None
    style: Optional[str] = None
    provider: Optional[str] = None

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    voice_id: Optional[int] = Field(default=None, foreign_key="voice.id")
    title: str
    source_text: str
    source_filename: Optional[str] = None
    language: Optional[str] = None
    style: Optional[str] = None
    status: ProjectStatus = Field(default=ProjectStatus.PENDING)
    audio_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

