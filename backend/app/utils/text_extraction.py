from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader
from docx import Document


async def extract_text_from_upload(upload: UploadFile) -> str:
    """Extract plain text from the uploaded document."""

    suffix = Path(upload.filename or "").suffix.lower()
    raw_bytes = await upload.read()

    if not raw_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    if suffix in {".txt", ""}:
        return raw_bytes.decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        reader = PdfReader(BytesIO(raw_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if not text.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to extract text from PDF")
        return text

    if suffix == ".docx":
        document = Document(BytesIO(raw_bytes))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        if not text.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to extract text from DOCX")
        return text

    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file format")
