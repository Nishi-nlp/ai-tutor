# PDF test fixture

`sample-linear-algebra.pdf` is a small, project-authored teaching document for
PDF ingestion, text extraction, page citation, chunking, and search tests. It is
not an external textbook.

The fixture contents are dedicated to the public domain under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

Regenerate it from the repository root with:

```console
uv run --with reportlab python scripts/generate_sample_pdf.py
```
