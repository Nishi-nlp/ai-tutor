import hashlib
import shutil
from pathlib import Path

import pytest
from pypdf import PdfWriter
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import Document, DocumentChunk, KnowledgeComponent
from app.services.document_chunks import (
    DocumentChunkingResult,
    DocumentNotFoundError,
    KnowledgeComponentNotFoundError,
    PdfExtractionError,
    extract_document_chunks,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_PDF = PROJECT_ROOT / "tests" / "fixtures" / "pdfs" / "sample-linear-algebra.pdf"
DOCUMENT_ID = "550e8400-e29b-41d4-a716-446655440000"
KC_ID = "la.linear_combination"


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _knowledge_component(kc_id: str = KC_ID) -> KnowledgeComponent:
    return KnowledgeComponent(
        id=kc_id,
        name="線形結合",
        description="複数のベクトルをスカラー倍して加えたもの",
        prerequisites=[],
        learning_objectives=["線形結合を説明できる"],
        source_refs=[],
        mastery_threshold=0.85,
        required_evidence=["no_hint_full_correct"],
    )


def _store_document(
    session: Session,
    storage_dir: Path,
    source: Path = SAMPLE_PDF,
) -> Document:
    storage_key = f"{DOCUMENT_ID}.pdf"
    stored_path = storage_dir / storage_key
    shutil.copyfile(source, stored_path)
    content = stored_path.read_bytes()
    document = Document(
        id=DOCUMENT_ID,
        original_filename="sample-linear-algebra.pdf",
        storage_key=storage_key,
        mime_type="application/pdf",
        size_bytes=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
    )
    session.add(document)
    return document


def test_sample_pdf_is_saved_as_page_chunks_with_traceable_metadata(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory.begin() as session:
        session.add(_knowledge_component())
        _store_document(session, tmp_path)

    with session_factory.begin() as session:
        result = extract_document_chunks(
            session,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            storage_dir=tmp_path,
        )

    with session_factory() as session:
        chunks = session.scalars(
            select(DocumentChunk).order_by(DocumentChunk.page_number)
        ).all()

        assert result == DocumentChunkingResult(
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            created=3,
        )
        assert [chunk.page_number for chunk in chunks] == [1, 2, 3]
        assert [chunk.kc_id for chunk in chunks] == [KC_ID, KC_ID, KC_ID]
        assert [chunk.document.original_filename for chunk in chunks] == [
            "sample-linear-algebra.pdf",
            "sample-linear-algebra.pdf",
            "sample-linear-algebra.pdf",
        ]
        assert "cobalt-vector-17" in chunks[0].content
        assert "amber-matrix-42" in chunks[1].content
        assert "jade-exercise-93" in chunks[2].content


def test_reprocessing_replaces_only_chunks_for_same_document_and_kc(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    other_kc_id = "la.other"
    with session_factory.begin() as session:
        session.add_all([_knowledge_component(), _knowledge_component(other_kc_id)])
        document = _store_document(session, tmp_path)
        document.chunks.extend(
            [
                DocumentChunk(kc_id=KC_ID, page_number=1, content="old content"),
                DocumentChunk(
                    kc_id=other_kc_id,
                    page_number=1,
                    content="other KC content",
                ),
            ]
        )

    for _ in range(2):
        with session_factory.begin() as session:
            extract_document_chunks(
                session,
                document_id=DOCUMENT_ID,
                kc_id=KC_ID,
                storage_dir=tmp_path,
            )

    with session_factory() as session:
        target_chunks = session.scalars(
            select(DocumentChunk).where(DocumentChunk.kc_id == KC_ID)
        ).all()
        other_chunks = session.scalars(
            select(DocumentChunk).where(DocumentChunk.kc_id == other_kc_id)
        ).all()

        assert len(target_chunks) == 3
        assert all(chunk.content != "old content" for chunk in target_chunks)
        assert len(other_chunks) == 1
        assert other_chunks[0].content == "other KC content"


def test_pdf_without_extractable_text_is_rejected_before_existing_chunks_are_deleted(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    blank_pdf = tmp_path / "blank-source.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with blank_pdf.open("wb") as output:
        writer.write(output)

    with session_factory.begin() as session:
        session.add(_knowledge_component())
        document = _store_document(session, tmp_path, blank_pdf)
        document.chunks.append(
            DocumentChunk(kc_id=KC_ID, page_number=1, content="existing content")
        )

    with (
        session_factory.begin() as session,
        pytest.raises(
            PdfExtractionError,
            match="PDF contains no extractable text",
        ),
    ):
        extract_document_chunks(
            session,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            storage_dir=tmp_path,
        )

    with session_factory() as session:
        chunks = session.scalars(select(DocumentChunk)).all()
        assert len(chunks) == 1
        assert chunks[0].content == "existing content"


def test_missing_document_is_reported(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory.begin() as session:
        session.add(_knowledge_component())

    with (
        session_factory() as session,
        pytest.raises(
            DocumentNotFoundError,
            match="Document not found",
        ),
    ):
        extract_document_chunks(
            session,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            storage_dir=tmp_path,
        )


def test_missing_knowledge_component_is_reported(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory.begin() as session:
        _store_document(session, tmp_path)

    with (
        session_factory() as session,
        pytest.raises(
            KnowledgeComponentNotFoundError,
            match="Knowledge component not found",
        ),
    ):
        extract_document_chunks(
            session,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            storage_dir=tmp_path,
        )


def test_missing_stored_pdf_is_reported(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    with session_factory.begin() as session:
        session.add(_knowledge_component())
        document = _store_document(session, tmp_path)

    (tmp_path / document.storage_key).unlink()

    with (
        session_factory() as session,
        pytest.raises(
            PdfExtractionError,
            match="Stored PDF was not found",
        ),
    ):
        extract_document_chunks(
            session,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            storage_dir=tmp_path,
        )


def test_broken_pdf_is_reported(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
) -> None:
    broken_pdf = tmp_path / "broken-source.pdf"
    broken_pdf.write_bytes(b"%PDF-broken")

    with session_factory.begin() as session:
        session.add(_knowledge_component())
        _store_document(session, tmp_path, broken_pdf)

    with (
        session_factory() as session,
        pytest.raises(PdfExtractionError, match="PDF text extraction failed"),
    ):
        extract_document_chunks(
            session,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            storage_dir=tmp_path,
        )
