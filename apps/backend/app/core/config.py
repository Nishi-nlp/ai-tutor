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


settings = Settings()


def get_settings() -> Settings:
    return settings
