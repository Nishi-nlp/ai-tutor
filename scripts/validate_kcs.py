import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.content.kc_yaml import KcValidationError, validate_kc_directory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="KC YAMLを検証します")
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=PROJECT_ROOT / "data" / "kcs",
        help="検証するKC YAMLディレクトリ",
    )
    args = parser.parse_args()

    try:
        definitions = validate_kc_directory(args.directory)
    except KcValidationError as error:
        print(f"KC YAML validation failed:\n{error}", file=sys.stderr)
        return 1

    print(f"KC YAML validation passed: {len(definitions)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
