"""식품(Food) 서비스 — 검색 및 상세 조회 비즈니스 로직."""

import math

from redis.asyncio import Redis
from sqlalchemy import String, case, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.redis import CACHE_TTL_DRUG_DETAIL, CACHE_TTL_DRUG_SEARCH, CACHE_TTL_SUGGEST
from src.backend.models.food import Food
from src.backend.schemas.food import FoodDetail, FoodSearchItem
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key

# slug/count 캐시 TTL (초)
CACHE_TTL_FOOD_SLUGS = 60 * 60 * 24  # 24시간
CACHE_TTL_FOOD_COUNT = 60 * 60 * 24  # 24시간
# 검색/상세 캐시는 drug과 동일한 TTL 사용
CACHE_TTL_FOOD_SEARCH = CACHE_TTL_DRUG_SEARCH
CACHE_TTL_FOOD_DETAIL = CACHE_TTL_DRUG_DETAIL


async def search_foods(
    db: AsyncSession,
    redis: Redis,
    q: str,
    page: int,
    page_size: int,
) -> dict:
    """식품을 이름으로 검색한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 ILIKE 검색을 수행한다.
    name 컬럼과 common_names JSONB 컬럼을 모두 검색한다.
    결과는 PaginatedData[FoodSearchItem] 호환 dict로 반환된다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (식품명).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict (items, total, page, page_size, total_pages).
    """
    cache_key = make_cache_key("food", "search", hash_query(q), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    # 검색 조건 (빈 쿼리면 전체 목록)
    # 식품명, common_names JSONB, 분류로 포괄 검색
    q_stripped = q.strip()
    if q_stripped:
        like_pattern = f"%{q_stripped}%"
        condition = or_(
            Food.name.ilike(like_pattern),
            cast(Food.common_names, String).ilike(like_pattern),
            Food.category.ilike(like_pattern),
        )
        # 관련성 점수: 정확 일치 > 접두사 > 포함(이름) > 포함(기타)
        relevance = case(
            (Food.name.ilike(q_stripped), 4),
            (Food.name.ilike(f"{q_stripped}%"), 3),
            (Food.name.ilike(like_pattern), 2),
            else_=1,
        )
    else:
        condition = None
        relevance = None

    # 전체 건수 조회
    count_stmt = select(func.count()).select_from(Food)
    if condition is not None:
        count_stmt = count_stmt.where(condition)
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    # 페이지네이션 조회 (관련성 높은 순)
    offset = (page - 1) * page_size
    search_stmt = select(Food)
    if condition is not None:
        search_stmt = search_stmt.where(condition)
    if relevance is not None:
        search_stmt = search_stmt.order_by(relevance.desc(), Food.name)
    search_stmt = search_stmt.offset(offset).limit(page_size)
    rows = await db.execute(search_stmt)
    foods = rows.scalars().all()

    items = [FoodSearchItem.model_validate(f).model_dump() for f in foods]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

    await cache_set(redis, cache_key, result, CACHE_TTL_FOOD_SEARCH)
    return result


async def suggest_foods(
    db: AsyncSession,
    redis: Redis,
    q: str,
    limit: int = 10,
) -> list[dict]:
    """식품 검색 자동완성 제안을 반환한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (2자 이상).
        limit: 최대 결과 수 (기본 10).

    Returns:
        [{"name": ..., "slug": ..., "type": "food"}] 형태의 리스트.
    """
    q_stripped = q.strip()
    if len(q_stripped) < 2:
        return []

    cache_key = make_cache_key("food", "suggest", hash_query(q_stripped), str(limit))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    like_pattern = f"%{q_stripped}%"
    relevance = case(
        (Food.name.ilike(q_stripped), 3),
        (Food.name.ilike(f"{q_stripped}%"), 2),
        else_=1,
    )

    stmt = (
        select(Food.name, Food.slug)
        .where(
            or_(
                Food.name.ilike(like_pattern),
                cast(Food.common_names, String).ilike(like_pattern),
            )
        )
        .order_by(relevance.desc(), Food.name)
        .limit(limit)
    )
    rows = await db.execute(stmt)
    result = [{"name": r[0], "slug": r[1], "type": "food"} for r in rows.all()]

    await cache_set(redis, cache_key, result, CACHE_TTL_SUGGEST)
    return result


async def get_food_detail(
    db: AsyncSession,
    redis: Redis,
    food_id: int,
) -> dict | None:
    """식품 상세 정보를 조회한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 PK 조회를 수행한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        food_id: 조회할 식품 ID.

    Returns:
        FoodDetail 구조의 dict 또는 None (존재하지 않는 경우).
    """
    cache_key = make_cache_key("food", "detail", str(food_id))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Food).where(Food.id == food_id)
    row = await db.execute(stmt)
    food = row.scalar_one_or_none()

    if food is None:
        return None

    result = FoodDetail.model_validate(food).model_dump()
    await cache_set(redis, cache_key, result, CACHE_TTL_FOOD_DETAIL)
    return result


async def get_food_by_slug(
    db: AsyncSession,
    redis: Redis,
    slug: str,
) -> dict | None:
    """slug로 식품 상세 정보를 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        slug: 식품 slug (예: food-1).

    Returns:
        FoodDetail 구조의 dict 또는 None.
    """
    cache_key = make_cache_key("food", "by-slug", slug)
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Food).where(Food.slug == slug)
    row = await db.execute(stmt)
    food = row.scalar_one_or_none()

    if food is None:
        return None

    result = FoodDetail.model_validate(food).model_dump()
    await cache_set(redis, cache_key, result, CACHE_TTL_FOOD_DETAIL)
    return result


async def get_all_food_slugs(
    db: AsyncSession,
    redis: Redis,
) -> list[str]:
    """모든 식품 slug 목록을 반환한다 (SSG generateStaticParams용).

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        slug 문자열 리스트.
    """
    cache_key = make_cache_key("food", "slugs", "all")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Food.slug)
    rows = await db.execute(stmt)
    slugs = [row[0] for row in rows.all()]

    await cache_set(redis, cache_key, slugs, CACHE_TTL_FOOD_SLUGS)
    return slugs


async def count_foods(
    db: AsyncSession,
    redis: Redis,
) -> int:
    """전체 식품 건수를 반환한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        식품 총 건수.
    """
    cache_key = make_cache_key("food", "count")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(func.count()).select_from(Food)
    result = await db.execute(stmt)
    count = result.scalar_one()

    await cache_set(redis, cache_key, count, CACHE_TTL_FOOD_COUNT)
    return count
