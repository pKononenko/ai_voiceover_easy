from pydantic import BaseModel


class VoiceRead(BaseModel):
    id: int
    name: str
    language: str
    accent: str | None = None
    gender: str | None = None
    style: str | None = None
    provider: str | None = None
