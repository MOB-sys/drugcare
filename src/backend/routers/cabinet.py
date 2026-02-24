"""복약함 라우터 — 사용자 약/영양제 보관함 관리 (스텁)."""

from fastapi import APIRouter, Request

from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/cabinet", tags=["cabinet"])


@router.post(
    "",
    response_model=ApiResponse[dict],
    summary="복약함 아이템 추가",
    description="복약함에 약물 또는 영양제를 추가합니다.",
)
async def add_cabinet_item(
    request: Request,
) -> dict:
    """복약함 아이템 추가 엔드포인트 (스텁).

    Phase 2에서 실제 DB 저장으로 구현 예정.

    Args:
        request: HTTP 요청 (device_id는 request.state에서 추출).

    Returns:
        ApiResponse 포맷의 dict.
    """
    device_id = request.state.device_id
    return success_response({
        "message": "복약함 아이템 추가 구현 예정입니다.",
        "device_id": device_id,
    })


@router.get(
    "",
    response_model=ApiResponse[PaginatedData[dict]],
    summary="복약함 목록 조회",
    description="사용자의 복약함 아이템 목록을 조회합니다.",
)
async def list_cabinet_items(
    request: Request,
) -> dict:
    """복약함 목록 조회 엔드포인트 (스텁).

    request.state.device_id로 사용자를 식별한다.
    Phase 2에서 실제 DB 조회로 구현 예정.

    Args:
        request: HTTP 요청 (device_id는 request.state에서 추출).

    Returns:
        ApiResponse[PaginatedData] 포맷의 dict.
    """
    _device_id = request.state.device_id
    paginated = PaginatedData[dict](
        items=[],
        total=0,
        page=1,
        page_size=20,
        total_pages=0,
    )
    return success_response(paginated.model_dump())


@router.delete(
    "/{item_id}",
    response_model=ApiResponse[dict],
    summary="복약함 아이템 삭제",
    description="복약함에서 아이템을 삭제합니다.",
)
async def delete_cabinet_item(
    item_id: int,
    request: Request,
) -> dict:
    """복약함 아이템 삭제 엔드포인트 (스텁).

    Phase 2에서 실제 DB 삭제로 구현 예정.

    Args:
        item_id: 삭제할 복약함 아이템의 내부 ID.
        request: HTTP 요청 (device_id는 request.state에서 추출).

    Returns:
        404 에러 응답 (구현 예정).
    """
    _device_id = request.state.device_id
    return error_response(
        message=f"복약함 아이템 삭제 구현 예정입니다. (item_id={item_id})",
        status_code=404,
    )
