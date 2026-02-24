"""리마인더 서비스 단위 테스트."""

from datetime import datetime, time, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.conftest import mock_cabinet_item, mock_reminder, TEST_DEVICE_ID
from src.backend.services.reminder_service import (
    create_reminder,
    list_reminders,
    update_reminder,
    delete_reminder,
)
from src.backend.schemas.reminder import ReminderCreate, ReminderUpdate


# ---------------------------------------------------------------------------
# create_reminder
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_reminder_success():
    """복약함 아이템이 존재하면 리마인더를 성공적으로 생성한다."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    cabinet_item = mock_cabinet_item()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = cabinet_item
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def fake_refresh(obj):
        """mock refresh — ORM 객체에 DB 반환값을 시뮬레이션한다."""
        obj.id = 1
        obj.device_id = TEST_DEVICE_ID
        obj.cabinet_item_id = 1
        obj.item_name = "타이레놀정500밀리그램"
        obj.reminder_time = time(9, 0)
        obj.days_of_week = [0, 1, 2, 3, 4]
        obj.is_active = True
        obj.memo = "아침 식후"
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = fake_refresh

    data = ReminderCreate(
        cabinet_item_id=1,
        reminder_time=time(9, 0),
        days_of_week=[0, 1, 2, 3, 4],
        memo="아침 식후",
    )
    result = await create_reminder(mock_db, TEST_DEVICE_ID, data)

    assert result is not None
    assert result["cabinet_item_id"] == 1
    assert result["item_name"] == "타이레놀정500밀리그램"
    assert result["is_active"] is True
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_create_reminder_cabinet_not_found():
    """복약함 아이템이 존재하지 않으면 None을 반환한다."""
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    data = ReminderCreate(
        cabinet_item_id=9999,
        reminder_time=time(9, 0),
        days_of_week=[0, 1, 2, 3, 4],
    )
    result = await create_reminder(mock_db, TEST_DEVICE_ID, data)

    assert result is None
    mock_db.add.assert_not_called()


# ---------------------------------------------------------------------------
# list_reminders
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_reminders():
    """리마인더가 있으면 목록을 반환한다."""
    mock_db = AsyncMock()

    reminder1 = mock_reminder()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [reminder1]
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await list_reminders(mock_db, TEST_DEVICE_ID)

    assert len(result) == 1
    assert result[0]["item_name"] == "타이레놀정500밀리그램"
    assert result[0]["reminder_time"] == time(9, 0)


@pytest.mark.asyncio
async def test_list_reminders_empty():
    """리마인더가 없으면 빈 리스트를 반환한다."""
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await list_reminders(mock_db, TEST_DEVICE_ID)

    assert result == []


# ---------------------------------------------------------------------------
# update_reminder
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_reminder_success():
    """리마인더가 존재하면 부분 업데이트 후 결과를 반환한다."""
    mock_db = AsyncMock()

    reminder = mock_reminder()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = reminder
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def fake_refresh(obj):
        """mock refresh — 업데이트된 값을 반영한다."""
        obj.id = 1
        obj.device_id = TEST_DEVICE_ID
        obj.cabinet_item_id = 1
        obj.item_name = "타이레놀정500밀리그램"
        obj.reminder_time = time(10, 0)
        obj.days_of_week = [0, 1, 2, 3, 4]
        obj.is_active = True
        obj.memo = "변경됨"
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = fake_refresh

    data = ReminderUpdate(reminder_time=time(10, 0), memo="변경됨")
    result = await update_reminder(mock_db, TEST_DEVICE_ID, reminder_id=1, data=data)

    assert result is not None
    assert result["reminder_time"] == time(10, 0)
    assert result["memo"] == "변경됨"
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_update_reminder_not_found():
    """리마인더가 존재하지 않으면 None을 반환한다."""
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    data = ReminderUpdate(memo="테스트")
    result = await update_reminder(mock_db, TEST_DEVICE_ID, reminder_id=9999, data=data)

    assert result is None


# ---------------------------------------------------------------------------
# delete_reminder
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_reminder_success():
    """리마인더가 존재하면 삭제 후 True를 반환한다."""
    mock_db = AsyncMock()

    reminder = mock_reminder()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = reminder
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await delete_reminder(mock_db, TEST_DEVICE_ID, reminder_id=1)

    assert result is True
    mock_db.delete.assert_called_once_with(reminder)
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_delete_reminder_not_found():
    """리마인더가 존재하지 않으면 None을 반환한다."""
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await delete_reminder(mock_db, TEST_DEVICE_ID, reminder_id=9999)

    assert result is None
    mock_db.delete.assert_not_called()
