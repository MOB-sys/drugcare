"""DUR 안전성 정보 모델 — 임부금기/노인주의/용량주의/투여기간주의/효능군중복."""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class DrugDURInfo(Base, TimestampMixin):
    """DUR 안전성 정보 테이블.

    Attributes:
        id: 내부 PK
        item_seq: 약물 품목기준코드 (drugs.item_seq 참조)
        dur_type: DUR 유형 (pregnancy/elderly/dosage/duration/efficacy_dup)
        type_name: 한글 유형명
        ingr_code: 성분 코드
        ingr_name: 성분명
        ingr_eng_name: 영문 성분명
        prohibition_content: 금기/주의 내용
        remark: 비고
        notification_date: 고시일자
        source_id: 유니크 식별자
    """

    __tablename__ = "drug_dur_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_seq: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    dur_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    type_name: Mapped[str | None] = mapped_column(String(50))
    ingr_code: Mapped[str | None] = mapped_column(String(20))
    ingr_name: Mapped[str | None] = mapped_column(String(200))
    ingr_eng_name: Mapped[str | None] = mapped_column(String(200))
    prohibition_content: Mapped[str | None] = mapped_column(Text)
    remark: Mapped[str | None] = mapped_column(Text)
    notification_date: Mapped[str | None] = mapped_column(String(8))
    source_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
