import hashlib
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


@dataclass(frozen=True)
class StoredDocument:
    path: Path
    size_bytes: int
    checksum_sha256: str


def save_document(
    content: bytes,
    storage_key: str,
    storage_dir: Path | None = None,
) -> StoredDocument:
    if (
        not storage_key
        or storage_key in {".", ".."}
        or "/" in storage_key
        or "\\" in storage_key
    ):
        raise ValueError("storage_key must be a file name")

    target_dir = storage_dir or settings.document_storage_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / storage_key
    with target_path.open("xb") as stored_file:
        stored_file.write(content)

    return StoredDocument(
        path=target_path,
        size_bytes=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
    )
