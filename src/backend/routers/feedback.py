"""피드백 라우터 — 베타 사용자 피드백 수집."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.schemas.common import ApiResponse
from src.backend.schemas.feedback import FeedbackCreate, FeedbackResponse
from src.backend.services import feedback_service
from src.backend.utils.response import success_response

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _get_device_id(request: Request) -> str:
    """요청에서 device_id를 안전하게 추출한다."""
    device_id = getattr(request.state, "device_id", None)
    if not device_id:
        raise HTTPException(status_code=401, detail="Device ID is required")
    return device_id


@router.post(
    "",
    response_model=ApiResponse[FeedbackResponse],
    summary="피드백 제출",
    description="베타 사용자 피드백을 제출합니다.",
)
async def submit_feedback(
    data: FeedbackCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """피드백 제출 엔드포인트.

    Args:
        data: 피드백 내용 (category, content, app_version, os_info).
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse[FeedbackResponse] 포맷의 dict.
    """
    device_id = _get_device_id(request)
    result = await feedback_service.create_feedback(db, device_id, data)
    return success_response(result)
