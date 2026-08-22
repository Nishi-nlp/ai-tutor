from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.db.models import KnowledgeComponent  # noqa: F401

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def _table_names(database_url: str) -> set[str]:
    engine = create_engine(database_url)
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_metadata_contains_knowledge_components_table() -> None:
    assert "knowledge_components" in Base.metadata.tables


def test_migration_upgrade_and_downgrade(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"
    config = _alembic_config(database_url)

    command.upgrade(config, "head")

    assert "knowledge_components" in _table_names(database_url)

    command.downgrade(config, "20260813_0001")

    assert "knowledge_components" not in _table_names(database_url)
