import pytest

from app.core.config import Settings, settings


def test_app_title() -> None:
    assert settings.app_title == "AI Tutor API"


def test_database_url_uses_local_database_by_default() -> None:
    assert settings.database_url.endswith("@localhost:5433/ai_tutor")


def test_document_storage_uses_private_data_directory_by_default() -> None:
    assert settings.document_storage_dir.parts[-2:] == ("data", "books")
    assert "public" not in settings.document_storage_dir.parts


def test_document_size_limit_is_ten_mebibytes_by_default() -> None:
    assert settings.document_max_size_bytes == 10 * 1024 * 1024


def test_embedding_defaults_match_database_vector_size() -> None:
    assert settings.embedding_model == "text-embedding-3-small"
    assert settings.embedding_dimensions == 1536
    assert settings.embedding_timeout_seconds == 30


@pytest.mark.parametrize("size_limit", [0, -1])
def test_document_size_limit_must_be_positive(size_limit: int) -> None:
    with pytest.raises(
        ValueError,
        match="DOCUMENT_MAX_SIZE_BYTES must be positive",
    ):
        Settings(document_max_size_bytes=size_limit)


def test_embedding_model_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="EMBEDDING_MODEL must not be empty"):
        Settings(embedding_model=" ")


@pytest.mark.parametrize("dimensions", [0, -1])
def test_embedding_dimensions_must_be_positive(dimensions: int) -> None:
    with pytest.raises(ValueError, match="EMBEDDING_DIMENSIONS must be positive"):
        Settings(embedding_dimensions=dimensions)


def test_embedding_dimensions_must_match_database_vector_size() -> None:
    with pytest.raises(ValueError, match="must match the database vector size"):
        Settings(embedding_dimensions=512)


@pytest.mark.parametrize("timeout", [0, -1])
def test_embedding_timeout_must_be_positive(timeout: float) -> None:
    with pytest.raises(ValueError, match="EMBEDDING_TIMEOUT_SECONDS must be positive"):
        Settings(embedding_timeout_seconds=timeout)
