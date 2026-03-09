"""drug_reviews 테이블 추가 — 약물/영양제 리뷰 및 평점.

Revision ID: 005
Revises: 004
Create Date: 2026-03-09

사용자가 약물/영양제에 대해 리뷰와 평점을 남길 수 있는
drug_reviews 테이블을 생성한다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """drug_reviews 테이블을 생성한다."""

    op.create_table(
        "drug_reviews",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.String(100), nullable=False),
        sa.Column("item_type", sa.String(20), nullable=False),
        sa.Column("item_id", sa.BigInteger, nullable=False),
        sa.Column("rating", sa.SmallInteger, nullable=False),
        sa.Column("effectiveness", sa.SmallInteger, nullable=True),
        sa.Column("ease_of_use", sa.SmallInteger, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("helpful_count", sa.Integer, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("device_id", "item_type", "item_id", name="uq_review_device_item"),
    )

    op.create_index(
        "ix_drug_reviews_item",
        "drug_reviews",
        ["item_type", "item_id"],
    )


def downgrade() -> None:
    """drug_reviews 테이블을 삭제한다."""
    op.drop_index("ix_drug_reviews_item", table_name="drug_reviews")
    op.drop_table("drug_reviews")
