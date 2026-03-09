"""약물/영양제 리뷰(DrugReview) 모델."""

from sqlalchemy import BigInteger, Index, Integer, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class DrugReview(Base, TimestampMixin):
    """약물/영양제 리뷰 테이블.

    Attributes:
        id: 내부 PK
        device_id: 디바이스 식별자
        item_type: 'drug' 또는 'supplement'
        item_id: 약물/영양제 ID
        rating: 전체 평점 (1-5)
        effectiveness: 효과 평점 (1-5, 선택)
        ease_of_use: 복용 편의성 평점 (1-5, 선택)
        comment: 리뷰 코멘트 (선택, 최대 500자)
        helpful_count: 도움됨 카운트
    """

    __tablename__ = "drug_reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    item_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    effectiveness: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ease_of_use: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    helpful_count: Mapped[int] = mapped_column(Integer, server_default="0")

    __table_args__ = (
        UniqueConstraint("device_id", "item_type", "item_id", name="uq_review_device_item"),
        Index("ix_drug_reviews_item", "item_type", "item_id"),
    )

    def __repr__(self) -> str:
        """리뷰 모델의 문자열 표현을 반환한다."""
        return f"<DrugReview(id={self.id}, item_type={self.item_type}, rating={self.rating})>"
