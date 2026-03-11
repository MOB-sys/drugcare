"""음식(Food) 모델 — 약물/영양제와의 상호작용 관리를 위한 식품 정보."""

from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class Food(Base, TimestampMixin):
    """식품 정보 테이블.

    Attributes:
        id: 내부 PK
        name: 식품명
        slug: URL용 슬러그
        category: 분류 (과일, 채소, 유제품, 음료, 곡류, 조미료 등)
        description: 설명
        common_names: 대체 이름 목록 JSONB ["자몽", "그레이프프루트"]
        nutrients: 주요 영양 정보 JSONB {"vitamin_c": "53mg", ...}
        image_url: 이미지 URL
    """

    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    common_names: Mapped[list | None] = mapped_column(JSONB, default=list)
    nutrients: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    image_url: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        Index("ix_foods_name", "name"),
        Index("ix_foods_common_names_gin", "common_names", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """식품 모델의 문자열 표현을 반환한다."""
        return f"<Food(id={self.id}, name={self.name!r})>"
