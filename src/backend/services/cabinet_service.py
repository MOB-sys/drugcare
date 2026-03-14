"""복약함 서비스 — 사용자 약/영양제 보관함 관리."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.drug import Drug
from src.backend.models.food import Food
from src.backend.models.herbal_medicine import HerbalMedicine
from src.backend.models.supplement import Supplement
from src.backend.models.user_cabinet import CabinetItemType, UserCabinet
from src.backend.schemas.cabinet import CabinetItemCreate, CabinetItemResponse


async def add_item(
    db: AsyncSession,
    device_id: str,
    data: CabinetItemCreate,
) -> dict | str | None:
    """복약함에 약/영양제를 추가한다.

    아이템 존재 여부를 확인한 후 복약함에 등록한다.
    중복 등록 시 "duplicate" 문자열을 반환하여 호출자가 409 처리하도록 한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        data: 추가할 아이템 정보.

    Returns:
        CabinetItemResponse dict, "duplicate" 문자열, 또는 None (아이템 미존재).
    """
    item_name = await _resolve_item_name(db, data.item_type, data.item_id)
    if item_name is None:
        return None

    cabinet_item = UserCabinet(
        device_id=device_id,
        item_type=data.item_type,
        item_id=data.item_id,
        item_name=item_name,
        nickname=data.nickname,
    )
    db.add(cabinet_item)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        return "duplicate"

    await db.refresh(cabinet_item)
    return CabinetItemResponse.model_validate(cabinet_item).model_dump()


async def list_items(db: AsyncSession, device_id: str) -> list[dict]:
    """사용자의 복약함 목록을 조회한다.

    최근 추가순으로 정렬하여 반환한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.

    Returns:
        CabinetItemResponse dict 리스트.
    """
    stmt = (
        select(UserCabinet)
        .where(UserCabinet.device_id == device_id)
        .order_by(UserCabinet.created_at.desc())
    )
    rows = await db.execute(stmt)
    items = rows.scalars().all()
    return [CabinetItemResponse.model_validate(item).model_dump() for item in items]


async def delete_item(
    db: AsyncSession,
    device_id: str,
    item_id: int,
) -> bool | None:
    """복약함에서 아이템을 삭제한다.

    소유권(device_id) 검증 후 삭제한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 UUID.
        item_id: 삭제할 복약함 아이템 PK.

    Returns:
        True (삭제 성공) 또는 None (아이템 미존재/소유권 불일치).
    """
    stmt = select(UserCabinet).where(
        UserCabinet.id == item_id,
        UserCabinet.device_id == device_id,
    )
    row = await db.execute(stmt)
    item = row.scalar_one_or_none()

    if item is None:
        return None

    await db.delete(item)
    await db.flush()
    return True


async def _resolve_item_name(
    db: AsyncSession,
    item_type: CabinetItemType,
    item_id: int,
) -> str | None:
    """아이템 유형과 ID로 이름을 조회한다.

    해당 item_type에 맞는 테이블에서 이름 컬럼만 SELECT하여
    불필요한 전체 행 로딩을 방지한다.

    Args:
        db: 비동기 DB 세션.
        item_type: 아이템 유형 (drug/supplement/food/herbal).
        item_id: 아이템 PK.

    Returns:
        아이템명 또는 None (존재하지 않는 경우).
    """
    # item_type → (모델, 이름 컬럼) 매핑 — 해당 타입만 1회 쿼리
    type_map = {
        CabinetItemType.DRUG: (Drug, Drug.item_name),
        CabinetItemType.SUPPLEMENT: (Supplement, Supplement.product_name),
        CabinetItemType.FOOD: (Food, Food.name),
        CabinetItemType.HERBAL: (HerbalMedicine, HerbalMedicine.name),
    }

    mapping = type_map.get(item_type)
    if mapping is None:
        return None

    model, name_col = mapping
    stmt = select(name_col).where(model.id == item_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
