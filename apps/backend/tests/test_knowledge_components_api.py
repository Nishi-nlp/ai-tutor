from collections.abc import Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import KnowledgeComponent
from app.db.session import get_db_session
from app.main import app


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def _override_db_session(session: Session) -> None:
    def override() -> Session:
        return session

    app.dependency_overrides[get_db_session] = override


@pytest.mark.anyio
async def test_get_knowledge_component(db_session: Session) -> None:
    db_session.add(
        KnowledgeComponent(
            id="la.linear_combination",
            name="線形結合",
            description="複数のベクトルをスカラー倍して加えたもの",
            prerequisites=[],
            learning_objectives=[
                "線形結合を説明できる",
                "線形結合を計算できる",
            ],
            source_refs=[],
            mastery_threshold=0.85,
            required_evidence=["no_hint_full_correct"],
        )
    )
    db_session.commit()
    _override_db_session(db_session)

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/kcs/la.linear_combination")
    finally:
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 200
    assert response.json() == {
        "id": "la.linear_combination",
        "name": "線形結合",
        "description": "複数のベクトルをスカラー倍して加えたもの",
        "learning_objectives": [
            "線形結合を説明できる",
            "線形結合を計算できる",
        ],
        "prerequisites": [],
    }


@pytest.mark.anyio
async def test_get_missing_knowledge_component_returns_404(
    db_session: Session,
) -> None:
    _override_db_session(db_session)

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/kcs/la.missing")
    finally:
        app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Knowledge component not found"}
