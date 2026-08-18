import pytest
from httpx import ASGITransport, AsyncClient

from app.api import health as health_api
from app.db.session import get_db_session
from app.main import app


@pytest.mark.anyio
async def test_health() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_database_health(monkeypatch: pytest.MonkeyPatch) -> None:
    session = object()
    checked_sessions: list[object] = []

    monkeypatch.setattr(
        health_api.database_health,
        "check_connection",
        checked_sessions.append,
    )

    def override_db_session() -> object:
        return session

    app.dependency_overrides[get_db_session] = override_db_session

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health/database")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert checked_sessions == [session]
