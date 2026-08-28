import hashlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Document, DocumentChunk, KnowledgeComponent


def _knowledge_component() -> KnowledgeComponent:
    return KnowledgeComponent(
        id="la.linear_combination",
        name="線形結合",
        description="複数のベクトルをスカラー倍して加えたもの",
        prerequisites=[],
        learning_objectives=["線形結合を説明できる"],
        source_refs=[],
        mastery_threshold=0.85,
        required_evidence=["no_hint_full_correct"],
    )


def _document() -> Document:
    content = b"%PDF-1.4 sample"
    return Document(
        id="550e8400-e29b-41d4-a716-446655440000",
        original_filename="linear-algebra.pdf",
        storage_key="550e8400-e29b-41d4-a716-446655440000.pdf",
        mime_type="application/pdf",
        size_bytes=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
    )


def test_document_and_chunk_can_be_saved_and_traced() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        document = _document()
        document.chunks.append(
            DocumentChunk(
                kc_id="la.linear_combination",
                page_number=2,
                content="線形結合とは、ベクトルのスカラー倍の和である。",
            )
        )
        session.add_all([_knowledge_component(), document])
        session.commit()

        saved_chunk = session.query(DocumentChunk).one()

        assert saved_chunk.document.id == document.id
        assert saved_chunk.document.original_filename == "linear-algebra.pdf"
        assert saved_chunk.kc_id == "la.linear_combination"
        assert saved_chunk.page_number == 2

    engine.dispose()


def test_deleting_document_also_deletes_its_chunks() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        document = _document()
        document.chunks.append(
            DocumentChunk(
                kc_id="la.linear_combination",
                page_number=1,
                content="線形結合の説明",
            )
        )
        session.add_all([_knowledge_component(), document])
        session.commit()

        chunk_id = document.chunks[0].id
        session.delete(document)
        session.commit()

        assert session.get(DocumentChunk, chunk_id) is None

    engine.dispose()


def test_document_size_must_not_be_negative() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    document = _document()
    document.size_bytes = -1

    with Session(engine) as session:
        session.add(document)

        with pytest.raises(IntegrityError):
            session.commit()

    engine.dispose()
