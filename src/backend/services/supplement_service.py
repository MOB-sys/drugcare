"""영양제(Supplement) 서비스 — 검색 및 상세 조회 비즈니스 로직."""

import math

from redis.asyncio import Redis
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.redis import CACHE_TTL_SUPPLEMENT_DETAIL, CACHE_TTL_SUPPLEMENT_SEARCH
from src.backend.models.supplement import Supplement
from src.backend.schemas.supplement import SupplementDetail, SupplementSearchItem
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key

# slug/count 캐시 TTL (초)
CACHE_TTL_SUPPLEMENT_SLUGS = 60 * 60 * 24  # 24시간
CACHE_TTL_SUPPLEMENT_COUNT = 60 * 60 * 24  # 24시간


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
    cache_key = make_cache_key("supplement", "search", hash_query(q), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    # 검색 조건 (빈 쿼리면 전체 목록)
    # 제품명, 주성분, 기능성, 분류, 제조사로 포괄 검색
    q_stripped = q.strip()
    if q_stripped:
        like_pattern = f"%{q_stripped}%"
        condition = or_(
            Supplement.product_name.ilike(like_pattern),
            Supplement.company.ilike(like_pattern),
            Supplement.main_ingredient.ilike(like_pattern),
            Supplement.functionality.ilike(like_pattern),
            Supplement.category.ilike(like_pattern),
        )
        # 관련성 점수: 정확 일치 > 접두사 > 포함(이름) > 포함(기타)
        relevance = case(
            (Supplement.product_name.ilike(q_stripped), 4),
            (Supplement.product_name.ilike(f"{q_stripped}%"), 3),
            (Supplement.product_name.ilike(like_pattern), 2),
            else_=1,
        )
    else:
        condition = None
        relevance = None

    # 전체 건수 조회
    count_stmt = select(func.count()).select_from(Supplement)
    if condition is not None:
        count_stmt = count_stmt.where(condition)
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    # 페이지네이션 조회 (관련성 높은 순)
    offset = (page - 1) * page_size
    search_stmt = select(Supplement)
    if condition is not None:
        search_stmt = search_stmt.where(condition)
    if relevance is not None:
        search_stmt = search_stmt.order_by(relevance.desc(), Supplement.product_name)
    search_stmt = search_stmt.offset(offset).limit(page_size)
    rows = await db.execute(search_stmt)
    supplements = rows.scalars().all()

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


async def suggest_supplements(
    db: AsyncSession,
    redis: Redis,
    q: str,
    limit: int = 10,
) -> list[dict]:
    """영양제 검색 자동완성 제안을 반환한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (2자 이상).
        limit: 최대 결과 수 (기본 10).

    Returns:
        [{"name": ..., "slug": ..., "type": "supplement"}] 형태의 리스트.
    """
    q_stripped = q.strip()
    if len(q_stripped) < 2:
        return []

    cache_key = make_cache_key("supplement", "suggest", hash_query(q_stripped), str(limit))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    like_pattern = f"%{q_stripped}%"
    relevance = case(
        (Supplement.product_name.ilike(q_stripped), 3),
        (Supplement.product_name.ilike(f"{q_stripped}%"), 2),
        else_=1,
    )

    stmt = (
        select(Supplement.product_name, Supplement.slug)
        .where(Supplement.product_name.ilike(like_pattern))
        .order_by(relevance.desc(), Supplement.product_name)
        .limit(limit)
    )
    rows = await db.execute(stmt)
    result = [{"name": r[0], "slug": r[1], "type": "supplement"} for r in rows.all()]

    await cache_set(redis, cache_key, result, 60 * 60)  # 1시간
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


# drug_service와 동일한 초성 매핑 재사용
from src.backend.services.drug_service import (  # noqa: E402
    _build_letter_condition,
    _CHOSUNG_INDEX_MAP,
)


async def browse_supplements_by_letter(
    db: AsyncSession,
    redis: Redis,
    letter: str,
    page: int,
    page_size: int,
) -> dict:
    """초성/알파벳 글자로 영양제를 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        letter: 초성(ㄱ~ㅎ) 또는 알파벳(A~Z).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict.
    """
    cache_key = make_cache_key("supplement", "browse", letter, str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    condition = _build_letter_condition(letter, Supplement.product_name)
    if condition is None:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    count_stmt = select(func.count()).select_from(Supplement).where(condition)
    total: int = (await db.execute(count_stmt)).scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    offset = (page - 1) * page_size
    query_stmt = (
        select(Supplement)
        .where(condition)
        .order_by(Supplement.product_name)
        .offset(offset)
        .limit(page_size)
    )
    rows = await db.execute(query_stmt)
    supplements = rows.scalars().all()

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


async def get_supplement_counts_by_letter(
    db: AsyncSession,
    redis: Redis,
) -> dict[str, int]:
    """초성/알파벳별 영양제 건수를 반환한다.

    단일 SQL 쿼리로 CASE/WHEN을 사용해 모든 글자 버킷을 한 번에 집계한다.

    Returns:
        {"ㄱ": 34, "ㄴ": 6, "A": 2, ...} 형태의 dict.
    """
    cache_key = make_cache_key("supplement", "browse", "counts")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    chosung_keys = list(_CHOSUNG_INDEX_MAP.keys())
    alpha_keys = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    all_keys = chosung_keys + alpha_keys

    # Build CASE/WHEN expressions for each letter bucket
    case_whens = []
    for letter in all_keys:
        cond = _build_letter_condition(letter, Supplement.product_name)
        if cond is not None:
            case_whens.append(func.count(case((cond, 1))).label(letter))

    if not case_whens:
        counts = {letter: 0 for letter in all_keys}
        await cache_set(redis, cache_key, counts, CACHE_TTL_SUPPLEMENT_COUNT)
        return counts

    stmt = select(*case_whens).select_from(Supplement)
    result = await db.execute(stmt)
    row = result.one()

    counts: dict[str, int] = {}
    for letter in all_keys:
        cond = _build_letter_condition(letter, Supplement.product_name)
        if cond is None:
            counts[letter] = 0
        else:
            counts[letter] = getattr(row, letter, 0) or 0

    await cache_set(redis, cache_key, counts, CACHE_TTL_SUPPLEMENT_COUNT)
    return counts
