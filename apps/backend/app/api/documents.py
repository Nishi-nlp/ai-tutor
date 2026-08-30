from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.schemas.document import DocumentResponse
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.services.documents import (
    DocumentTooLargeError,
    InvalidPdfError,
    register_document,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    file: Annotated[UploadFile, File()],
    session: Annotated[Session, Depends(get_db_session)],
    app_settings: Annotated[Settings, Depends(get_settings)],
) -> DocumentResponse:
    content = file.file.read(app_settings.document_max_size_bytes + 1)

    try:
        document = register_document(
            session,
            original_filename=file.filename,
            mime_type=file.content_type,
            content=content,
            storage_dir=app_settings.document_storage_dir,
            max_size_bytes=app_settings.document_max_size_bytes,
        )
    except DocumentTooLargeError as error:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(error),
        ) from error
    except InvalidPdfError as error:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(error),
        ) from error

    return DocumentResponse.model_validate(document)
