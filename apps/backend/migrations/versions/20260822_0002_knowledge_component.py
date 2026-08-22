"""Create the knowledge_components table.

Revision ID: 20260822_0002
Revises: 20260813_0001
Create Date: 2026-08-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260822_0002"
down_revision: str | Sequence[str] | None = "20260813_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_components",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("prerequisites", sa.JSON(), nullable=False),
        sa.Column("learning_objectives", sa.JSON(), nullable=False),
        sa.Column("source_refs", sa.JSON(), nullable=False),
        sa.Column("mastery_threshold", sa.Float(), nullable=False),
        sa.Column("required_evidence", sa.JSON(), nullable=False),
        sa.CheckConstraint(
            "mastery_threshold >= 0.0 AND mastery_threshold <= 1.0",
            name="ck_knowledge_components_mastery_threshold",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("knowledge_components")
