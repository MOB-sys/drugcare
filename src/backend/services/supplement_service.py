"""영양제(Supplement) 서비스 — 검색 및 상세 조회 비즈니스 로직."""

import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.backend.models.supplement import Supplement
from src.backend.schemas.supplement import SupplementDetail, SupplementSearchItem
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key
from src.backend.core.redis import CACHE_TTL_SUPPLEMENT_DETAIL, CACHE_TTL_SUPPLEMENT_SEARCH

# slug/count 캐시 TTL (초)
CACHE_TTL_SUPPLEMENT_SLUGS = 60 * 60 * 24   # 24시간
CACHE_TTL_SUPPLEMENT_COUNT = 60 * 60 * 24   # 24시간


async def search_supplements(
    db: AsyncSession,
    redis: Redis,
    q: str,
    page: int,
    page_size: int,
) -> dict:
    """영양제를 제품명으로 검색한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 ILIKE 검색을 수행한다.
    결과는 PaginatedData[SupplementSearchItem] 호환 dict로 반환된다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (영양제 제품명).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict (items, total, page, page_size, total_pages).
    """
    if not q.strip():
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    cache_key = make_cache_key("supplement", "search", hash_query(q), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    # 검색 조건
    condition = Supplement.product_name.ilike(f"%{q}%")

    # 전체 건수 조회
    count_stmt = select(func.count()).select_from(Supplement).where(condition)
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    # 페이지네이션 조회
    offset = (page - 1) * page_size
    search_stmt = select(Supplement).where(condition).offset(offset).limit(page_size)
    rows = await db.execute(search_stmt)
    supplements = rows.scalars().all()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    items = [SupplementSearchItem.model_validate(s).model_dump() for s in supplements]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

    await cache_set(redis, cache_key, result, CACHE_TTL_SUPPLEMENT_SEARCH)
    return result


async def get_supplement_detail(
    db: AsyncSession,
    redis: Redis,
    supplement_id: int,
) -> dict | None:
    """영양제 상세 정보를 조회한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 PK 조회를 수행한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        supplement_id: 조회할 영양제 ID.

    Returns:
        SupplementDetail 구조의 dict 또는 None (존재하지 않는 경우).
    """
    cache_key = make_cache_key("supplement", "detail", str(supplement_id))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Supplement).where(Supplement.id == supplement_id)
    row = await db.execute(stmt)
    supplement = row.scalar_one_or_none()

    if supplement is None:
        return None

    result = SupplementDetail.model_validate(supplement).model_dump()
    await cache_set(redis, cache_key, result, CACHE_TTL_SUPPLEMENT_DETAIL)
    return result


async def get_supplement_by_slug(
    db: AsyncSession,
    redis: Redis,
    slug: str,
) -> dict | None:
    """slug로 영양제 상세 정보를 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        slug: 영양제 slug (예: supp-1).

    Returns:
        SupplementDetail 구조의 dict 또는 None.
    """
    cache_key = make_cache_key("supplement", "by-slug", slug)
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Supplement).where(Supplement.slug == slug)
    row = await db.execute(stmt)
    supplement = row.scalar_one_or_none()

    if supplement is None:
        return None

    result = SupplementDetail.model_validate(supplement).model_dump()
    await cache_set(redis, cache_key, result, CACHE_TTL_SUPPLEMENT_DETAIL)
    return result


async def get_all_supplement_slugs(
    db: AsyncSession,
    redis: Redis,
) -> list[str]:
    """모든 영양제 slug 목록을 반환한다 (SSG generateStaticParams용).

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        slug 문자열 리스트.
    """
    cache_key = make_cache_key("supplement", "slugs", "all")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Supplement.slug)
    rows = await db.execute(stmt)
    slugs = [row[0] for row in rows.all()]

    await cache_set(redis, cache_key, slugs, CACHE_TTL_SUPPLEMENT_SLUGS)
    return slugs


async def count_supplements(
    db: AsyncSession,
    redis: Redis,
) -> int:
    """전체 영양제 건수를 반환한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        영양제 총 건수.
    """
    cache_key = make_cache_key("supplement", "count")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(func.count()).select_from(Supplement)
    result = await db.execute(stmt)
    count = result.scalar_one()

    await cache_set(redis, cache_key, count, CACHE_TTL_SUPPLEMENT_COUNT)
    return count
