import hashlib
from collections.abc import Generator
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings, settings
from app.db.base import Base
from app.db.models import Document
from app.db.session import get_db_session
from app.main import app

TEST_MAX_SIZE_BYTES = 32


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as session:
        yield session

    engine.dispose()


@pytest.fixture
def document_storage(
    db_session: Session,
    tmp_path: Path,
) -> Generator[Path, None, None]:
    def override_db_session() -> Session:
        return db_session

    def override_settings():
        return replace(
            settings,
            document_storage_dir=tmp_path,
            document_max_size_bytes=TEST_MAX_SIZE_BYTES,
        )

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings

    try:
        yield tmp_path
    finally:
        app.dependency_overrides.pop(get_db_session, None)
        app.dependency_overrides.pop(get_settings, None)


@pytest.mark.anyio
async def test_register_pdf_saves_file_and_document(
    db_session: Session,
    document_storage: Path,
) -> None:
    content = b"%PDF-1.4\nsample"
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents",
            files={"file": ("linear-algebra.pdf", content, "application/pdf")},
        )

    assert response.status_code == 201
    response_body = response.json()
    document_id = response_body["id"]
    UUID(document_id)
    assert response_body == {
        "id": document_id,
        "original_filename": "linear-algebra.pdf",
        "mime_type": "application/pdf",
        "size_bytes": len(content),
        "checksum_sha256": hashlib.sha256(content).hexdigest(),
    }

    saved_document = db_session.get(Document, document_id)
    assert saved_document is not None
    assert saved_document.storage_key == f"{document_id}.pdf"
    assert saved_document.storage_key != saved_document.original_filename
    assert (document_storage / saved_document.storage_key).read_bytes() == content


@pytest.mark.anyio
async def test_register_pdf_accepts_case_insensitive_mime_type(
    document_storage: Path,
) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents",
            files={"file": ("sample.PDF", b"%PDF-1.4", "Application/PDF")},
        )

    assert response.status_code == 201
    assert len(list(document_storage.iterdir())) == 1


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("filename", "content", "mime_type"),
    [
        ("linear-algebra.txt", b"%PDF-1.4", "application/pdf"),
        ("linear-algebra.pdf", b"%PDF-1.4", "text/plain"),
        ("linear-algebra.pdf", b"not a pdf", "application/pdf"),
    ],
)
async def test_register_document_rejects_non_pdf(
    document_storage: Path,
    filename: str,
    content: bytes,
    mime_type: str,
) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents",
            files={"file": (filename, content, mime_type)},
        )

    assert response.status_code == 415
    assert response.json() == {"detail": "Only PDF files are supported"}
    assert list(document_storage.iterdir()) == []


@pytest.mark.anyio
async def test_register_document_rejects_file_over_size_limit(
    document_storage: Path,
) -> None:
    content = b"%PDF-" + b"x" * TEST_MAX_SIZE_BYTES
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents",
            files={"file": ("large.pdf", content, "application/pdf")},
        )

    assert response.status_code == 413
    assert response.json() == {"detail": "PDF exceeds the maximum allowed size"}
    assert list(document_storage.iterdir()) == []


@pytest.mark.anyio
async def test_register_document_removes_file_when_database_commit_fails(
    db_session: Session,
    document_storage: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_commit() -> None:
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(db_session, "commit", fail_commit)
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents",
            files={
                "file": (
                    "linear-algebra.pdf",
                    b"%PDF-1.4\nsample",
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert list(document_storage.iterdir()) == []
    assert db_session.query(Document).count() == 0
