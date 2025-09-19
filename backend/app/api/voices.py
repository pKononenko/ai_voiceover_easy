from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..models.entities import Voice
from ..schemas.voice import VoiceRead
from ..services.voices import ensure_default_voices
from .dependencies import get_db


router = APIRouter(prefix="/voices", tags=["voices"])


@router.get("", response_model=List[VoiceRead])
def list_voices(db: Session = Depends(get_db)) -> list[VoiceRead]:
    ensure_default_voices(db)
    voices = db.exec(select(Voice)).all()
    return [VoiceRead.model_validate(voice, from_attributes=True) for voice in voices]
