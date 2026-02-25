"""상호작용(Interaction) 모델 — 약물/영양제 간 상호작용 정보."""

import enum

from sqlalchemy import BigInteger, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class ItemType(str, enum.Enum):
    """상호작용 대상 아이템 유형."""

    DRUG = "drug"
    SUPPLEMENT = "supplement"


class Severity(str, enum.Enum):
    """상호작용 심각도.

    - danger: DUR 병용금기 (공식 금기)
    - warning: 주의 필요
    - caution: 참고 사항
    - info: 정보 제공
    """

    DANGER = "danger"
    WARNING = "warning"
    CAUTION = "caution"
    INFO = "info"


class Interaction(Base, TimestampMixin):
    """상호작용 정보 테이블.

    Attributes:
        id: 내부 PK
        item_a_type: A 아이템 유형 (drug/supplement)
        item_a_id: A 아이템 참조 ID
        item_a_name: A 아이템명 (비정규화, 조회 성능)
        item_b_type: B 아이템 유형
        item_b_id: B 아이템 참조 ID
        item_b_name: B 아이템명
        severity: 심각도
        description: 상호작용 설명 (원문)
        mechanism: 상호작용 기전
        recommendation: 권장 조치
        source: 데이터 출처 (DUR, DrugBank 등)
        source_id: 출처 내 고유 ID
        evidence_level: 근거 수준
    """

    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    item_a_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)
    item_a_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    item_a_name: Mapped[str] = mapped_column(String(500), nullable=False)
    item_b_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)
    item_b_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    item_b_name: Mapped[str] = mapped_column(String(500), nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    mechanism: Mapped[str | None] = mapped_column(Text)
    recommendation: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100))
    evidence_level: Mapped[str | None] = mapped_column(String(50))

    __table_args__ = (
        Index("ix_interactions_pair", "item_a_type", "item_a_id", "item_b_type", "item_b_id"),
        Index("ix_interactions_item_a", "item_a_type", "item_a_id"),
        Index("ix_interactions_item_b", "item_b_type", "item_b_id"),
        Index("ix_interactions_severity", "severity"),
    )

    def __repr__(self) -> str:
        """상호작용 모델의 문자열 표현을 반환한다."""
        return (
            f"<Interaction(id={self.id}, "
            f"{self.item_a_name!r} x {self.item_b_name!r}, "
            f"severity={self.severity.value})>"
        )
