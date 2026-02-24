"""초기 스키마 생성 — drugs, supplements, interactions, user_cabinets, reminders.

Revision ID: 001
Revises: None
Create Date: 2026-02-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum 타입 정의
item_type_enum = postgresql.ENUM("drug", "supplement", name="itemtype", create_type=False)
severity_enum = postgresql.ENUM("danger", "warning", "caution", "info", name="severity", create_type=False)
cabinet_item_type_enum = postgresql.ENUM("drug", "supplement", name="cabinetitemtype", create_type=False)


def upgrade() -> None:
    """모든 테이블 및 인덱스를 생성한다."""

    # Enum 타입 생성
    op.execute("CREATE TYPE itemtype AS ENUM ('drug', 'supplement')")
    op.execute("CREATE TYPE severity AS ENUM ('danger', 'warning', 'caution', 'info')")
    op.execute("CREATE TYPE cabinetitemtype AS ENUM ('drug', 'supplement')")

    # --- drugs 테이블 ---
    op.create_table(
        "drugs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("item_seq", sa.String(20), nullable=False),
        sa.Column("item_name", sa.String(500), nullable=False),
        sa.Column("entp_name", sa.String(200), nullable=True),
        sa.Column("etc_otc_code", sa.String(20), nullable=True),
        sa.Column("class_no", sa.String(10), nullable=True),
        sa.Column("chart", sa.Text(), nullable=True),
        sa.Column("bar_code", sa.String(50), nullable=True),
        sa.Column("material_name", sa.Text(), nullable=True),
        sa.Column("ingredients", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("efcy_qesitm", sa.Text(), nullable=True),
        sa.Column("use_method_qesitm", sa.Text(), nullable=True),
        sa.Column("atpn_warn_qesitm", sa.Text(), nullable=True),
        sa.Column("atpn_qesitm", sa.Text(), nullable=True),
        sa.Column("intrc_qesitm", sa.Text(), nullable=True),
        sa.Column("se_qesitm", sa.Text(), nullable=True),
        sa.Column("deposit_method_qesitm", sa.Text(), nullable=True),
        sa.Column("item_image", sa.String(500), nullable=True),
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
        sa.UniqueConstraint("item_seq"),
    )

    # drugs 인덱스
    op.create_index("ix_drugs_item_seq", "drugs", ["item_seq"])
    op.create_index("ix_drugs_item_name", "drugs", ["item_name"])
    op.create_index(
        "ix_drugs_ingredients_gin",
        "drugs",
        ["ingredients"],
        postgresql_using="gin",
    )

    # --- supplements 테이블 ---
    op.create_table(
        "supplements",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_name", sa.String(500), nullable=False),
        sa.Column("company", sa.String(200), nullable=True),
        sa.Column("registration_no", sa.String(50), nullable=True),
        sa.Column("main_ingredient", sa.String(200), nullable=True),
        sa.Column("ingredients", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("functionality", sa.Text(), nullable=True),
        sa.Column("precautions", sa.Text(), nullable=True),
        sa.Column("intake_method", sa.Text(), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
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
        sa.UniqueConstraint("registration_no"),
    )

    # supplements 인덱스
    op.create_index("ix_supplements_product_name", "supplements", ["product_name"])
    op.create_index(
        "ix_supplements_ingredients_gin",
        "supplements",
        ["ingredients"],
        postgresql_using="gin",
    )

    # --- interactions 테이블 ---
    op.create_table(
        "interactions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("item_a_type", item_type_enum, nullable=False),
        sa.Column("item_a_id", sa.BigInteger(), nullable=False),
        sa.Column("item_a_name", sa.String(500), nullable=False),
        sa.Column("item_b_type", item_type_enum, nullable=False),
        sa.Column("item_b_id", sa.BigInteger(), nullable=False),
        sa.Column("item_b_name", sa.String(500), nullable=False),
        sa.Column("severity", severity_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mechanism", sa.Text(), nullable=True),
        sa.Column("recommendation", sa.Text(), nullable=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column("evidence_level", sa.String(50), nullable=True),
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

    # interactions 인덱스
    op.create_index(
        "ix_interactions_pair",
        "interactions",
        ["item_a_type", "item_a_id", "item_b_type", "item_b_id"],
    )
    op.create_index(
        "ix_interactions_item_a",
        "interactions",
        ["item_a_type", "item_a_id"],
    )
    op.create_index(
        "ix_interactions_item_b",
        "interactions",
        ["item_b_type", "item_b_id"],
    )
    op.create_index("ix_interactions_severity", "interactions", ["severity"])

    # --- user_cabinets 테이블 ---
    op.create_table(
        "user_cabinets",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(100), nullable=False),
        sa.Column("item_type", cabinet_item_type_enum, nullable=False),
        sa.Column("item_id", sa.BigInteger(), nullable=False),
        sa.Column("item_name", sa.String(500), nullable=False),
        sa.Column("nickname", sa.String(200), nullable=True),
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

    # user_cabinets 인덱스
    op.create_index("ix_user_cabinets_device_id", "user_cabinets", ["device_id"])
    op.create_index(
        "ix_user_cabinets_device_item",
        "user_cabinets",
        ["device_id", "item_type", "item_id"],
        unique=True,
    )

    # --- reminders 테이블 ---
    op.create_table(
        "reminders",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.String(100), nullable=False),
        sa.Column("cabinet_item_id", sa.BigInteger(), nullable=False),
        sa.Column("item_name", sa.String(500), nullable=False),
        sa.Column("reminder_time", sa.Time(), nullable=False),
        sa.Column("days_of_week", postgresql.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("memo", sa.String(500), nullable=True),
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

    # reminders 인덱스
    op.create_index("ix_reminders_device_id", "reminders", ["device_id"])
    op.create_index(
        "ix_reminders_device_active",
        "reminders",
        ["device_id", "is_active"],
    )


def downgrade() -> None:
    """모든 테이블 및 인덱스를 삭제한다."""

    # reminders
    op.drop_index("ix_reminders_device_active", table_name="reminders")
    op.drop_index("ix_reminders_device_id", table_name="reminders")
    op.drop_table("reminders")

    # user_cabinets
    op.drop_index("ix_user_cabinets_device_item", table_name="user_cabinets")
    op.drop_index("ix_user_cabinets_device_id", table_name="user_cabinets")
    op.drop_table("user_cabinets")

    # interactions
    op.drop_index("ix_interactions_severity", table_name="interactions")
    op.drop_index("ix_interactions_item_b", table_name="interactions")
    op.drop_index("ix_interactions_item_a", table_name="interactions")
    op.drop_index("ix_interactions_pair", table_name="interactions")
    op.drop_table("interactions")

    # supplements
    op.drop_index("ix_supplements_ingredients_gin", table_name="supplements")
    op.drop_index("ix_supplements_product_name", table_name="supplements")
    op.drop_table("supplements")

    # drugs
    op.drop_index("ix_drugs_ingredients_gin", table_name="drugs")
    op.drop_index("ix_drugs_item_name", table_name="drugs")
    op.drop_index("ix_drugs_item_seq", table_name="drugs")
    op.drop_table("drugs")

    # Enum 타입 삭제
    op.execute("DROP TYPE IF EXISTS cabinetitemtype")
    op.execute("DROP TYPE IF EXISTS severity")
    op.execute("DROP TYPE IF EXISTS itemtype")
