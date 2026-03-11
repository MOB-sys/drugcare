"""한약재(HerbalMedicine) 모델 — 전통 한약재 및 생약 정보."""

from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class HerbalMedicine(Base, TimestampMixin):
    """한약재 정보 테이블.

    Attributes:
        id: 내부 PK
        name: 대표 이름 (한글)
        slug: URL용 슬러그
        korean_name: 한글명
        latin_name: 학명
        category: 분류 (보기약, 보혈약, 해표약 등)
        properties: 성질 JSONB {"taste": "쓴맛", "nature": "한성", "meridian": ["간", "담"]}
        description: 설명
        efficacy: 효능
        precautions: 주의사항
        image_url: 이미지 URL
    """

    __tablename__ = "herbal_medicines"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    korean_name: Mapped[str | None] = mapped_column(String(200))
    latin_name: Mapped[str | None] = mapped_column(String(300))
    category: Mapped[str | None] = mapped_column(String(100))
    properties: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    description: Mapped[str | None] = mapped_column(Text)
    efficacy: Mapped[str | None] = mapped_column(Text)
    precautions: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        Index("ix_herbal_medicines_name", "name"),
        Index("ix_herbal_medicines_properties_gin", "properties", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """한약재 모델의 문자열 표현을 반환한다."""
        return f"<HerbalMedicine(id={self.id}, name={self.name!r})>"
