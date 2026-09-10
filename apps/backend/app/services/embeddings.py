import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI, OpenAIError
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import DocumentChunk


class EmbeddingError(ValueError):
    pass


class DocumentChunksNotFoundError(EmbeddingError):
    pass


class EmbeddingProviderError(EmbeddingError):
    pass


class InvalidEmbeddingResponseError(EmbeddingError):
    pass


class DocumentChunksChangedError(EmbeddingError):
    pass


@dataclass(frozen=True)
class EmbeddingBatch:
    model: str
    vectors: list[list[float]]


@dataclass(frozen=True)
class ChunkInput:
    id: int
    content: str


@dataclass(frozen=True)
class EmbeddingResult:
    document_id: str
    kc_id: str
    model: str
    updated: int


class EmbeddingProvider(Protocol):
    def embed(
        self,
        texts: Sequence[str],
        *,
        model: str,
        dimensions: int,
    ) -> EmbeddingBatch: ...


class OpenAIEmbeddingProvider:
    def __init__(self, client: OpenAI) -> None:
        self._client = client

    def embed(
        self,
        texts: Sequence[str],
        *,
        model: str,
        dimensions: int,
    ) -> EmbeddingBatch:
        try:
            response = self._client.embeddings.create(
                input=list(texts),
                model=model,
                dimensions=dimensions,
            )
        except OpenAIError as error:
            raise EmbeddingProviderError("Embedding API request failed") from error

        vectors_by_index: dict[int, list[float]] = {}
        for item in response.data:
            if item.index in vectors_by_index:
                raise EmbeddingProviderError(
                    "Embedding API returned duplicate result indexes"
                )
            vectors_by_index[item.index] = list(item.embedding)

        expected_indexes = set(range(len(texts)))
        if set(vectors_by_index) != expected_indexes:
            raise EmbeddingProviderError(
                "Embedding API returned invalid result indexes"
            )

        return EmbeddingBatch(
            model=response.model,
            vectors=[vectors_by_index[index] for index in range(len(texts))],
        )


def _load_chunk_inputs(
    session_factory: sessionmaker[Session],
    *,
    document_id: str,
    kc_id: str,
) -> list[ChunkInput]:
    with session_factory() as session:
        chunks = session.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.kc_id == kc_id,
            )
            .order_by(DocumentChunk.id)
        ).all()

        if not chunks:
            raise DocumentChunksNotFoundError(
                f"Document chunks not found: document_id={document_id} kc_id={kc_id}"
            )

        return [ChunkInput(id=chunk.id, content=chunk.content) for chunk in chunks]


def _validate_embedding_batch(
    batch: EmbeddingBatch,
    *,
    expected_count: int,
    dimensions: int,
) -> list[list[float]]:
    if not batch.model.strip():
        raise InvalidEmbeddingResponseError("Embedding model name is missing")
    if len(batch.model) > 100:
        raise InvalidEmbeddingResponseError("Embedding model name is too long")
    if len(batch.vectors) != expected_count:
        raise InvalidEmbeddingResponseError(
            "Embedding result count does not match the chunk count"
        )

    normalized_vectors = []
    for vector in batch.vectors:
        try:
            normalized = [float(value) for value in vector]
        except (TypeError, ValueError) as error:
            raise InvalidEmbeddingResponseError(
                "Embedding contains a non-numeric value"
            ) from error

        if len(normalized) != dimensions:
            raise InvalidEmbeddingResponseError(
                "Embedding dimensions do not match the configured dimensions"
            )
        if not all(math.isfinite(value) for value in normalized):
            raise InvalidEmbeddingResponseError("Embedding contains a non-finite value")
        normalized_vectors.append(normalized)

    return normalized_vectors


def _save_embeddings(
    session_factory: sessionmaker[Session],
    *,
    inputs: Sequence[ChunkInput],
    vectors: Sequence[list[float]],
    model: str,
) -> None:
    chunk_ids = [chunk_input.id for chunk_input in inputs]

    with session_factory.begin() as session:
        chunks = session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.id.in_(chunk_ids))
            .order_by(DocumentChunk.id)
            .with_for_update()
        ).all()
        chunks_by_id = {chunk.id: chunk for chunk in chunks}

        if set(chunks_by_id) != set(chunk_ids):
            raise DocumentChunksChangedError(
                "Document chunks changed while embeddings were generated"
            )

        for chunk_input, vector in zip(inputs, vectors, strict=True):
            chunk = chunks_by_id[chunk_input.id]
            if chunk.content != chunk_input.content:
                raise DocumentChunksChangedError(
                    "Document chunks changed while embeddings were generated"
                )
            chunk.embedding = vector
            chunk.embedding_model = model


def embed_document_chunks(
    session_factory: sessionmaker[Session],
    provider: EmbeddingProvider,
    *,
    document_id: str,
    kc_id: str,
    model: str,
    dimensions: int,
) -> EmbeddingResult:
    inputs = _load_chunk_inputs(
        session_factory,
        document_id=document_id,
        kc_id=kc_id,
    )
    batch = provider.embed(
        [chunk_input.content for chunk_input in inputs],
        model=model,
        dimensions=dimensions,
    )
    vectors = _validate_embedding_batch(
        batch,
        expected_count=len(inputs),
        dimensions=dimensions,
    )
    _save_embeddings(
        session_factory,
        inputs=inputs,
        vectors=vectors,
        model=batch.model,
    )

    return EmbeddingResult(
        document_id=document_id,
        kc_id=kc_id,
        model=batch.model,
        updated=len(inputs),
    )
