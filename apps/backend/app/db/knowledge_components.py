from sqlalchemy.orm import Session

from app.db.models import KnowledgeComponent


def get_by_id(session: Session, kc_id: str) -> KnowledgeComponent | None:
    return session.get(KnowledgeComponent, kc_id)
