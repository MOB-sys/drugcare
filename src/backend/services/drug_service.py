"""의약품(Drug) 서비스 — 검색 및 상세 조회 비즈니스 로직."""

import math
from datetime import datetime, timedelta, timezone

from redis.asyncio import Redis
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.redis import CACHE_TTL_DRUG_DETAIL, CACHE_TTL_DRUG_SEARCH
from src.backend.models.drug import Drug
from src.backend.models.drug_dur_info import DrugDURInfo
from src.backend.schemas.drug import (
    DrugConditionItem,
    DrugDetail,
    DrugIdentifyItem,
    DrugSearchItem,
    DrugSideEffectItem,
    DURSafetyItem,
)
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key

# slug/count 캐시 TTL (초)
CACHE_TTL_DRUG_SLUGS = 60 * 60 * 24  # 24시간
CACHE_TTL_DRUG_COUNT = 60 * 60 * 24  # 24시간


async def search_drugs(
    db: AsyncSession,
    redis: Redis,
    q: str,
    page: int,
    page_size: int,
) -> dict:
    """의약품을 이름으로 검색한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 ILIKE 검색을 수행한다.
    결과는 PaginatedData[DrugSearchItem] 호환 dict로 반환된다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (의약품명).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict (items, total, page, page_size, total_pages).
    """
    cache_key = make_cache_key("drug", "search", hash_query(q), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    # 검색 조건 (빈 쿼리면 전체 목록)
    # 제품명, 성분, 효능효과, 제약사명으로 포괄 검색
    q_stripped = q.strip()
    if q_stripped:
        like_pattern = f"%{q_stripped}%"
        condition = or_(
            Drug.item_name.ilike(like_pattern),
            Drug.entp_name.ilike(like_pattern),
            Drug.material_name.ilike(like_pattern),
            Drug.efcy_qesitm.ilike(like_pattern),
        )
    else:
        condition = None

    # 전체 건수 조회
    count_stmt = select(func.count()).select_from(Drug)
    if condition is not None:
        count_stmt = count_stmt.where(condition)
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    # 페이지네이션 조회
    offset = (page - 1) * page_size
    search_stmt = select(Drug)
    if condition is not None:
        search_stmt = search_stmt.where(condition)
    search_stmt = search_stmt.offset(offset).limit(page_size)
    rows = await db.execute(search_stmt)
    drugs = rows.scalars().all()

    items = [DrugSearchItem.model_validate(drug).model_dump() for drug in drugs]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result


async def _fetch_dur_safety(db: AsyncSession, item_seq: str) -> list[dict]:
    """약물의 DUR 안전성 정보를 조회한다.

    Args:
        db: 비동기 DB 세션.
        item_seq: 약물 품목기준코드.

    Returns:
        DURSafetyItem dict 리스트.
    """
    stmt = select(DrugDURInfo).where(DrugDURInfo.item_seq == item_seq)
    rows = await db.execute(stmt)
    dur_items = rows.scalars().all()
    return [DURSafetyItem.model_validate(item).model_dump() for item in dur_items]


async def get_drug_detail(
    db: AsyncSession,
    redis: Redis,
    drug_id: int,
) -> dict | None:
    """의약품 상세 정보를 조회한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 PK 조회를 수행한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        drug_id: 조회할 의약품 ID.

    Returns:
        DrugDetail 구조의 dict 또는 None (존재하지 않는 경우).
    """
    cache_key = make_cache_key("drug", "detail", str(drug_id))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Drug).where(Drug.id == drug_id)
    row = await db.execute(stmt)
    drug = row.scalar_one_or_none()

    if drug is None:
        return None

    result = DrugDetail.model_validate(drug).model_dump()
    result["dur_safety"] = await _fetch_dur_safety(db, drug.item_seq)
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_DETAIL)
    return result


async def get_drug_by_slug(
    db: AsyncSession,
    redis: Redis,
    slug: str,
) -> dict | None:
    """slug로 의약품 상세 정보를 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        slug: 의약품 slug (예: drug-200001234).

    Returns:
        DrugDetail 구조의 dict 또는 None.
    """
    cache_key = make_cache_key("drug", "by-slug", slug)
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Drug).where(Drug.slug == slug)
    row = await db.execute(stmt)
    drug = row.scalar_one_or_none()

    if drug is None:
        return None

    result = DrugDetail.model_validate(drug).model_dump()
    result["dur_safety"] = await _fetch_dur_safety(db, drug.item_seq)
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_DETAIL)
    return result


async def get_all_drug_slugs(
    db: AsyncSession,
    redis: Redis,
) -> list[str]:
    """모든 의약품 slug 목록을 반환한다 (SSG generateStaticParams용).

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        slug 문자열 리스트.
    """
    cache_key = make_cache_key("drug", "slugs", "all")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Drug.slug)
    rows = await db.execute(stmt)
    slugs = [row[0] for row in rows.all()]

    await cache_set(redis, cache_key, slugs, CACHE_TTL_DRUG_SLUGS)
    return slugs


async def count_drugs(
    db: AsyncSession,
    redis: Redis,
) -> int:
    """전체 의약품 건수를 반환한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.

    Returns:
        의약품 총 건수.
    """
    cache_key = make_cache_key("drug", "count")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(func.count()).select_from(Drug)
    result = await db.execute(stmt)
    count = result.scalar_one()

    await cache_set(redis, cache_key, count, CACHE_TTL_DRUG_COUNT)
    return count


async def search_by_symptom(
    db: AsyncSession,
    redis: Redis,
    symptom: str,
    page: int,
    page_size: int,
) -> dict:
    """증상 키워드로 효능효과 컬럼을 검색한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        symptom: 증상 키워드 (예: 두통, 소화불량).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict.
    """
    cache_key = make_cache_key("drug", "symptom", hash_query(symptom), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    symptom_stripped = symptom.strip()
    if not symptom_stripped:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    condition = Drug.efcy_qesitm.ilike(f"%{symptom_stripped}%")

    count_stmt = select(func.count()).select_from(Drug).where(condition)
    total: int = (await db.execute(count_stmt)).scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    offset = (page - 1) * page_size
    query_stmt = (
        select(Drug).where(condition).order_by(Drug.item_name).offset(offset).limit(page_size)
    )
    rows = await db.execute(query_stmt)
    drugs = rows.scalars().all()

    items = [DrugSearchItem.model_validate(d).model_dump() for d in drugs]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result


async def get_recent_drugs(
    db: AsyncSession,
    redis: Redis,
    days: int,
    limit: int,
) -> list[dict]:
    """최근 N일 이내에 등록된 의약품 목록을 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        days: 조회 범위 (일).
        limit: 최대 결과 수.

    Returns:
        DrugSearchItem dict 리스트.
    """
    cache_key = make_cache_key("drug", "recent", str(days), str(limit))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    days_ago = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = (
        select(Drug)
        .where(Drug.created_at >= days_ago)
        .order_by(Drug.created_at.desc())
        .limit(limit)
    )
    rows = await db.execute(stmt)
    drugs = rows.scalars().all()

    result = [DrugSearchItem.model_validate(d).model_dump() for d in drugs]
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result


# 한글 초성 → 유니코드 범위 매핑 (19개 초성 인덱스)
_CHOSUNG_LABELS = [
    "ㄱ",
    "ㄲ",
    "ㄴ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
]

# 프론트에서 쓰는 14자 초성 → 실제 19자 초성 인덱스 매핑
_CHOSUNG_INDEX_MAP: dict[str, list[int]] = {
    "ㄱ": [0, 1],  # ㄱ, ㄲ
    "ㄴ": [2],
    "ㄷ": [3, 4],  # ㄷ, ㄸ
    "ㄹ": [5],
    "ㅁ": [6],
    "ㅂ": [7, 8],  # ㅂ, ㅃ
    "ㅅ": [9, 10],  # ㅅ, ㅆ
    "ㅇ": [11],
    "ㅈ": [12, 13],  # ㅈ, ㅉ
    "ㅊ": [14],
    "ㅋ": [15],
    "ㅌ": [16],
    "ㅍ": [17],
    "ㅎ": [18],
}


def _build_chosung_condition(letter: str, column):
    """한글 초성에 해당하는 유니코드 범위 조건을 생성한다."""

    indices = _CHOSUNG_INDEX_MAP.get(letter)
    if not indices:
        return None

    conditions = []
    for idx in indices:
        start = chr(0xAC00 + idx * 588)
        end = chr(0xAC00 + (idx + 1) * 588 - 1)
        conditions.append(and_(column >= start, column <= end))
    return or_(*conditions) if conditions else None


def _build_letter_condition(letter: str, column):
    """글자 인덱스 키에 해당하는 SQL 조건을 생성한다."""
    if letter in _CHOSUNG_INDEX_MAP:
        return _build_chosung_condition(letter, column)
    if len(letter) == 1 and letter.isascii() and letter.isalpha():
        upper = letter.upper()
        return or_(
            column.ilike(f"{upper}%"),
            column.ilike(f"{upper.lower()}%"),
        )
    return None


async def browse_drugs_by_letter(
    db: AsyncSession,
    redis: Redis,
    letter: str,
    page: int,
    page_size: int,
) -> dict:
    """초성/알파벳 글자로 의약품을 조회한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        letter: 초성(ㄱ~ㅎ) 또는 알파벳(A~Z).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict.
    """
    cache_key = make_cache_key("drug", "browse", letter, str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    condition = _build_letter_condition(letter, Drug.item_name)
    if condition is None:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    count_stmt = select(func.count()).select_from(Drug).where(condition)
    total: int = (await db.execute(count_stmt)).scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    offset = (page - 1) * page_size
    query_stmt = (
        select(Drug).where(condition).order_by(Drug.item_name).offset(offset).limit(page_size)
    )
    rows = await db.execute(query_stmt)
    drugs = rows.scalars().all()

    items = [DrugSearchItem.model_validate(d).model_dump() for d in drugs]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result


async def get_drug_counts_by_letter(
    db: AsyncSession,
    redis: Redis,
) -> dict[str, int]:
    """초성/알파벳별 의약품 건수를 반환한다.

    단일 SQL 쿼리로 CASE/WHEN을 사용해 모든 글자 버킷을 한 번에 집계한다.

    Returns:
        {"ㄱ": 234, "ㄴ": 56, "A": 12, ...} 형태의 dict.
    """
    cache_key = make_cache_key("drug", "browse", "counts")
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    chosung_keys = list(_CHOSUNG_INDEX_MAP.keys())
    alpha_keys = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    all_keys = chosung_keys + alpha_keys

    # Build CASE/WHEN expressions for each letter bucket
    case_whens = []
    for letter in all_keys:
        cond = _build_letter_condition(letter, Drug.item_name)
        if cond is not None:
            case_whens.append(func.count(case((cond, 1))).label(letter))

    if not case_whens:
        counts = {letter: 0 for letter in all_keys}
        await cache_set(redis, cache_key, counts, CACHE_TTL_DRUG_COUNT)
        return counts

    stmt = select(*case_whens).select_from(Drug)
    result = await db.execute(stmt)
    row = result.one()

    counts: dict[str, int] = {}
    for letter in all_keys:
        cond = _build_letter_condition(letter, Drug.item_name)
        if cond is None:
            counts[letter] = 0
        else:
            counts[letter] = getattr(row, letter, 0) or 0

    await cache_set(redis, cache_key, counts, CACHE_TTL_DRUG_COUNT)
    return counts


async def search_by_side_effect(
    db: AsyncSession,
    redis: Redis,
    q: str,
    page: int,
    page_size: int,
) -> dict:
    """부작용 키워드로 의약품을 검색한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 부작용 검색어.
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict.
    """
    cache_key = make_cache_key("drug", "side-effect", hash_query(q), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    q_stripped = q.strip()
    if not q_stripped:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    condition = Drug.se_qesitm.ilike(f"%{q_stripped}%")

    count_stmt = select(func.count()).select_from(Drug).where(condition)
    total: int = (await db.execute(count_stmt)).scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    offset = (page - 1) * page_size
    query_stmt = select(Drug).where(condition).offset(offset).limit(page_size)
    rows = await db.execute(query_stmt)
    drugs = rows.scalars().all()

    items = [DrugSideEffectItem.model_validate(d).model_dump() for d in drugs]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result


async def identify_drug(
    db: AsyncSession,
    redis: Redis,
    color: str | None,
    shape: str | None,
    imprint: str | None,
    page: int,
    page_size: int,
) -> dict:
    """약 외형(색상, 모양, 각인)으로 의약품을 식별한다.

    chart 필드에서 색상/모양/각인 텍스트를 ILIKE로 검색한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        color: 약 색상 키워드.
        shape: 약 모양 키워드.
        imprint: 각인 문자.
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict.
    """
    parts = [color or "", shape or "", imprint or ""]
    cache_key = make_cache_key(
        "drug",
        "identify",
        *[hash_query(p) for p in parts],
        str(page),
        str(page_size),
    )
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    conditions = []
    if color and color.strip():
        conditions.append(Drug.chart.ilike(f"%{color.strip()}%"))
    if shape and shape.strip():
        conditions.append(Drug.chart.ilike(f"%{shape.strip()}%"))
    if imprint and imprint.strip():
        conditions.append(Drug.chart.ilike(f"%{imprint.strip()}%"))

    if not conditions:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    condition = and_(*conditions)

    count_stmt = select(func.count()).select_from(Drug).where(condition)
    total: int = (await db.execute(count_stmt)).scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    offset = (page - 1) * page_size
    query_stmt = select(Drug).where(condition).offset(offset).limit(page_size)
    rows = await db.execute(query_stmt)
    drugs = rows.scalars().all()

    items = [DrugIdentifyItem.model_validate(d).model_dump() for d in drugs]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result


async def search_by_condition(
    db: AsyncSession,
    redis: Redis,
    condition_q: str,
    page: int,
    page_size: int,
) -> dict:
    """질환 키워드로 주의사항에서 약물을 검색한다.

    atpn_qesitm과 atpn_warn_qesitm 필드를 모두 검색한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        condition_q: 질환 검색어.
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict.
    """
    cache_key = make_cache_key(
        "drug",
        "condition",
        hash_query(condition_q),
        str(page),
        str(page_size),
    )
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    q_stripped = condition_q.strip()
    if not q_stripped:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    like_pattern = f"%{q_stripped}%"
    condition = or_(
        Drug.atpn_qesitm.ilike(like_pattern),
        Drug.atpn_warn_qesitm.ilike(like_pattern),
    )

    count_stmt = select(func.count()).select_from(Drug).where(condition)
    total: int = (await db.execute(count_stmt)).scalar_one()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    page = min(page, max(1, total_pages))

    offset = (page - 1) * page_size
    query_stmt = select(Drug).where(condition).offset(offset).limit(page_size)
    rows = await db.execute(query_stmt)
    drugs = rows.scalars().all()

    items = [DrugConditionItem.model_validate(d).model_dump() for d in drugs]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result
