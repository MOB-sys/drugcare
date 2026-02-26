"""영양제(Supplement) 모델 — 건강기능식품 정보."""

from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class Supplement(Base, TimestampMixin):
    """건강기능식품(영양제) 정보 테이블.

    Attributes:
        id: 내부 PK
        product_name: 제품명
        company: 제조사/판매사
        registration_no: 인허가번호
        main_ingredient: 주성분명
        ingredients: 성분 구조화 JSONB [{"name": ..., "amount": ..., "unit": ...}]
        functionality: 기능성 내용
        precautions: 섭취 시 주의사항
        intake_method: 섭취방법
        category: 분류 (비타민, 미네랄, 프로바이오틱스 등)
        source: 데이터 출처 (자체 구축/식약처)
    """

    __tablename__ = "supplements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    company: Mapped[str | None] = mapped_column(String(200))
    registration_no: Mapped[str | None] = mapped_column(String(50), unique=True)
    main_ingredient: Mapped[str | None] = mapped_column(String(200))
    ingredients: Mapped[dict | None] = mapped_column(JSONB, default=list)
    functionality: Mapped[str | None] = mapped_column(Text)
    precautions: Mapped[str | None] = mapped_column(Text)
    intake_method: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    source: Mapped[str | None] = mapped_column(String(100))

    __table_args__ = (
        Index("ix_supplements_product_name", "product_name"),
        Index("ix_supplements_ingredients_gin", "ingredients", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """영양제 모델의 문자열 표현을 반환한다."""
        return f"<Supplement(id={self.id}, name={self.product_name!r})>"
