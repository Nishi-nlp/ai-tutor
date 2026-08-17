from sqlalchemy import text
from sqlalchemy.orm import Session


def check_connection(session: Session) -> None:
    session.execute(text("SELECT 1"))
