from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import Document
from app.storage import save_document

PDF_MIME_TYPE = "application/pdf"
PDF_HEADER = b"%PDF-"
MAX_ORIGINAL_FILENAME_LENGTH = 255


class InvalidPdfError(ValueError):
    pass


class DocumentTooLargeError(ValueError):
    pass


def _normalize_original_filename(original_filename: str | None) -> str:
    if original_filename is None:
        raise InvalidPdfError("Only PDF files are supported")

    filename = original_filename.replace("\\", "/").rsplit("/", 1)[-1]
    if (
        not filename
        or len(filename) > MAX_ORIGINAL_FILENAME_LENGTH
        or Path(filename).suffix.lower() != ".pdf"
    ):
        raise InvalidPdfError("Only PDF files are supported")

    return filename


def _is_pdf_mime_type(mime_type: str | None) -> bool:
    if mime_type is None:
        return False
    return mime_type.split(";", 1)[0].strip().lower() == PDF_MIME_TYPE


def register_document(
    session: Session,
    *,
    original_filename: str | None,
    mime_type: str | None,
    content: bytes,
    storage_dir: Path,
    max_size_bytes: int,
) -> Document:
    if len(content) > max_size_bytes:
        raise DocumentTooLargeError("PDF exceeds the maximum allowed size")

    filename = _normalize_original_filename(original_filename)
    if not _is_pdf_mime_type(mime_type) or not content.startswith(PDF_HEADER):
        raise InvalidPdfError("Only PDF files are supported")

    document_id = str(uuid4())
    storage_key = f"{document_id}.pdf"
    stored_document = save_document(content, storage_key, storage_dir)
    document = Document(
        id=document_id,
        original_filename=filename,
        storage_key=storage_key,
        mime_type=PDF_MIME_TYPE,
        size_bytes=stored_document.size_bytes,
        checksum_sha256=stored_document.checksum_sha256,
    )

    try:
        session.add(document)
        session.commit()
    except Exception:
        try:
            session.rollback()
        finally:
            stored_document.path.unlink(missing_ok=True)
        raise

    return document
