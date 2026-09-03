import argparse
import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "apps" / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings  # noqa: E402
from app.db.session import SessionFactory  # noqa: E402
from app.services.document_chunks import (  # noqa: E402
    DocumentChunkingError,
    extract_document_chunks,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="登録済みPDFをページ単位のチャンクとしてDBへ保存します"
    )
    parser.add_argument("document_id", help="処理するDocument ID")
    parser.add_argument("kc_id", help="チャンクへ付与するKC ID")
    args = parser.parse_args()

    try:
        with SessionFactory.begin() as session:
            result = extract_document_chunks(
                session,
                document_id=args.document_id,
                kc_id=args.kc_id,
                storage_dir=settings.document_storage_dir,
            )
    except DocumentChunkingError as error:
        print(f"Document chunking failed: {error}", file=sys.stderr)
        return 1
    except SQLAlchemyError as error:
        print(f"Document chunking failed: database error: {error}", file=sys.stderr)
        return 1

    print(
        "Document chunking completed: "
        f"document_id={result.document_id} kc_id={result.kc_id} "
        f"created={result.created}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
