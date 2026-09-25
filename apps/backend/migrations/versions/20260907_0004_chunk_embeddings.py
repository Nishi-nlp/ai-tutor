"""Add embeddings to document chunks.

Revision ID: 20260907_0004
Revises: 20260826_0003
Create Date: 2026-09-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "20260907_0004"
down_revision: str | Sequence[str] | None = "20260826_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIMENSIONS = 1536


def upgrade() -> None:
    with op.batch_alter_table("document_chunks") as batch_op:
        batch_op.add_column(
            sa.Column(
                "embedding",
                Vector(EMBEDDING_DIMENSIONS),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column("embedding_model", sa.String(length=100), nullable=True)
        )
        batch_op.create_check_constraint(
            "ck_document_chunks_embedding_pair",
            "(embedding IS NULL AND embedding_model IS NULL) OR "
            "(embedding IS NOT NULL AND embedding_model IS NOT NULL)",
        )


def downgrade() -> None:
    with op.batch_alter_table("document_chunks") as batch_op:
        batch_op.drop_constraint(
            "ck_document_chunks_embedding_pair",
            type_="check",
        )
        batch_op.drop_column("embedding_model")
        batch_op.drop_column("embedding")
