"""피드백 및 메트릭스 테이블 추가.

Revision ID: 002
Revises: 001
Create Date: 2026-02-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """feedbacks, app_metrics 테이블을 생성한다."""

    # --- feedbacks 테이블 ---
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("app_version", sa.String(20), nullable=False, server_default="1.0.0"),
        sa.Column("os_info", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedbacks_device_id", "feedbacks", ["device_id"])
    op.create_index("ix_feedbacks_category", "feedbacks", ["category"])

    # --- app_metrics 테이블 ---
    op.create_table(
        "app_metrics",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_data", sa.JSON(), nullable=True),
        sa.Column("app_version", sa.String(20), nullable=False, server_default="1.0.0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_app_metrics_device_id", "app_metrics", ["device_id"])
    op.create_index("ix_app_metrics_event_type", "app_metrics", ["event_type"])
    op.create_index("ix_app_metrics_created_at", "app_metrics", ["created_at"])


def downgrade() -> None:
    """feedbacks, app_metrics 테이블을 삭제한다."""

    op.drop_index("ix_app_metrics_created_at", table_name="app_metrics")
    op.drop_index("ix_app_metrics_event_type", table_name="app_metrics")
    op.drop_index("ix_app_metrics_device_id", table_name="app_metrics")
    op.drop_table("app_metrics")

    op.drop_index("ix_feedbacks_category", table_name="feedbacks")
    op.drop_index("ix_feedbacks_device_id", table_name="feedbacks")
    op.drop_table("feedbacks")
