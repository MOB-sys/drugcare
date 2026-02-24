"""상호작용 체크 라우터 — 약물/영양제 상호작용 확인 (스텁)."""

from fastapi import APIRouter

from src.backend.schemas.common import ApiResponse
from src.backend.schemas.interaction import (
    InteractionCheckRequest,
    InteractionCheckResponse,
)
from src.backend.utils.response import success_response

router = APIRouter(prefix="/interactions", tags=["interactions"])

DISCLAIMER = "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다."


@router.post(
    "/check",
    response_model=ApiResponse[InteractionCheckResponse],
    summary="상호작용 체크",
    description="2개 이상의 약물/영양제 간 상호작용을 확인합니다.",
)
async def check_interactions(
    request: InteractionCheckRequest,
) -> dict:
    """상호작용 체크 엔드포인트 (스텁).

    Phase 2에서 실제 상호작용 엔진 연동으로 구현 예정.
    요청된 아이템 쌍 수를 계산하여 빈 결과를 반환한다.

    Args:
        request: 상호작용 체크 요청 (최소 2개 아이템 필수).

    Returns:
        ApiResponse[InteractionCheckResponse] 포맷의 dict.
    """
    # 아이템 쌍 수 계산: nC2 = n*(n-1)/2
    item_count = len(request.items)
    total_pairs = item_count * (item_count - 1) // 2

    response_data = InteractionCheckResponse(
        total_checked=total_pairs,
        interactions_found=0,
        has_danger=False,
        results=[],
        disclaimer=DISCLAIMER,
    )

    return success_response(response_data.model_dump())
