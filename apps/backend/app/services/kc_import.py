from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.content.kc_yaml import KnowledgeComponentDefinition
from app.db.models import KnowledgeComponent


@dataclass(frozen=True)
class KcImportResult:
    created: int
    updated: int


def _definition_values(
    definition: KnowledgeComponentDefinition,
) -> dict[str, object]:
    return {
        "name": definition.name,
        "description": definition.description,
        "prerequisites": list(definition.prerequisites),
        "learning_objectives": list(definition.learning_objectives),
        "source_refs": [reference.model_dump() for reference in definition.source_refs],
        "mastery_threshold": definition.mastery.threshold,
        "required_evidence": list(definition.mastery.required_evidence),
    }


def upsert_kc_definitions(
    session: Session,
    definitions: Sequence[KnowledgeComponentDefinition],
) -> KcImportResult:
    created = 0
    updated = 0

    for definition in definitions:
        values = _definition_values(definition)
        existing = session.get(KnowledgeComponent, definition.id)

        if existing is None:
            session.add(KnowledgeComponent(id=definition.id, **values))
            created += 1
            continue

        for field_name, value in values.items():
            setattr(existing, field_name, value)
        updated += 1

    return KcImportResult(created=created, updated=updated)
