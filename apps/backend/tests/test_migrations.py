from app.db.base import Base


def test_baseline_has_no_domain_tables() -> None:
    assert Base.metadata.tables == {}
