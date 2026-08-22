from sqlalchemy import JSON, CheckConstraint, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeComponent(Base):
    __tablename__ = "knowledge_components"
    __table_args__ = (
        CheckConstraint(
            "mastery_threshold >= 0.0 AND mastery_threshold <= 1.0",
            name="ck_knowledge_components_mastery_threshold",
        ),
    )

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    learning_objectives: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    source_refs: Mapped[list[dict[str, object]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    mastery_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    required_evidence: Mapped[list[str]] = mapped_column(JSON, nullable=False)
