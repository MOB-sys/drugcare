"""성능 및 안전 인덱스 추가 + PostgreSQL 쿼리 타임아웃 설정.

Revision ID: 010
Revises: 009
Create Date: 2026-03-15

interactions 테이블에 역방향 복합 인덱스를 추가하여 (item_b → item_a) 조회 성능을 개선하고,
user_cabinets 테이블에 device_id + created_at 복합 인덱스를 추가한다.
또한 PostgreSQL 롤 수준 statement_timeout / idle_in_transaction_session_timeout 을 설정하여
장시간 실행 쿼리 및 유휴 트랜잭션을 방지한다.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """역방향 상호작용 인덱스 + 복약함 복합 인덱스 + 쿼리 타임아웃 설정."""

    # --- 1) interactions 역방향 복합 인덱스 ---
    op.create_index(
        "ix_interactions_pair_rev",
        "interactions",
        ["item_b_type", "item_b_id", "item_a_type", "item_a_id"],
    )

    # --- 2) user_cabinets device_id + created_at 복합 인덱스 ---
    op.create_index(
        "ix_user_cabinets_device_created",
        "user_cabinets",
        ["device_id", "created_at"],
    )

    # --- 3) PostgreSQL 쿼리 타임아웃 설정 ---
    op.execute("ALTER ROLE yakmeogeo SET statement_timeout = '30s'")
    op.execute("ALTER ROLE yakmeogeo SET idle_in_transaction_session_timeout = '120s'")


def downgrade() -> None:
    """인덱스 삭제 + 타임아웃 리셋."""
    op.execute("ALTER ROLE yakmeogeo RESET idle_in_transaction_session_timeout")
    op.execute("ALTER ROLE yakmeogeo RESET statement_timeout")
    op.drop_index("ix_user_cabinets_device_created", table_name="user_cabinets")
    op.drop_index("ix_interactions_pair_rev", table_name="interactions")
