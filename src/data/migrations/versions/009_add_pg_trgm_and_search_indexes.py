"""pg_trgm 확장 활성화 및 검색 성능 인덱스 추가.

Revision ID: 009
Revises: 008
Create Date: 2026-03-14

pg_trgm 확장을 활성화하고, 주요 검색 컬럼에 GIN trigram 인덱스를 추가하여
ILIKE 검색 성능을 대폭 개선하고 유사도(similarity) 기반 퍼지 매칭을 지원한다.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """pg_trgm 확장 활성화 + trigram GIN 인덱스 추가."""

    # --- 1) pg_trgm 확장 활성화 ---
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # --- 2) drugs 검색 인덱스 ---
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_drugs_item_name_trgm "
        "ON drugs USING gin (item_name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_drugs_material_name_trgm "
        "ON drugs USING gin (material_name gin_trgm_ops)"
    )

    # --- 3) supplements 검색 인덱스 ---
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_supplements_product_name_trgm "
        "ON supplements USING gin (product_name gin_trgm_ops)"
    )

    # --- 4) foods 검색 인덱스 ---
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_foods_name_trgm "
        "ON foods USING gin (name gin_trgm_ops)"
    )

    # --- 5) herbal_medicines 검색 인덱스 ---
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_herbal_medicines_name_trgm "
        "ON herbal_medicines USING gin (name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_herbal_medicines_korean_name_trgm "
        "ON herbal_medicines USING gin (korean_name gin_trgm_ops)"
    )


def downgrade() -> None:
    """trigram 인덱스 삭제. pg_trgm 확장은 다른 기능에서도 사용될 수 있으므로 유지."""
    op.execute("DROP INDEX IF EXISTS ix_herbal_medicines_korean_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_herbal_medicines_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_foods_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_supplements_product_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_drugs_material_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_drugs_item_name_trgm")
