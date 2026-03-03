"""피드백 서비스 — 베타 사용자 피드백 수집."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.feedback import Feedback
from src.backend.schemas.feedback import FeedbackCreate

logger = logging.getLogger(__name__)


async def create_feedback(db: AsyncSession, device_id: str, data: FeedbackCreate) -> dict:
    """피드백을 생성하고 저장한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 식별자.
        data: 피드백 생성 데이터.

    Returns:
        생성된 피드백 정보 dict.
    """
    feedback = Feedback(
        device_id=device_id,
        category=data.category,
        content=data.content,
        app_version=data.app_version,
        os_info=data.os_info,
    )
    db.add(feedback)
    await db.flush()
    await db.refresh(feedback)

    logger.info(
        "피드백 생성 — id=%d, device=%s, category=%s",
        feedback.id,
        device_id,
        data.category,
    )

    from src.backend.schemas.feedback import FeedbackResponse

    return FeedbackResponse.model_validate(feedback).model_dump()
