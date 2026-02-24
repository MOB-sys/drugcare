"""복약함 서비스 단위 테스트."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from tests.conftest import mock_drug, mock_supplement, mock_cabinet_item, TEST_DEVICE_ID
from src.backend.services.cabinet_service import add_item, list_items, delete_item
from src.backend.schemas.cabinet import CabinetItemCreate
from src.backend.models.user_cabinet import CabinetItemType


# ---------------------------------------------------------------------------
# add_item
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_item_drug_success():
    """의약품을 복약함에 성공적으로 추가한다."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    drug = mock_drug()
    mock_drug_result = MagicMock()
    mock_drug_result.scalar_one_or_none.return_value = drug
    mock_db.execute = AsyncMock(return_value=mock_drug_result)

    # flush 후 refresh에서 속성을 설정한다
    async def fake_refresh(obj):
        """mock refresh — ORM 객체에 DB 반환값을 시뮬레이션한다."""
        obj.id = 1
        obj.device_id = TEST_DEVICE_ID
        obj.item_type = CabinetItemType.DRUG
        obj.item_id = 1
        obj.item_name = "타이레놀정500밀리그램"
        obj.nickname = None
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = fake_refresh

    data = CabinetItemCreate(item_type=CabinetItemType.DRUG, item_id=1)
    result = await add_item(mock_db, TEST_DEVICE_ID, data)

    assert result is not None
    assert result != "duplicate"
    assert result["item_name"] == "타이레놀정500밀리그램"
    assert result["device_id"] == TEST_DEVICE_ID
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_add_item_supplement_success():
    """영양제를 복약함에 성공적으로 추가한다."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    supp = mock_supplement()
    mock_supp_result = MagicMock()
    mock_supp_result.scalar_one_or_none.return_value = supp
    mock_db.execute = AsyncMock(return_value=mock_supp_result)

    async def fake_refresh(obj):
        """mock refresh — ORM 객체에 DB 반환값을 시뮬레이션한다."""
        obj.id = 2
        obj.device_id = TEST_DEVICE_ID
        obj.item_type = CabinetItemType.SUPPLEMENT
        obj.item_id = 1
        obj.item_name = "종근당 비타민C 1000"
        obj.nickname = None
        obj.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = fake_refresh

    data = CabinetItemCreate(item_type=CabinetItemType.SUPPLEMENT, item_id=1)
    result = await add_item(mock_db, TEST_DEVICE_ID, data)

    assert result is not None
    assert result != "duplicate"
    assert result["item_name"] == "종근당 비타민C 1000"


@pytest.mark.asyncio
async def test_add_item_not_found():
    """존재하지 않는 아이템 추가 시 None을 반환한다."""
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    data = CabinetItemCreate(item_type=CabinetItemType.DRUG, item_id=9999)
    result = await add_item(mock_db, TEST_DEVICE_ID, data)

    assert result is None
    mock_db.add.assert_not_called()


@pytest.mark.asyncio
async def test_add_item_duplicate():
    """중복 아이템 추가 시 'duplicate' 문자열을 반환한다."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    drug = mock_drug()
    mock_drug_result = MagicMock()
    mock_drug_result.scalar_one_or_none.return_value = drug
    mock_db.execute = AsyncMock(return_value=mock_drug_result)

    mock_db.flush = AsyncMock(
        side_effect=IntegrityError("duplicate key", {}, Exception()),
    )

    data = CabinetItemCreate(item_type=CabinetItemType.DRUG, item_id=1)
    result = await add_item(mock_db, TEST_DEVICE_ID, data)

    assert result == "duplicate"
    mock_db.rollback.assert_called_once()


# ---------------------------------------------------------------------------
# list_items
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_items():
    """복약함에 아이템이 있으면 목록을 반환한다."""
    mock_db = AsyncMock()

    item1 = mock_cabinet_item()
    item2 = mock_cabinet_item(
        id=2,
        item_type="supplement",
        item_id=1,
        item_name="종근당 비타민C 1000",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [item1, item2]
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await list_items(mock_db, TEST_DEVICE_ID)

    assert len(result) == 2
    assert result[0]["item_name"] == "타이레놀정500밀리그램"
    assert result[1]["item_name"] == "종근당 비타민C 1000"


@pytest.mark.asyncio
async def test_list_items_empty():
    """복약함이 비어 있으면 빈 리스트를 반환한다."""
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await list_items(mock_db, TEST_DEVICE_ID)

    assert result == []


# ---------------------------------------------------------------------------
# delete_item
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_item_success():
    """존재하는 복약함 아이템 삭제 시 True를 반환한다."""
    mock_db = AsyncMock()

    item = mock_cabinet_item()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = item
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await delete_item(mock_db, TEST_DEVICE_ID, item_id=1)

    assert result is True
    mock_db.delete.assert_called_once_with(item)
    mock_db.flush.assert_called_once()


@pytest.mark.asyncio
async def test_delete_item_not_found():
    """존재하지 않는 복약함 아이템 삭제 시 None을 반환한다."""
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await delete_item(mock_db, TEST_DEVICE_ID, item_id=9999)

    assert result is None
    mock_db.delete.assert_not_called()
