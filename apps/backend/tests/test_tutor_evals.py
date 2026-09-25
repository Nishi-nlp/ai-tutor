import json
from pathlib import Path

import pytest

from evals.run import _read_items, evaluate

ROOT = Path(__file__).resolve().parents[1] / "evals"


def test_recorded_contract_cases_pass() -> None:
    cases = _read_items(ROOT / "cases.json", "cases")
    responses = _read_items(ROOT / "fixtures" / "responses.json", "responses")
    assert len(cases) == 10
    assert evaluate(cases, responses)["passed"] == 10


def test_wrong_citation_and_missing_response_fail() -> None:
    cases = _read_items(ROOT / "cases.json", "cases")
    responses = _read_items(ROOT / "fixtures" / "responses.json", "responses")
    responses[0]["citations"] = ["other:p999"]
    responses.pop()
    results = evaluate(cases, responses)["results"]
    assert "duplicate or unprovided citation" in results[0]["failures"]
    assert "missing response" in results[-1]["failures"]


def test_hallucinated_answer_fails_even_if_marked_unsupported() -> None:
    cases = _read_items(ROOT / "cases.json", "cases")
    responses = _read_items(ROOT / "fixtures" / "responses.json", "responses")
    responses[-2]["answer"] = "秘密は123です。"
    assert not evaluate(cases, responses)["results"][-2]["passed"]


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "responses.json"
    path.write_text(json.dumps({"responses": [{"id": "a"}, {"id": "a"}]}))
    with pytest.raises(ValueError, match="duplicate case IDs"):
        _read_items(path, "responses")
