"""복약함 라우터 — 사용자 약/영양제 보관함 관리."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.schemas.cabinet import CabinetItemCreate, CabinetItemResponse
from src.backend.schemas.common import ApiResponse
from src.backend.services import cabinet_service
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/cabinet", tags=["cabinet"])


def _get_device_id(request: Request) -> str:
    """요청에서 device_id를 안전하게 추출한다."""
    device_id = getattr(request.state, "device_id", None)
    if not device_id:
        raise HTTPException(status_code=401, detail="Device ID is required")
    return device_id


@router.post(
    "",
    response_model=ApiResponse[CabinetItemResponse],
    summary="복약함 아이템 추가",
    description="복약함에 약물 또는 영양제를 추가합니다.",
)
async def add_cabinet_item(
    data: CabinetItemCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """복약함 아이템 추가 엔드포인트.

    Args:
        data: 추가할 아이템 정보 (item_type, item_id, nickname).
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse[CabinetItemResponse] 포맷의 dict.
    """
    device_id = _get_device_id(request)
    result = await cabinet_service.add_item(db, device_id, data)

    if result is None:
        return error_response("해당 약물/영양제를 찾을 수 없습니다.", 404)
    if result == "duplicate":
        return error_response("이미 복약함에 등록된 아이템입니다.", 409)

    return success_response(result)


@router.get(
    "",
    response_model=ApiResponse[list[CabinetItemResponse]],
    summary="복약함 목록 조회",
    description="사용자의 복약함 아이템 목록을 조회합니다.",
)
async def list_cabinet_items(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """복약함 목록 조회 엔드포인트.

    Args:
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse[list[CabinetItemResponse]] 포맷의 dict.
    """
    device_id = _get_device_id(request)
    items = await cabinet_service.list_items(db, device_id)
    return success_response(items)


@router.delete(
    "/{item_id}",
    response_model=ApiResponse[dict],
    summary="복약함 아이템 삭제",
    description="복약함에서 아이템을 삭제합니다.",
)
async def delete_cabinet_item(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """복약함 아이템 삭제 엔드포인트.

    Args:
        item_id: 삭제할 복약함 아이템의 내부 ID.
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse 포맷의 dict 또는 404 에러.
    """
    device_id = _get_device_id(request)
    result = await cabinet_service.delete_item(db, device_id, item_id)

    if result is None:
        return error_response("복약함 아이템을 찾을 수 없습니다.", 404)

    return success_response({"message": "복약함 아이템이 삭제되었습니다."})
