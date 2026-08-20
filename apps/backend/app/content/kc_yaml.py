from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SourceReference(StrictModel):
    document: NonEmptyString
    pages: list[int] = Field(min_length=1)
    relation: NonEmptyString


class MasteryDefinition(StrictModel):
    threshold: float = Field(ge=0, le=1)
    required_evidence: list[NonEmptyString] = Field(min_length=1)


class KnowledgeComponentDefinition(StrictModel):
    id: NonEmptyString
    name: NonEmptyString
    description: NonEmptyString
    prerequisites: list[NonEmptyString]
    learning_objectives: list[NonEmptyString] = Field(min_length=1)
    source_refs: list[SourceReference] = Field(default_factory=list)
    mastery: MasteryDefinition


class KcValidationError(ValueError):
    """Raised when KC YAML cannot be loaded or validated."""


def _format_validation_error(error: ValidationError) -> str:
    messages = []
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"])
        messages.append(f"{location}: {detail['msg']}")
    return "\n".join(messages)


def load_kc_file(path: Path) -> KnowledgeComponentDefinition:
    try:
        raw_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise KcValidationError(f"{path}: YAMLを読み込めません: {error}") from error

    try:
        return KnowledgeComponentDefinition.model_validate(raw_data)
    except ValidationError as error:
        details = _format_validation_error(error)
        raise KcValidationError(f"{path}: KC YAMLが不正です:\n{details}") from error


def validate_kc_directory(directory: Path) -> list[KnowledgeComponentDefinition]:
    paths = sorted(directory.glob("*.yaml"))
    if not paths:
        raise KcValidationError(f"{directory}: KC YAMLが見つかりません")

    loaded = [(path, load_kc_file(path)) for path in paths]
    known_ids = {definition.id for _, definition in loaded}

    missing_prerequisites = []
    for path, definition in loaded:
        for prerequisite_id in definition.prerequisites:
            if prerequisite_id not in known_ids:
                missing_prerequisites.append(
                    f"{path}: 前提KC '{prerequisite_id}' が存在しません"
                )

    if missing_prerequisites:
        raise KcValidationError("\n".join(missing_prerequisites))

    return [definition for _, definition in loaded]
