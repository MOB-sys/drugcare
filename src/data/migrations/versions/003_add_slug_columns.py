"""drugs, supplements 테이블에 slug 컬럼 추가.

Revision ID: 003
Revises: 002
Create Date: 2026-02-26

웹 SSG(generateStaticParams)용 slug 기반 URL 지원.
slug 형식: drug-{item_seq}, supp-{id}
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """drugs, supplements에 slug 컬럼을 추가한다."""

    # --- drugs.slug ---
    op.add_column("drugs", sa.Column("slug", sa.String(200), nullable=True))

    # 기존 행 populate: drug-{item_seq}
    op.execute("UPDATE drugs SET slug = 'drug-' || item_seq WHERE slug IS NULL")

    # NOT NULL + UNIQUE 제약 적용
    op.alter_column("drugs", "slug", nullable=False)
    op.create_unique_constraint("uq_drugs_slug", "drugs", ["slug"])
    op.create_index("ix_drugs_slug", "drugs", ["slug"], unique=True)

    # --- supplements.slug ---
    op.add_column("supplements", sa.Column("slug", sa.String(200), nullable=True))

    # 기존 행 populate: supp-{id}
    op.execute("UPDATE supplements SET slug = 'supp-' || id WHERE slug IS NULL")

    # NOT NULL + UNIQUE 제약 적용
    op.alter_column("supplements", "slug", nullable=False)
    op.create_unique_constraint("uq_supplements_slug", "supplements", ["slug"])
    op.create_index("ix_supplements_slug", "supplements", ["slug"], unique=True)


def downgrade() -> None:
    """slug 컬럼을 삭제한다."""

    op.drop_index("ix_supplements_slug", table_name="supplements")
    op.drop_constraint("uq_supplements_slug", "supplements", type_="unique")
    op.drop_column("supplements", "slug")

    op.drop_index("ix_drugs_slug", table_name="drugs")
    op.drop_constraint("uq_drugs_slug", "drugs", type_="unique")
    op.drop_column("drugs", "slug")
