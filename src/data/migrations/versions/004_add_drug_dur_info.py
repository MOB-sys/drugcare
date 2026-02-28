"""drug_dur_info 테이블 추가 — DUR 안전성 정보 저장.

Revision ID: 004
Revises: 003
Create Date: 2026-02-28

임부금기, 노인주의, 용량주의, 투여기간주의, 효능군중복 등
약물별 DUR 안전성 경고 데이터를 저장한다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """drug_dur_info 테이블을 생성한다."""

    op.create_table(
        "drug_dur_info",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("item_seq", sa.String(20), nullable=False, index=True),
        sa.Column("dur_type", sa.String(30), nullable=False, index=True),
        sa.Column("type_name", sa.String(50)),
        sa.Column("ingr_code", sa.String(20)),
        sa.Column("ingr_name", sa.String(200)),
        sa.Column("ingr_eng_name", sa.String(200)),
        sa.Column("prohibition_content", sa.Text),
        sa.Column("remark", sa.Text),
        sa.Column("notification_date", sa.String(8)),
        sa.Column("source_id", sa.String(100), unique=True, nullable=False),
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
    )


def downgrade() -> None:
    """drug_dur_info 테이블을 삭제한다."""
    op.drop_table("drug_dur_info")
