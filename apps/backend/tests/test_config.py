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


@pytest.mark.parametrize("size_limit", [0, -1])
def test_document_size_limit_must_be_positive(size_limit: int) -> None:
    with pytest.raises(
        ValueError,
        match="DOCUMENT_MAX_SIZE_BYTES must be positive",
    ):
        Settings(document_max_size_bytes=size_limit)
