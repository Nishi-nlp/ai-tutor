from app.core.config import settings


def test_app_title() -> None:
    assert settings.app_title == "AI Tutor API"


def test_database_url_uses_local_database_by_default() -> None:
    assert settings.database_url.endswith("@localhost:5433/ai_tutor")
