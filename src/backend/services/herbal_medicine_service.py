"""한약재(HerbalMedicine) 서비스 — 검색 및 상세 조회 비즈니스 로직."""

import math

from redis.asyncio import Redis
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.redis import CACHE_TTL_DRUG_DETAIL, CACHE_TTL_DRUG_SEARCH
from src.backend.models.herbal_medicine import HerbalMedicine
from src.backend.schemas.herbal_medicine import HerbalMedicineDetail, HerbalMedicineSearchItem
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key

# slug/count 캐시 TTL (초)
CACHE_TTL_HERBAL_SLUGS = 60 * 60 * 24  # 24시간
CACHE_TTL_HERBAL_COUNT = 60 * 60 * 24  # 24시간
# 검색/상세 캐시는 drug과 동일한 TTL 사용
CACHE_TTL_HERBAL_SEARCH = CACHE_TTL_DRUG_SEARCH
CACHE_TTL_HERBAL_DETAIL = CACHE_TTL_DRUG_DETAIL


async def search_herbal_medicines(
    db: AsyncSession,
    redis: Redis,
    q: str,
    page: int,
    page_size: int,
) -> dict:
    """한약재를 이름으로 검색한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 ILIKE 검색을 수행한다.
    name, korean_name, latin_name 컬럼을 모두 검색한다.
    결과는 PaginatedData[HerbalMedicineSearchItem] 호환 dict로 반환된다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (한약재명).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict (items, total, page, page_size, total_pages).
    """
    cache_key = make_cache_key("herbal", "search", hash_query(q), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    # 검색 조건 (빈 쿼리면 전체 목록)
    # 대표명, 한글명, 학명, 분류로 포괄 검색
    q_stripped = q.strip()
    if q_stripped:
        like_pattern = f"%{q_stripped}%"
        condition = or_(
            HerbalMedicine.name.ilike(like_pattern),
            HerbalMedicine.korean_name.ilike(like_pattern),
            HerbalMedicine.latin_name.ilike(like_pattern),
            HerbalMedicine.category.ilike(like_pattern),
        )
        # 관련성 점수: 정확 일치 > 접두사 > 포함(이름) > 포함(기타)
        relevance = case(
            (HerbalMedicine.name.ilike(q_stripped), 4),
            (HerbalMedicine.name.ilike(f"{q_stripped}%"), 3),
            (HerbalMedicine.name.ilike(like_pattern), 2),
            else_=1,
        )
    else:
        condition = None
        relevance = None

    # 전체 건수 조회
    count_stmt = select(func.count()).select_from(HerbalMedicine)
    if condition is not None:
        count_stmt = count_stmt.where(condition)
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    # 페이지네이션 조회 (관련성 높은 순)
    offset = (page - 1) * page_size
    search_stmt = select(HerbalMedicine)
    if condition is not None:
        search_stmt = search_stmt.where(condition)
    if relevance is not None:
        search_stmt = search_stmt.order_by(relevance.desc(), HerbalMedicine.name)
    search_stmt = search_stmt.offset(offset).limit(page_size)
    rows = await db.execute(search_stmt)
    herbals = rows.scalars().all()

    items = [HerbalMedicineSearchItem.model_validate(h).model_dump() for h in herbals]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

    await cache_set(redis, cache_key, result, CACHE_TTL_HERBAL_SEARCH)
    return result


async def suggest_herbal_medicines(
    db: AsyncSession,
    redis: Redis,
    q: str,
    limit: int = 10,
) -> list[dict]:
    """한약재 검색 자동완성 제안을 반환한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (2자 이상).
        limit: 최대 결과 수 (기본 10).

    Returns:
        [{"name": ..., "slug": ..., "type": "herbal"}] 형태의 리스트.
    """
    q_stripped = q.strip()
    if len(q_stripped) < 2:
        return []

    cache_key = make_cache_key("herbal", "suggest", hash_query(q_stripped), str(limit))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    like_pattern = f"%{q_stripped}%"
    relevance = case(
        (HerbalMedicine.name.ilike(q_stripped), 3),
        (HerbalMedicine.name.ilike(f"{q_stripped}%"), 2),
        else_=1,
    )

    stmt = (
        select(HerbalMedicine.name, HerbalMedicine.slug)
        .where(
            or_(
                HerbalMedicine.name.ilike(like_pattern),
                HerbalMedicine.korean_name.ilike(like_pattern),
            )
        )
        .order_by(relevance.desc(), HerbalMedicine.name)
        .limit(limit)
    )
    rows = await db.execute(stmt)
    result = [{"name": r[0], "slug": r[1], "type": "herbal"} for r in rows.all()]

    await cache_set(redis, cache_key, result, 60 * 60)  # 1시간
    return result


async def get_herbal_medicine_detail(
    db: AsyncSession,
    redis: Redis,
    herbal_id: int,
) -> dict | None:
    """한약재 상세 정보를 조회한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 PK 조회를 수행한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        herbal_id: 조회할 한약재 ID.

    Returns:
        HerbalMedicineDetail 구조의 dict 또는 None (존재하지 않는 경우).
    """
    cache_key = make_cache_key("herbal", "detail", str(herbal_id))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(HerbalMedicine).where(HerbalMedicine.id == herbal_id)
    row = await db.execute(stmt)
    herbal = row.scalar_one_or_none()

    if herbal is None:
        return None

    result = HerbalMedicineDetail.model_validate(herbal).model_dump()
    await cache_set(redis, cache_key, result, CACHE_TTL_HERBAL_DETAIL)
    return result


async def get_herbal_medicine_by_slug(
    db: AsyncSession,
    redis: Redis,
    slug: str,
) -> dict | None:
    """slug로 한약재 상세 정보를 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        slug: 한약재 slug (예: herbal-1).

    Returns:
        HerbalMedicineDetail 구조의 dict 또는 None.
    """
    cache_key = make_cache_key("herbal", "by-slug", slug)
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(HerbalMedicine).where(HerbalMedicine.slug == slug)
    row = await db.execute(stmt)
    herbal = row.scalar_one_or_none()

    if herbal is None:
        return None

    result = HerbalMedicineDetail.model_validate(herbal).model_dump()
    await cache_set(redis, cache_key, result, CACHE_TTL_HERBAL_DETAIL)
    return result


async def get_all_herbal_medicine_slugs(
    db: AsyncSession,
    redis: Redis,
) -> list[str]:
    """모든 한약재 slug 목록을 반환한다 (SSG generateStaticParams용).

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        slug 문자열 리스트.
    """
    cache_key = make_cache_key("herbal", "slugs", "all")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(HerbalMedicine.slug)
    rows = await db.execute(stmt)
    slugs = [row[0] for row in rows.all()]

    await cache_set(redis, cache_key, slugs, CACHE_TTL_HERBAL_SLUGS)
    return slugs


async def count_herbal_medicines(
    db: AsyncSession,
    redis: Redis,
) -> int:
    """전체 한약재 건수를 반환한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        한약재 총 건수.
    """
    cache_key = make_cache_key("herbal", "count")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(func.count()).select_from(HerbalMedicine)
    result = await db.execute(stmt)
    count = result.scalar_one()

    await cache_set(redis, cache_key, count, CACHE_TTL_HERBAL_COUNT)
    return count
