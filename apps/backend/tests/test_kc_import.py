from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.content.kc_yaml import (
    KnowledgeComponentDefinition,
    validate_kc_directory,
)
from app.db.base import Base
from app.db.models import KnowledgeComponent
from app.services.kc_import import KcImportResult, upsert_kc_definitions

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _definition(*, name: str = "線形結合") -> KnowledgeComponentDefinition:
    return KnowledgeComponentDefinition.model_validate(
        {
            "id": "la.linear_combination",
            "name": name,
            "description": "複数のベクトルをスカラー倍して加えたもの",
            "prerequisites": [],
            "learning_objectives": ["線形結合を計算できる"],
            "source_refs": [],
            "mastery": {
                "threshold": 0.85,
                "required_evidence": ["no_hint_full_correct"],
            },
        }
    )


def _kc_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(KnowledgeComponent)) or 0


def test_reimport_updates_without_creating_duplicate() -> None:
    session_factory = _session_factory()

    with session_factory.begin() as session:
        first_result = upsert_kc_definitions(session, [_definition()])

    with session_factory.begin() as session:
        second_result = upsert_kc_definitions(
            session,
            [_definition(name="更新された線形結合")],
        )

    with session_factory() as session:
        saved = session.get(KnowledgeComponent, "la.linear_combination")

        assert first_result == KcImportResult(created=1, updated=0)
        assert second_result == KcImportResult(created=0, updated=1)
        assert _kc_count(session) == 1
        assert saved is not None
        assert saved.name == "更新された線形結合"


def test_current_kc_yaml_can_be_imported_twice() -> None:
    session_factory = _session_factory()
    definitions = validate_kc_directory(PROJECT_ROOT / "data" / "kcs")

    with session_factory.begin() as session:
        upsert_kc_definitions(session, definitions)

    with session_factory.begin() as session:
        upsert_kc_definitions(session, definitions)

    with session_factory() as session:
        saved = session.get(KnowledgeComponent, "la.linear_combination")

        assert _kc_count(session) == 1
        assert saved is not None
        assert saved.learning_objectives == definitions[0].learning_objectives
        assert saved.mastery_threshold == definitions[0].mastery.threshold


def test_transaction_rolls_back_when_import_fails() -> None:
    session_factory = _session_factory()

    with (
        pytest.raises(RuntimeError, match="import failed"),
        session_factory.begin() as session,
    ):
        upsert_kc_definitions(session, [_definition()])
        raise RuntimeError("import failed")

    with session_factory() as session:
        assert _kc_count(session) == 0
