from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.db import session as session_module


class FakeSession:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_get_db_session_closes_session(monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    monkeypatch.setattr(session_module, "SessionFactory", lambda: session)

    dependency: Generator[Session, None, None] = session_module.get_db_session()

    assert next(dependency) is session
    dependency.close()

    assert session.closed is True
