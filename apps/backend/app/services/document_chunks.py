from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk, KnowledgeComponent


class DocumentChunkingError(ValueError):
    pass


class DocumentNotFoundError(DocumentChunkingError):
    pass


class KnowledgeComponentNotFoundError(DocumentChunkingError):
    pass


class PdfExtractionError(DocumentChunkingError):
    pass


@dataclass(frozen=True)
class DocumentChunkingResult:
    document_id: str
    kc_id: str
    created: int


def _extract_pages(pdf_path: Path) -> list[tuple[int, str]]:
    try:
        reader = PdfReader(pdf_path)
        if reader.is_encrypted:
            raise PdfExtractionError("Encrypted PDFs are not supported")

        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            content = (page.extract_text() or "").strip()
            if content:
                pages.append((page_number, content))
    except PdfExtractionError:
        raise
    except FileNotFoundError as error:
        raise PdfExtractionError("Stored PDF was not found") from error
    except (OSError, PdfReadError) as error:
        raise PdfExtractionError("PDF text extraction failed") from error

    if not pages:
        raise PdfExtractionError("PDF contains no extractable text")

    return pages


def extract_document_chunks(
    session: Session,
    *,
    document_id: str,
    kc_id: str,
    storage_dir: Path,
) -> DocumentChunkingResult:
    document = session.get(Document, document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document not found: {document_id}")

    if session.get(KnowledgeComponent, kc_id) is None:
        raise KnowledgeComponentNotFoundError(f"Knowledge component not found: {kc_id}")

    extracted_pages = _extract_pages(storage_dir / document.storage_key)

    session.execute(
        delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.kc_id == kc_id,
        )
    )
    session.add_all(
        [
            DocumentChunk(
                document_id=document_id,
                kc_id=kc_id,
                page_number=page_number,
                content=content,
            )
            for page_number, content in extracted_pages
        ]
    )

    return DocumentChunkingResult(
        document_id=document_id,
        kc_id=kc_id,
        created=len(extracted_pages),
    )
