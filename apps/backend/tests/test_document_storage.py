import hashlib
from pathlib import Path

import pytest

from app.storage import save_document


def test_save_document_writes_to_private_storage(tmp_path: Path) -> None:
    content = b"%PDF-1.4 sample"

    stored = save_document(content, "document-id.pdf", tmp_path)

    assert stored.path == tmp_path / "document-id.pdf"
    assert stored.path.read_bytes() == content
    assert stored.size_bytes == len(content)
    assert stored.checksum_sha256 == hashlib.sha256(content).hexdigest()


@pytest.mark.parametrize(
    "storage_key",
    ["", ".", "..", "../outside.pdf", "nested/file.pdf", "nested\\file.pdf"],
)
def test_save_document_rejects_non_file_storage_key(
    tmp_path: Path,
    storage_key: str,
) -> None:
    with pytest.raises(ValueError, match="storage_key must be a file name"):
        save_document(b"content", storage_key, tmp_path)


def test_save_document_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    save_document(b"first", "document-id.pdf", tmp_path)

    with pytest.raises(FileExistsError):
        save_document(b"second", "document-id.pdf", tmp_path)

    assert (tmp_path / "document-id.pdf").read_bytes() == b"first"
