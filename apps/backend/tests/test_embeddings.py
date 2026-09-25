import hashlib
from collections.abc import Sequence
from types import SimpleNamespace
from typing import Any, cast

import pytest
from openai import OpenAI, OpenAIError
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import Document, DocumentChunk, KnowledgeComponent
from app.db.models.document_chunk import EMBEDDING_DIMENSIONS
from app.services.embeddings import (
    DocumentChunksChangedError,
    DocumentChunksNotFoundError,
    EmbeddingBatch,
    EmbeddingProviderError,
    InvalidEmbeddingResponseError,
    OpenAIEmbeddingProvider,
    embed_document_chunks,
)

DOCUMENT_ID = "550e8400-e29b-41d4-a716-446655440000"
KC_ID = "la.linear_combination"


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)

    with factory.begin() as session:
        content = b"%PDF-1.4 sample"
        session.add(
            KnowledgeComponent(
                id=KC_ID,
                name="線形結合",
                description="複数のベクトルをスカラー倍して加えたもの",
                prerequisites=[],
                learning_objectives=["線形結合を説明できる"],
                source_refs=[],
                mastery_threshold=0.85,
                required_evidence=["no_hint_full_correct"],
            )
        )
        document = Document(
            id=DOCUMENT_ID,
            original_filename="linear-algebra.pdf",
            storage_key=f"{DOCUMENT_ID}.pdf",
            mime_type="application/pdf",
            size_bytes=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
        )
        document.chunks.extend(
            [
                DocumentChunk(
                    kc_id=KC_ID,
                    page_number=1,
                    content="線形結合の定義",
                ),
                DocumentChunk(
                    kc_id=KC_ID,
                    page_number=2,
                    content="線形結合の例題",
                ),
            ]
        )
        session.add(document)

    yield factory
    engine.dispose()


class RecordingProvider:
    def __init__(self, batch: EmbeddingBatch) -> None:
        self.batch = batch
        self.calls: list[tuple[list[str], str, int]] = []

    def embed(
        self,
        texts: Sequence[str],
        *,
        model: str,
        dimensions: int,
    ) -> EmbeddingBatch:
        self.calls.append((list(texts), model, dimensions))
        return self.batch


def _vector(value: float) -> list[float]:
    return [value] * EMBEDDING_DIMENSIONS


def _saved_chunks(factory: sessionmaker[Session]) -> list[DocumentChunk]:
    with factory() as session:
        return list(session.scalars(select(DocumentChunk).order_by(DocumentChunk.id)))


def test_embeddings_are_generated_in_one_batch_and_saved(
    session_factory: sessionmaker[Session],
) -> None:
    provider = RecordingProvider(
        EmbeddingBatch(
            model="text-embedding-3-small",
            vectors=[_vector(0.1), _vector(0.2)],
        )
    )

    result = embed_document_chunks(
        session_factory,
        provider,
        document_id=DOCUMENT_ID,
        kc_id=KC_ID,
        model="text-embedding-3-small",
        dimensions=EMBEDDING_DIMENSIONS,
    )

    assert provider.calls == [
        (
            ["線形結合の定義", "線形結合の例題"],
            "text-embedding-3-small",
            EMBEDDING_DIMENSIONS,
        )
    ]
    assert result.updated == 2
    assert result.model == "text-embedding-3-small"

    chunks = _saved_chunks(session_factory)
    assert list(chunks[0].embedding or []) == pytest.approx(_vector(0.1))
    assert list(chunks[1].embedding or []) == pytest.approx(_vector(0.2))
    assert {chunk.embedding_model for chunk in chunks} == {"text-embedding-3-small"}


def test_reprocessing_overwrites_embeddings_without_adding_chunks(
    session_factory: sessionmaker[Session],
) -> None:
    first_provider = RecordingProvider(
        EmbeddingBatch(model="model-v1", vectors=[_vector(0.1), _vector(0.2)])
    )
    second_provider = RecordingProvider(
        EmbeddingBatch(model="model-v2", vectors=[_vector(0.3), _vector(0.4)])
    )

    for provider in (first_provider, second_provider):
        embed_document_chunks(
            session_factory,
            provider,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            model="requested-model",
            dimensions=EMBEDDING_DIMENSIONS,
        )

    chunks = _saved_chunks(session_factory)
    assert len(chunks) == 2
    assert list(chunks[0].embedding or []) == pytest.approx(_vector(0.3))
    assert list(chunks[1].embedding or []) == pytest.approx(_vector(0.4))
    assert {chunk.embedding_model for chunk in chunks} == {"model-v2"}


def test_provider_failure_does_not_change_existing_embeddings(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory.begin() as session:
        for chunk in session.scalars(select(DocumentChunk)):
            chunk.embedding = _vector(0.5)
            chunk.embedding_model = "existing-model"

    class FailingProvider:
        def embed(
            self,
            texts: Sequence[str],
            *,
            model: str,
            dimensions: int,
        ) -> EmbeddingBatch:
            raise EmbeddingProviderError("Embedding API request failed")

    with pytest.raises(EmbeddingProviderError, match="request failed"):
        embed_document_chunks(
            session_factory,
            FailingProvider(),
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            model="requested-model",
            dimensions=EMBEDDING_DIMENSIONS,
        )

    chunks = _saved_chunks(session_factory)
    assert all(
        list(chunk.embedding or []) == pytest.approx(_vector(0.5)) for chunk in chunks
    )
    assert {chunk.embedding_model for chunk in chunks} == {"existing-model"}


@pytest.mark.parametrize(
    "vectors, error_message",
    [
        ([_vector(0.1)], "count does not match"),
        (
            [[0.1] * (EMBEDDING_DIMENSIONS - 1), _vector(0.2)],
            "dimensions do not match",
        ),
        (
            [[float("nan")] * EMBEDDING_DIMENSIONS, _vector(0.2)],
            "non-finite value",
        ),
    ],
)
def test_invalid_provider_response_is_not_saved(
    session_factory: sessionmaker[Session],
    vectors: list[list[float]],
    error_message: str,
) -> None:
    provider = RecordingProvider(EmbeddingBatch(model="model", vectors=vectors))

    with pytest.raises(InvalidEmbeddingResponseError, match=error_message):
        embed_document_chunks(
            session_factory,
            provider,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            model="model",
            dimensions=EMBEDDING_DIMENSIONS,
        )

    assert all(chunk.embedding is None for chunk in _saved_chunks(session_factory))


def test_too_long_model_name_is_not_saved(
    session_factory: sessionmaker[Session],
) -> None:
    provider = RecordingProvider(
        EmbeddingBatch(model="m" * 101, vectors=[_vector(0.1), _vector(0.2)])
    )

    with pytest.raises(InvalidEmbeddingResponseError, match="model name is too long"):
        embed_document_chunks(
            session_factory,
            provider,
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            model="model",
            dimensions=EMBEDDING_DIMENSIONS,
        )

    assert all(chunk.embedding is None for chunk in _saved_chunks(session_factory))


def test_missing_chunks_are_rejected_before_calling_provider(
    session_factory: sessionmaker[Session],
) -> None:
    provider = RecordingProvider(EmbeddingBatch(model="model", vectors=[]))

    with pytest.raises(DocumentChunksNotFoundError, match="not found"):
        embed_document_chunks(
            session_factory,
            provider,
            document_id="missing-document",
            kc_id=KC_ID,
            model="model",
            dimensions=EMBEDDING_DIMENSIONS,
        )

    assert provider.calls == []


def test_changed_chunk_is_not_overwritten_after_api_call(
    session_factory: sessionmaker[Session],
) -> None:
    class MutatingProvider:
        def embed(
            self,
            texts: Sequence[str],
            *,
            model: str,
            dimensions: int,
        ) -> EmbeddingBatch:
            with session_factory.begin() as session:
                chunk = session.scalar(
                    select(DocumentChunk).order_by(DocumentChunk.id).limit(1)
                )
                assert chunk is not None
                chunk.content = "API呼び出し中に更新された内容"
            return EmbeddingBatch(
                model=model,
                vectors=[_vector(0.1), _vector(0.2)],
            )

    with pytest.raises(DocumentChunksChangedError, match="changed"):
        embed_document_chunks(
            session_factory,
            MutatingProvider(),
            document_id=DOCUMENT_ID,
            kc_id=KC_ID,
            model="model",
            dimensions=EMBEDDING_DIMENSIONS,
        )

    chunks = _saved_chunks(session_factory)
    assert chunks[0].content == "API呼び出し中に更新された内容"
    assert all(chunk.embedding is None for chunk in chunks)


def test_openai_provider_restores_response_order() -> None:
    calls: list[dict[str, Any]] = []

    def create(**kwargs: Any) -> SimpleNamespace:
        calls.append(kwargs)
        return SimpleNamespace(
            model="text-embedding-3-small",
            data=[
                SimpleNamespace(index=1, embedding=[0.3, 0.4]),
                SimpleNamespace(index=0, embedding=[0.1, 0.2]),
            ],
        )

    client = cast(OpenAI, SimpleNamespace(embeddings=SimpleNamespace(create=create)))
    provider = OpenAIEmbeddingProvider(client)

    result = provider.embed(
        ["first", "second"],
        model="text-embedding-3-small",
        dimensions=2,
    )

    assert calls == [
        {
            "input": ["first", "second"],
            "model": "text-embedding-3-small",
            "dimensions": 2,
        }
    ]
    assert result.vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert result.model == "text-embedding-3-small"


@pytest.mark.parametrize("indexes", [[0, 0], [0, 2]])
def test_openai_provider_rejects_invalid_response_indexes(indexes: list[int]) -> None:
    response = SimpleNamespace(
        model="text-embedding-3-small",
        data=[SimpleNamespace(index=index, embedding=[0.1, 0.2]) for index in indexes],
    )
    client = cast(
        OpenAI,
        SimpleNamespace(
            embeddings=SimpleNamespace(create=lambda **kwargs: response),
        ),
    )

    with pytest.raises(EmbeddingProviderError, match="result indexes"):
        OpenAIEmbeddingProvider(client).embed(
            ["first", "second"],
            model="text-embedding-3-small",
            dimensions=2,
        )


def test_openai_provider_hides_sdk_error_details() -> None:
    def create(**kwargs: Any) -> None:
        raise OpenAIError("secret provider detail")

    client = cast(OpenAI, SimpleNamespace(embeddings=SimpleNamespace(create=create)))

    with pytest.raises(
        EmbeddingProviderError,
        match="^Embedding API request failed$",
    ) as error:
        OpenAIEmbeddingProvider(client).embed(
            ["text"],
            model="text-embedding-3-small",
            dimensions=2,
        )

    assert "secret provider detail" not in str(error.value)


def test_embedding_pair_constraint_rejects_only_one_value(
    session_factory: sessionmaker[Session],
) -> None:
    with pytest.raises(IntegrityError), session_factory.begin() as session:
        chunk = session.scalar(select(DocumentChunk).limit(1))
        assert chunk is not None
        chunk.embedding_model = "model-without-vector"

        session.flush()

    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(DocumentChunk)) == 2
