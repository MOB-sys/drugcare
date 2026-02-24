"""의약품(Drug) 모델 — 식약처 e약은요/허가정보 기반."""

from sqlalchemy import BigInteger, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class Drug(Base, TimestampMixin):
    """의약품 정보 테이블.

    Attributes:
        id: 내부 PK
        item_seq: 식약처 품목기준코드 (고유)
        item_name: 제품명
        entp_name: 업체명
        etc_otc_code: 전문/일반 구분
        class_no: 약효분류번호
        chart: 성상
        bar_code: 표준코드
        material_name: 원료성분 (원문 텍스트)
        ingredients: 성분 구조화 JSONB [{"name": ..., "amount": ..., "unit": ...}]
        efcy_qesitm: 효능효과
        use_method_qesitm: 용법용량
        atpn_warn_qesitm: 주의사항 경고
        atpn_qesitm: 주의사항
        intrc_qesitm: 상호작용
        se_qesitm: 부작용
        deposit_method_qesitm: 보관방법
        item_image: 제품 이미지 URL
    """

    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_seq: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(500), nullable=False)
    entp_name: Mapped[str | None] = mapped_column(String(200))
    etc_otc_code: Mapped[str | None] = mapped_column(String(20))
    class_no: Mapped[str | None] = mapped_column(String(10))
    chart: Mapped[str | None] = mapped_column(Text)
    bar_code: Mapped[str | None] = mapped_column(String(50))
    material_name: Mapped[str | None] = mapped_column(Text)
    ingredients: Mapped[dict | None] = mapped_column(JSONB, default=list)
    efcy_qesitm: Mapped[str | None] = mapped_column(Text)
    use_method_qesitm: Mapped[str | None] = mapped_column(Text)
    atpn_warn_qesitm: Mapped[str | None] = mapped_column(Text)
    atpn_qesitm: Mapped[str | None] = mapped_column(Text)
    intrc_qesitm: Mapped[str | None] = mapped_column(Text)
    se_qesitm: Mapped[str | None] = mapped_column(Text)
    deposit_method_qesitm: Mapped[str | None] = mapped_column(Text)
    item_image: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        Index("ix_drugs_item_name", "item_name"),
        Index("ix_drugs_ingredients_gin", "ingredients", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Drug(id={self.id}, item_seq={self.item_seq}, name={self.item_name!r})>"
