"""리뷰 서비스 — 약물/영양제 리뷰 CRUD 비즈니스 로직."""

import math

from redis.asyncio import Redis
from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.drug_review import DrugReview
from src.backend.schemas.review import ReviewCreate, ReviewResponse, ReviewSummary
from src.backend.utils.cache import cache_get, cache_set, make_cache_key

# 캐시 TTL (초)
CACHE_TTL_REVIEW_SUMMARY = 60 * 60  # 1시간
CACHE_TTL_REVIEW_LIST = 60 * 10  # 10분


def _summary_cache_key(item_type: str, item_id: int) -> str:
    """리뷰 요약 캐시 키를 생성한다."""
    return make_cache_key("review", "summary", item_type, str(item_id))


def _list_cache_key(item_type: str, item_id: int, page: int, page_size: int) -> str:
    """리뷰 목록 캐시 키를 생성한다."""
    return make_cache_key("review", "list", item_type, str(item_id), str(page), str(page_size))


async def _invalidate_review_cache(
    redis: Redis,
    item_type: str,
    item_id: int,
) -> None:
    """리뷰 관련 캐시를 무효화한다."""
    summary_key = _summary_cache_key(item_type, item_id)
    try:
        await redis.delete(summary_key)
        # 목록 캐시는 패턴 삭제 (첫 페이지만)
        list_key = _list_cache_key(item_type, item_id, 1, 10)
        await redis.delete(list_key)
    except Exception:
        pass


async def create_review(
    db: AsyncSession,
    redis: Redis,
    device_id: str,
    item_type: str,
    item_id: int,
    data: ReviewCreate,
) -> dict:
    """리뷰를 생성하거나 기존 리뷰를 업데이트한다 (upsert).

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        device_id: 디바이스 식별자.
        item_type: 'drug' 또는 'supplement'.
        item_id: 약물/영양제 ID.
        data: 리뷰 생성 데이터.

    Returns:
        ReviewResponse 구조의 dict.
    """
    stmt = pg_insert(DrugReview).values(
        device_id=device_id,
        item_type=item_type,
        item_id=item_id,
        rating=data.rating,
        effectiveness=data.effectiveness,
        ease_of_use=data.ease_of_use,
        comment=data.comment,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_review_device_item",
        set_={
            "rating": data.rating,
            "effectiveness": data.effectiveness,
            "ease_of_use": data.ease_of_use,
            "comment": data.comment,
            "updated_at": func.now(),
        },
    )
    stmt = stmt.returning(DrugReview)
    result = await db.execute(stmt)
    await db.commit()
    review = result.scalar_one()

    await _invalidate_review_cache(redis, item_type, item_id)
    return ReviewResponse.model_validate(review).model_dump()


async def get_reviews(
    db: AsyncSession,
    redis: Redis,
    item_type: str,
    item_id: int,
    page: int,
    page_size: int,
) -> dict:
    """약물/영양제의 리뷰 목록을 페이지네이션으로 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        item_type: 'drug' 또는 'supplement'.
        item_id: 약물/영양제 ID.
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict.
    """
    cache_key = _list_cache_key(item_type, item_id, page, page_size)
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    condition = (DrugReview.item_type == item_type) & (DrugReview.item_id == item_id)

    count_stmt = select(func.count()).select_from(DrugReview).where(condition)
    total: int = (await db.execute(count_stmt)).scalar_one()

    offset = (page - 1) * page_size
    query_stmt = (
        select(DrugReview)
        .where(condition)
        .order_by(DrugReview.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = await db.execute(query_stmt)
    reviews = rows.scalars().all()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    items = [ReviewResponse.model_validate(r).model_dump() for r in reviews]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    await cache_set(redis, cache_key, result, CACHE_TTL_REVIEW_LIST)
    return result


async def get_review_summary(
    db: AsyncSession,
    redis: Redis,
    item_type: str,
    item_id: int,
) -> dict:
    """약물/영양제의 리뷰 요약 통계를 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        item_type: 'drug' 또는 'supplement'.
        item_id: 약물/영양제 ID.

    Returns:
        ReviewSummary 구조의 dict.
    """
    cache_key = _summary_cache_key(item_type, item_id)
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    condition = (DrugReview.item_type == item_type) & (DrugReview.item_id == item_id)

    # 평균/총 건수
    agg_stmt = select(
        func.coalesce(func.avg(DrugReview.rating), 0),
        func.count(),
    ).where(condition)
    agg_row = (await db.execute(agg_stmt)).one()
    avg_rating = round(float(agg_row[0]), 1)
    total_count = int(agg_row[1])

    # 분포 (1~5별 건수)
    dist_stmt = (
        select(DrugReview.rating, func.count())
        .where(condition)
        .group_by(DrugReview.rating)
    )
    dist_rows = (await db.execute(dist_stmt)).all()
    distribution = {str(i): 0 for i in range(1, 6)}
    for rating_val, cnt in dist_rows:
        distribution[str(rating_val)] = cnt

    result = ReviewSummary(
        average_rating=avg_rating,
        total_count=total_count,
        distribution=distribution,
    ).model_dump()

    await cache_set(redis, cache_key, result, CACHE_TTL_REVIEW_SUMMARY)
    return result


async def mark_helpful(
    db: AsyncSession,
    redis: Redis,
    review_id: int,
) -> dict | None:
    """리뷰의 도움됨 카운트를 증가시킨다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        review_id: 리뷰 ID.

    Returns:
        업데이트된 ReviewResponse dict 또는 None.
    """
    stmt = (
        update(DrugReview)
        .where(DrugReview.id == review_id)
        .values(helpful_count=DrugReview.helpful_count + 1)
        .returning(DrugReview)
    )
    result = await db.execute(stmt)
    await db.commit()
    review = result.scalar_one_or_none()

    if review is None:
        return None

    await _invalidate_review_cache(redis, review.item_type, review.item_id)
    return ReviewResponse.model_validate(review).model_dump()


async def delete_review(
    db: AsyncSession,
    redis: Redis,
    device_id: str,
    review_id: int,
) -> bool:
    """자신의 리뷰를 삭제한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        device_id: 디바이스 식별자.
        review_id: 리뷰 ID.

    Returns:
        삭제 성공 여부.
    """
    # 먼저 리뷰 정보 조회 (캐시 무효화용)
    select_stmt = select(DrugReview).where(
        (DrugReview.id == review_id) & (DrugReview.device_id == device_id)
    )
    row = await db.execute(select_stmt)
    review = row.scalar_one_or_none()

    if review is None:
        return False

    item_type = review.item_type
    item_id = review.item_id

    del_stmt = delete(DrugReview).where(
        (DrugReview.id == review_id) & (DrugReview.device_id == device_id)
    )
    result = await db.execute(del_stmt)
    await db.commit()

    if result.rowcount > 0:
        await _invalidate_review_cache(redis, item_type, item_id)
        return True
    return False
