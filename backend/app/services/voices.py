from __future__ import annotations

from typing import Iterable

from sqlmodel import Session, select

from ..models.entities import Voice


DEFAULT_VOICES: Iterable[Voice] = (
    Voice(name="Ava", language="en", accent="US", gender="female", style="narration", provider="placeholder"),
    Voice(name="Noah", language="en", accent="US", gender="male", style="storyteller", provider="placeholder"),
    Voice(name="Isabella", language="en", accent="UK", gender="female", style="dramatic", provider="placeholder"),
    Voice(name="Mateo", language="es", accent="LatAm", gender="male", style="neutral", provider="placeholder"),
)


def ensure_default_voices(session: Session) -> None:
    if session.exec(select(Voice)).first():
        return
    for voice in DEFAULT_VOICES:
        session.add(voice)
    session.commit()
