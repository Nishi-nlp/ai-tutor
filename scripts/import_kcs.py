import argparse
import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.content.kc_yaml import KcValidationError, validate_kc_directory  # noqa: E402
from app.db.session import SessionFactory  # noqa: E402
from app.services.kc_import import upsert_kc_definitions  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="KC YAMLをDBへ登録します")
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=PROJECT_ROOT / "data" / "kcs",
        help="登録するKC YAMLディレクトリ",
    )
    args = parser.parse_args()

    try:
        definitions = validate_kc_directory(args.directory)
        with SessionFactory.begin() as session:
            result = upsert_kc_definitions(session, definitions)
    except KcValidationError as error:
        print(f"KC import failed:\n{error}", file=sys.stderr)
        return 1
    except SQLAlchemyError as error:
        print(f"KC import failed: database error: {error}", file=sys.stderr)
        return 1

    print(
        "KC import completed: "
        f"created={result.created} updated={result.updated} "
        f"total={len(definitions)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
