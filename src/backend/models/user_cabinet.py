"""복약함(UserCabinet) 모델 — 사용자의 약/영양제 보관함."""

import enum

from sqlalchemy import BigInteger, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class CabinetItemType(str, enum.Enum):
    """복약함 아이템 유형."""

    DRUG = "drug"
    SUPPLEMENT = "supplement"


class UserCabinet(Base, TimestampMixin):
    """사용자 복약함 테이블.

    Attributes:
        id: 내부 PK
        device_id: 디바이스 UUID (사용자 식별)
        item_type: 아이템 유형 (drug/supplement)
        item_id: 약/영양제 참조 ID
        item_name: 아이템명 (비정규화)
        nickname: 사용자 지정 별칭
    """

    __tablename__ = "user_cabinets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    item_type: Mapped[CabinetItemType] = mapped_column(Enum(CabinetItemType), nullable=False)
    item_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    item_name: Mapped[str] = mapped_column(String(500), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(200))

    __table_args__ = (
        Index("ix_user_cabinets_device_item", "device_id", "item_type", "item_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<UserCabinet(id={self.id}, device={self.device_id}, item={self.item_name!r})>"
