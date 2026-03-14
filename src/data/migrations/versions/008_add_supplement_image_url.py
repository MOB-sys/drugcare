"""supplements 테이블에 image_url 컬럼 추가.

Revision ID: 008
Revises: 007
Create Date: 2026-03-14

영양제(Supplement) 이미지 수집 파이프라인을 위해
supplements 테이블에 image_url 컬럼을 추가한다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """supplements 테이블에 image_url 컬럼을 추가한다."""
    op.add_column(
        "supplements",
        sa.Column("image_url", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    """image_url 컬럼을 제거한다."""
    op.drop_column("supplements", "image_url")
