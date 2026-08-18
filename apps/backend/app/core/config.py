import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_title: str = "AI Tutor API"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://ai_tutor:local-development-only@localhost:5433/ai_tutor",
    )


settings = Settings()
