import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import KnowledgeComponent


def _knowledge_component(*, mastery_threshold: float = 0.85) -> KnowledgeComponent:
    return KnowledgeComponent(
        id="la.linear_combination",
        name="線形結合",
        description="複数のベクトルをスカラー倍して加えたもの",
        prerequisites=[],
        learning_objectives=[
            "線形結合を説明できる",
            "線形結合を計算できる",
        ],
        source_refs=[
            {
                "document": "strang",
                "pages": [12, 13],
                "relation": "explanation",
            }
        ],
        mastery_threshold=mastery_threshold,
        required_evidence=["no_hint_full_correct"],
    )


def test_knowledge_component_can_be_saved_and_loaded() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(_knowledge_component())
        session.commit()

    with Session(engine) as session:
        saved = session.get(KnowledgeComponent, "la.linear_combination")

        assert saved is not None
        assert saved.name == "線形結合"
        assert saved.prerequisites == []
        assert saved.learning_objectives == [
            "線形結合を説明できる",
            "線形結合を計算できる",
        ]
        assert saved.source_refs[0]["pages"] == [12, 13]
        assert saved.mastery_threshold == 0.85
        assert saved.required_evidence == ["no_hint_full_correct"]

    engine.dispose()


def test_mastery_threshold_must_be_between_zero_and_one() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(_knowledge_component(mastery_threshold=1.1))

        with pytest.raises(IntegrityError):
            session.commit()

    engine.dispose()
