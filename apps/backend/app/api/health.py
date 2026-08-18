from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import health as database_health
from app.db.session import get_db_session

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/database")
def health_database(
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str]:
    database_health.check_connection(session)
    return {"status": "ok"}
