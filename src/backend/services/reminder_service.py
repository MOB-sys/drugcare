"""리마인더 서비스 — 복약 알림 스케줄 관리."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.reminder import Reminder
from src.backend.models.user_cabinet import UserCabinet
from src.backend.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate


async def create_reminder(
    db: AsyncSession,
    device_id: str,
    data: ReminderCreate,
) -> dict | None:
    """복약 리마인더를 생성한다.

    복약함 아이템 소유권을 확인한 후 리마인더를 등록한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        data: 리마인더 생성 정보.

    Returns:
        ReminderResponse dict 또는 None (복약함 아이템 미존재/소유권 불일치).
    """
    cabinet_item = await _get_cabinet_item(db, device_id, data.cabinet_item_id)
    if cabinet_item is None:
        return None

    reminder = Reminder(
        device_id=device_id,
        cabinet_item_id=data.cabinet_item_id,
        item_name=cabinet_item.item_name,
        reminder_time=data.reminder_time,
        days_of_week=data.days_of_week,
        memo=data.memo,
    )
    db.add(reminder)
    await db.flush()
    await db.refresh(reminder)
    return ReminderResponse.model_validate(reminder).model_dump()


async def list_reminders(
    db: AsyncSession,
    device_id: str,
    active_only: bool = True,
) -> list[dict]:
    """사용자의 리마인더 목록을 조회한다.

    알림 시각 순으로 정렬하여 반환한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        active_only: True이면 활성 리마인더만 조회.

    Returns:
        ReminderResponse dict 리스트.
    """
    stmt = select(Reminder).where(Reminder.device_id == device_id)

    if active_only:
        stmt = stmt.where(Reminder.is_active.is_(True))

    stmt = stmt.order_by(Reminder.reminder_time)
    rows = await db.execute(stmt)
    reminders = rows.scalars().all()
    return [ReminderResponse.model_validate(r).model_dump() for r in reminders]


async def update_reminder(
    db: AsyncSession,
    device_id: str,
    reminder_id: int,
    data: ReminderUpdate,
) -> dict | None:
    """리마인더를 부분 업데이트한다.

    소유권 확인 후 전달된 필드만 갱신한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        reminder_id: 수정할 리마인더 PK.
        data: 수정 정보 (설정된 필드만 반영).

    Returns:
        ReminderResponse dict 또는 None (리마인더 미존재/소유권 불일치).
    """
    reminder = await _get_reminder(db, device_id, reminder_id)
    if reminder is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(reminder, field_name, value)

    await db.flush()
    await db.refresh(reminder)
    return ReminderResponse.model_validate(reminder).model_dump()


async def delete_reminder(
    db: AsyncSession,
    device_id: str,
    reminder_id: int,
) -> bool | None:
    """리마인더를 삭제한다.

    소유권(device_id) 검증 후 삭제한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        reminder_id: 삭제할 리마인더 PK.

    Returns:
        True (삭제 성공) 또는 None (리마인더 미존재/소유권 불일치).
    """
    reminder = await _get_reminder(db, device_id, reminder_id)
    if reminder is None:
        return None

    await db.delete(reminder)
    await db.flush()
    return True


async def _get_cabinet_item(
    db: AsyncSession,
    device_id: str,
    cabinet_item_id: int,
) -> UserCabinet | None:
    """복약함 아이템을 소유권 검증과 함께 조회한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        cabinet_item_id: 복약함 아이템 PK.

    Returns:
        UserCabinet 인스턴스 또는 None.
    """
    stmt = select(UserCabinet).where(
        UserCabinet.id == cabinet_item_id,
        UserCabinet.device_id == device_id,
    )
    row = await db.execute(stmt)
    return row.scalar_one_or_none()


async def _get_reminder(
    db: AsyncSession,
    device_id: str,
    reminder_id: int,
) -> Reminder | None:
    """리마인더를 소유권 검증과 함께 조회한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        reminder_id: 리마인더 PK.

    Returns:
        Reminder 인스턴스 또는 None.
    """
    stmt = select(Reminder).where(
        Reminder.id == reminder_id,
        Reminder.device_id == device_id,
    )
    row = await db.execute(stmt)
    return row.scalar_one_or_none()
