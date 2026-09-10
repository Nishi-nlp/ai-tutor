import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Settings:
    app_title: str = "AI Tutor API"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://ai_tutor:local-development-only@localhost:5433/ai_tutor",
    )
    document_storage_dir: Path = Path(
        os.getenv("DOCUMENT_STORAGE_DIR", PROJECT_ROOT / "data" / "books")
    )
    document_max_size_bytes: int = int(
        os.getenv("DOCUMENT_MAX_SIZE_BYTES", str(10 * 1024 * 1024))
    )
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL",
        "text-embedding-3-small",
    )
    embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    embedding_timeout_seconds: float = float(
        os.getenv("EMBEDDING_TIMEOUT_SECONDS", "30")
    )

    def __post_init__(self) -> None:
        if self.document_max_size_bytes <= 0:
            raise ValueError("DOCUMENT_MAX_SIZE_BYTES must be positive")
        if not self.embedding_model.strip():
            raise ValueError("EMBEDDING_MODEL must not be empty")
        if self.embedding_dimensions <= 0:
            raise ValueError("EMBEDDING_DIMENSIONS must be positive")
        if self.embedding_dimensions != 1536:
            raise ValueError(
                "EMBEDDING_DIMENSIONS must match the database vector size: 1536"
            )
        if self.embedding_timeout_seconds <= 0:
            raise ValueError("EMBEDDING_TIMEOUT_SECONDS must be positive")


settings = Settings()


def get_settings() -> Settings:
    return settings
