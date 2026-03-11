"""foods, herbal_medicines 테이블 추가 및 enum 확장.

Revision ID: 006
Revises: 005
Create Date: 2026-03-11

식품(foods)과 한약재(herbal_medicines) 테이블을 생성하고,
ItemType / CabinetItemType enum에 'food', 'herbal' 값을 추가한다.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """enum 확장 + foods / herbal_medicines 테이블을 생성한다."""

    # --- 1) enum 타입 확장 (Alembic은 PG enum 변경 미지원 → raw SQL) ---
    op.execute("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'food'")
    op.execute("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'herbal'")
    op.execute("ALTER TYPE cabinetitemtype ADD VALUE IF NOT EXISTS 'food'")
    op.execute("ALTER TYPE cabinetitemtype ADD VALUE IF NOT EXISTS 'herbal'")

    # --- 2) foods 테이블 ---
    op.create_table(
        "foods",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("common_names", JSONB, nullable=True),
        sa.Column("nutrients", JSONB, nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
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
        sa.UniqueConstraint("slug", name="uq_foods_slug"),
    )

    op.create_index("ix_foods_name", "foods", ["name"])
    op.create_index("ix_foods_slug", "foods", ["slug"])
    op.create_index(
        "ix_foods_common_names_gin",
        "foods",
        ["common_names"],
        postgresql_using="gin",
    )

    # --- 3) herbal_medicines 테이블 ---
    op.create_table(
        "herbal_medicines",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("korean_name", sa.String(200), nullable=True),
        sa.Column("latin_name", sa.String(300), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("properties", JSONB, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("efficacy", sa.Text, nullable=True),
        sa.Column("precautions", sa.Text, nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
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
        sa.UniqueConstraint("slug", name="uq_herbal_medicines_slug"),
    )

    op.create_index("ix_herbal_medicines_name", "herbal_medicines", ["name"])
    op.create_index("ix_herbal_medicines_slug", "herbal_medicines", ["slug"])
    op.create_index(
        "ix_herbal_medicines_properties_gin",
        "herbal_medicines",
        ["properties"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    """foods / herbal_medicines 테이블을 삭제한다.

    주의: PostgreSQL에서 ALTER TYPE ... REMOVE VALUE는 지원되지 않으므로,
    enum 값 제거는 수동으로 타입을 재생성해야 한다.
    """
    op.drop_index("ix_herbal_medicines_properties_gin", table_name="herbal_medicines")
    op.drop_index("ix_herbal_medicines_slug", table_name="herbal_medicines")
    op.drop_index("ix_herbal_medicines_name", table_name="herbal_medicines")
    op.drop_table("herbal_medicines")

    op.drop_index("ix_foods_common_names_gin", table_name="foods")
    op.drop_index("ix_foods_slug", table_name="foods")
    op.drop_index("ix_foods_name", table_name="foods")
    op.drop_table("foods")
