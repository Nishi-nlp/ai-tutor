"""Score tutor responses against a small, versioned question set.

Run from apps/backend: python -m evals.run --responses evals/fixtures/responses.json
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

CASES_PATH = Path(__file__).parent / "cases.json"


def _read_items(path: Path, key: str) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data[key]
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f"{path}: {key} must be a list of objects")
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: duplicate case IDs")
    return items


def evaluate(cases: list[dict], responses: list[dict]) -> dict:
    """Check structured output, grounded citations and literal key concepts.

    This is a contract/keyword check, not a semantic correctness judge.
    """
    by_id = {item["id"]: item for item in responses}
    if len(by_id) != len(responses):
        raise ValueError("duplicate response IDs")
    case_ids = {case["id"] for case in cases}
    extra = sorted(by_id.keys() - case_ids)
    if extra:
        raise ValueError(f"unknown response IDs: {extra}")

    results = []
    for case in cases:
        response = by_id.get(case["id"])
        failures = []
        if response is None:
            failures.append("missing response")
        else:
            answer = response.get("answer")
            citations = response.get("citations")
            supported = response.get("supported")
            if not isinstance(answer, str) or not answer.strip():
                failures.append("answer must be nonempty text")
            if not isinstance(citations, list) or any(
                not isinstance(citation, str) for citation in citations
            ):
                failures.append("citations must be a list of IDs")
            if not isinstance(supported, bool):
                failures.append("supported must be a boolean")
            if not failures:
                allowed = set(case["source_ids"])
                if (
                    len(citations) != len(set(citations))
                    or not set(citations) <= allowed
                ):
                    failures.append("duplicate or unprovided citation")
                if supported != case["expect_supported"]:
                    failures.append("incorrect supported status")
                if case["expect_supported"] and not citations:
                    failures.append("supported answer needs a citation")
                if not case["expect_supported"] and citations:
                    failures.append("unsupported answer must not cite a source")
                for group in case["required_any"]:
                    if not any(term.casefold() in answer.casefold() for term in group):
                        failures.append(f"missing concept: {' / '.join(group)}")
                for term in case.get("forbidden", []):
                    if term.casefold() in answer.casefold():
                        failures.append(f"forbidden text: {term}")
        results.append({"id": case["id"], "passed": not failures, "failures": failures})

    passed = sum(item["passed"] for item in results)
    return {
        "total": len(cases),
        "passed": passed,
        "pass_rate": passed / len(cases) if cases else 0,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=CASES_PATH)
    parser.add_argument("--responses", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("eval-results.json"))
    args = parser.parse_args()
    try:
        cases = _read_items(args.cases, "cases")
        responses = _read_items(args.responses, "responses")
        if len(cases) != 10:
            raise ValueError("expected exactly 10 evaluation cases")
        report = evaluate(cases, responses)
        report["generated_at"] = datetime.now(UTC).isoformat()
        report["response_file"] = str(args.responses)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"evaluation input error: {error}\n")
    print(f"Tutor eval: {report['passed']}/{report['total']} passed; {args.output}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
