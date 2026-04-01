from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.services.rag import ingest_pdf

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_FILES = 50


class UploadFileResult(BaseModel):
    filename: str
    chunks: int | None = None
    error: str | None = None


@router.post("/upload")
async def upload_pdf(files: list[UploadFile] = File(default=[])) -> list[UploadFileResult]:
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one file must be provided.")
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"No more than {MAX_FILES} files per request.")

    uploads_path = Path(settings.uploads_dir)
    uploads_path.mkdir(parents=True, exist_ok=True)

    results: list[UploadFileResult] = []

    for file in files:
        filename = file.filename or "upload.pdf"
        try:
            if file.content_type != "application/pdf" or not filename.endswith(".pdf"):
                raise ValueError("Only PDF files are accepted.")

            content = await file.read()

            if len(content) > MAX_FILE_SIZE:
                raise ValueError("File exceeds the 5 MB size limit.")

            destination = uploads_path / filename
            destination.write_bytes(content)

            chunks = ingest_pdf(destination)
            results.append(UploadFileResult(filename=filename, chunks=chunks))

        except Exception as e:
            results.append(UploadFileResult(filename=filename, error=str(e)))

    return results
