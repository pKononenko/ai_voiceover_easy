from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from ..core.config import get_settings
from ..core.database import get_session
from ..models.entities import Project, ProjectStatus, User
from ..schemas.project import ProjectDetail, ProjectRead
from ..services.audio import generate_audio_file
from ..utils.text_extraction import extract_text_from_upload
from .dependencies import get_current_user, get_db


router = APIRouter(prefix="/projects", tags=["projects"])


def _project_to_read(project: Project) -> ProjectRead:
    audio_url = f"/projects/{project.id}/audio" if project.audio_path else None
    return ProjectRead(
        id=project.id,
        title=project.title,
        status=project.status,
        language=project.language,
        style=project.style,
        voice_id=project.voice_id,
        audio_url=audio_url,
        error_message=project.error_message,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_to_detail(project: Project) -> ProjectDetail:
    base = _project_to_read(project)
    return ProjectDetail(**base.model_dump(), source_text=project.source_text, source_filename=project.source_filename)


async def _queue_audio_generation(project_id: int) -> None:
    settings = get_settings()
    with get_session() as session:
        project = session.get(Project, project_id)
        if not project:
            return
        try:
            project.status = ProjectStatus.PROCESSING
            session.add(project)
            session.commit()
            session.refresh(project)

            filename = f"project_{project.id}.wav"
            audio_path = generate_audio_file(project.source_text, settings.storage_dir, filename)
            project.audio_path = str(audio_path)
            project.status = ProjectStatus.COMPLETED
            project.updated_at = datetime.utcnow()
        except Exception as exc:  # pragma: no cover - defensive
            project.status = ProjectStatus.FAILED
            project.error_message = str(exc)
        finally:
            project.updated_at = datetime.utcnow()
            session.add(project)
            session.commit()


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    voice_id: int | None = Form(default=None),
    language: str | None = Form(default=None),
    style: str | None = Form(default=None),
    text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectDetail:
    extracted_text = text.strip() if text else ""
    source_filename = None
    if file is not None:
        source_filename = file.filename
        extracted_text = (await extract_text_from_upload(file)).strip()

    if not extracted_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No text provided for narration")

    project = Project(
        title=title,
        source_text=extracted_text,
        source_filename=source_filename,
        voice_id=voice_id,
        language=language,
        style=style,
        status=ProjectStatus.PENDING,
        user_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    background_tasks.add_task(_queue_audio_generation, project.id)

    return _project_to_detail(project)


@router.get("", response_model=list[ProjectRead])
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ProjectRead]:
    projects = db.exec(select(Project).where(Project.user_id == current_user.id).order_by(Project.created_at.desc())).all()
    return [_project_to_read(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProjectDetail:
    project = db.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _project_to_detail(project)


@router.get("/{project_id}/audio")
def download_audio(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FileResponse:
    project = db.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if not project.audio_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio not available yet")

    audio_path = Path(project.audio_path)
    if not audio_path.exists():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Audio file missing")

    return FileResponse(path=audio_path, filename=audio_path.name, media_type="audio/wav")
