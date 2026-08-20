from pathlib import Path

import pytest

from app.content.kc_yaml import KcValidationError, validate_kc_directory

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_linear_combination_kc_is_valid() -> None:
    definitions = validate_kc_directory(PROJECT_ROOT / "data" / "kcs")

    assert [definition.id for definition in definitions] == ["la.linear_combination"]


def test_missing_required_field_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "invalid.yaml").write_text(
        """
id: la.invalid
description: 名前がないKC
prerequisites: []
learning_objectives:
  - 検証できる
mastery:
  threshold: 0.85
  required_evidence:
    - no_hint_full_correct
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(KcValidationError, match="name: Field required"):
        validate_kc_directory(tmp_path)


def test_unknown_field_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "invalid.yaml").write_text(
        """
id: la.invalid
name: 不正なKC
description: 項目名にスペルミスがある
descripton: この項目は許可されない
prerequisites: []
learning_objectives:
  - 検証できる
mastery:
  threshold: 0.85
  required_evidence:
    - no_hint_full_correct
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(KcValidationError, match="descripton: Extra inputs"):
        validate_kc_directory(tmp_path)


def test_missing_prerequisite_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "invalid.yaml").write_text(
        """
id: la.invalid
name: 不正なKC
description: 存在しない前提KCを参照する
prerequisites:
  - la.missing
learning_objectives:
  - 検証できる
mastery:
  threshold: 0.85
  required_evidence:
    - no_hint_full_correct
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(KcValidationError, match="前提KC 'la.missing' が存在しません"):
        validate_kc_directory(tmp_path)
