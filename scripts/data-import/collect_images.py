"""이미지 수집 파이프라인 — Food, Herbal, Supplement 이미지 URL 수집.

Usage:
    python collect_images.py --type {food,herbal,supplement,all} [--dry-run] [--force] [--limit N]

환경변수:
    DATABASE_URL: PostgreSQL 연결 문자열 (필수)
    UNSPLASH_ACCESS_KEY: Unsplash API 키 (필수)
"""

import argparse
import json
import logging
import os
import random
import sys
import time
from urllib.parse import quote

import httpx
import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
UNSPLASH_BASE = "https://api.unsplash.com"
WIKIPEDIA_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary"

# Unsplash 무료 tier: 50 req/hr → 75초 간격으로 안전 유지
UNSPLASH_DELAY = 75  # 초 (약 48 req/hr)
WIKIPEDIA_DELAY = 0.3  # 초


def _progress(current: int, total: int, prefix: str = "") -> str:
    """진행률 문자열을 반환한다."""
    pct = (current / total * 100) if total > 0 else 0
    return f"{prefix}[{current}/{total}] {pct:.0f}%"


def get_db_connection():
    """PostgreSQL 연결을 반환한다."""
    if not DATABASE_URL:
        logger.error("DATABASE_URL 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    return psycopg2.connect(DATABASE_URL)


def unsplash_search(query: str, remaining_calls: dict) -> str | None:
    """Unsplash에서 이미지를 검색하여 최적화된 URL을 반환한다."""
    if not UNSPLASH_ACCESS_KEY:
        logger.error("UNSPLASH_ACCESS_KEY 환경변수가 설정되지 않았습니다.")
        return None

    # Rate limit 체크
    if remaining_calls.get("remaining", 50) <= 2:
        logger.warning("Unsplash rate limit 임박 — 중단합니다.")
        return None

    url = f"{UNSPLASH_BASE}/search/photos"
    params = {
        "query": query,
        "orientation": "landscape",
        "content_filter": "high",
        "per_page": 5,
    }
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}

    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        # Rate limit 추적
        remaining_calls["remaining"] = int(
            resp.headers.get("X-Ratelimit-Remaining", 50)
        )
        logger.info(
            "Unsplash rate limit remaining: %s", remaining_calls["remaining"]
        )

        if resp.status_code == 403:
            logger.warning("Unsplash rate limit 초과")
            return None
        resp.raise_for_status()

        data = resp.json()
        results = data.get("results", [])
        if not results:
            logger.info("  Unsplash 결과 없음: %s", query)
            return None

        # 첫 번째 결과의 raw URL에 크기 파라미터 추가
        raw_url = results[0]["urls"]["raw"]
        optimized = f"{raw_url}&w=400&h=400&fit=crop&auto=format&q=80"
        return optimized
    except Exception as e:
        logger.error("Unsplash 검색 실패 (%s): %s", query, e)
        return None


def unsplash_search_multiple(query: str, count: int, remaining_calls: dict) -> list[str]:
    """Unsplash에서 여러 장의 이미지를 검색한다."""
    if not UNSPLASH_ACCESS_KEY:
        return []

    if remaining_calls.get("remaining", 50) <= 2:
        return []

    url = f"{UNSPLASH_BASE}/search/photos"
    params = {
        "query": query,
        "orientation": "landscape",
        "content_filter": "high",
        "per_page": min(count, 5),
    }
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}

    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        remaining_calls["remaining"] = int(
            resp.headers.get("X-Ratelimit-Remaining", 50)
        )

        if resp.status_code == 403:
            return []
        resp.raise_for_status()

        results = resp.json().get("results", [])
        urls = []
        for r in results[:count]:
            raw_url = r["urls"]["raw"]
            urls.append(f"{raw_url}&w=400&h=400&fit=crop&auto=format&q=80")
        return urls
    except Exception as e:
        logger.error("Unsplash 다중 검색 실패 (%s): %s", query, e)
        return []


def wikipedia_image(latin_name: str) -> str | None:
    """Wikipedia REST API에서 한약재 이미지를 검색한다."""
    # latin_name 정제: 속명+종명만 사용 (저자명 등 제거)
    parts = latin_name.strip().split()
    if len(parts) >= 2:
        clean_name = f"{parts[0]}_{parts[1]}"
    else:
        clean_name = parts[0] if parts else latin_name

    url = f"{WIKIPEDIA_BASE}/{quote(clean_name)}"

    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": "YakMeogeo/1.0 (pillright.com)"},
            timeout=10,
            follow_redirects=True,
        )
        if resp.status_code == 404:
            logger.info("  Wikipedia 페이지 없음: %s", clean_name)
            return None
        resp.raise_for_status()

        data = resp.json()
        thumbnail = data.get("thumbnail", {})
        source = thumbnail.get("source")
        if source:
            logger.info("  Wikipedia 이미지 발견: %s", clean_name)
            return source
        logger.info("  Wikipedia 이미지 없음: %s", clean_name)
        return None
    except Exception as e:
        logger.error("Wikipedia 검색 실패 (%s): %s", clean_name, e)
        return None


# ── Food 수집 ──────────────────────────────────────

def collect_food_images(
    conn, *, dry_run: bool = False, force: bool = False, limit: int = 0
) -> int:
    """Food 이미지를 수집한다. common_names의 영어명으로 Unsplash 검색."""
    cur = conn.cursor()
    where = "" if force else "WHERE image_url IS NULL"
    query = f"SELECT id, name, common_names FROM foods {where} ORDER BY id"
    if limit > 0:
        query += f" LIMIT {limit}"
    cur.execute(query)
    rows = cur.fetchall()
    logger.info("Food 수집 대상: %d건", len(rows))

    remaining = {"remaining": 50}
    updated = 0
    est_minutes = len(rows) * UNSPLASH_DELAY / 60
    logger.info("예상 소요시간: ~%.0f분 (delay %ds/건)", est_minutes, UNSPLASH_DELAY)

    for idx, (food_id, name, common_names) in enumerate(rows, 1):
        # common_names JSONB에서 영어명 추출 (마지막 항목이 보통 영문)
        search_term = name
        if common_names:
            if isinstance(common_names, str):
                common_names = json.loads(common_names)
            if isinstance(common_names, list) and common_names:
                # 영어명 찾기: ASCII 문자로 시작하는 항목
                eng_names = [n for n in common_names if n and n[0].isascii()]
                if eng_names:
                    search_term = eng_names[-1]
                else:
                    search_term = common_names[-1]

        logger.info(
            "%s [Food #%d] %s → 검색: %s",
            _progress(idx, len(rows)),
            food_id,
            name,
            search_term,
        )

        image_url = unsplash_search(f"{search_term} food", remaining)

        if image_url:
            if dry_run:
                logger.info("  [DRY-RUN] URL: %s", image_url[:80])
            else:
                cur.execute(
                    "UPDATE foods SET image_url = %s, updated_at = NOW() WHERE id = %s",
                    (image_url, food_id),
                )
                conn.commit()
                logger.info("  업데이트 완료")
            updated += 1
        else:
            logger.info("  이미지 없음 — 건너뜀")

        if remaining.get("remaining", 50) <= 2:
            logger.warning("Rate limit 임박 — Food 수집 중단")
            break

        time.sleep(UNSPLASH_DELAY)

    cur.close()
    return updated


# ── Herbal 수집 ────────────────────────────────────

def collect_herbal_images(
    conn, *, dry_run: bool = False, force: bool = False, limit: int = 0
) -> int:
    """Herbal 이미지를 수집한다. Wikipedia → Unsplash 폴백."""
    cur = conn.cursor()
    where = "" if force else "WHERE image_url IS NULL"
    query = f"SELECT id, name, latin_name FROM herbal_medicines {where} ORDER BY id"
    if limit > 0:
        query += f" LIMIT {limit}"
    cur.execute(query)
    rows = cur.fetchall()
    logger.info("Herbal 수집 대상: %d건", len(rows))

    remaining = {"remaining": 50}
    updated = 0
    est_minutes = len(rows) * (WIKIPEDIA_DELAY + UNSPLASH_DELAY * 0.3) / 60
    logger.info("예상 소요시간: ~%.0f분 (Wikipedia 우선, Unsplash 폴백)", est_minutes)

    for idx, (herbal_id, name, latin_name) in enumerate(rows, 1):
        logger.info(
            "%s [Herbal #%d] %s (latin: %s)",
            _progress(idx, len(rows)),
            herbal_id,
            name,
            latin_name,
        )

        image_url = None

        # 1차: Wikipedia (latin_name 있을 때)
        if latin_name:
            image_url = wikipedia_image(latin_name)
            time.sleep(WIKIPEDIA_DELAY)

        # 2차: Unsplash 폴백 (속명으로 검색)
        if not image_url:
            if latin_name:
                genus = latin_name.strip().split()[0]
                search_term = f"{genus} herb plant"
            else:
                search_term = f"{name} herb"
            image_url = unsplash_search(search_term, remaining)
            if image_url:
                time.sleep(UNSPLASH_DELAY)

            if remaining.get("remaining", 50) <= 2:
                logger.warning("Rate limit 임박 — Herbal 수집 중단")
                break

        if image_url:
            if dry_run:
                logger.info("  [DRY-RUN] URL: %s", image_url[:80])
            else:
                cur.execute(
                    "UPDATE herbal_medicines SET image_url = %s, updated_at = NOW() WHERE id = %s",
                    (image_url, herbal_id),
                )
                conn.commit()
                logger.info("  업데이트 완료")
            updated += 1
        else:
            logger.info("  이미지 없음 — 건너뜀")

    cur.close()
    return updated


# ── Supplement 수집 ────────────────────────────────

# 카테고리 → 영어 검색어 매핑
SUPPLEMENT_CATEGORY_MAP = {
    "비타민": "vitamin supplement bottle",
    "미네랄": "mineral supplement",
    "프로바이오틱스": "probiotics supplement",
    "오메가-3 지방산": "omega fish oil supplement",
    "오메가-3": "omega fish oil supplement",
    "아미노산": "amino acid supplement",
    "식이섬유": "dietary fiber supplement",
    "콜라겐": "collagen supplement",
    "루테인": "lutein eye supplement",
    "홍삼": "red ginseng supplement",
    "인삼": "ginseng supplement",
    "밀크씨슬": "milk thistle supplement",
    "코엔자임Q10": "coenzyme Q10 supplement",
    "글루코사민": "glucosamine supplement",
}

DEFAULT_SUPPLEMENT_QUERY = "health supplement"


def collect_supplement_images(
    conn, *, dry_run: bool = False, force: bool = False, limit: int = 0
) -> int:
    """Supplement 이미지를 수집한다. 카테고리별 대표 이미지를 랜덤 배정."""
    cur = conn.cursor()
    where = "" if force else "WHERE image_url IS NULL"
    query = f"SELECT id, product_name, category FROM supplements {where} ORDER BY category, id"
    if limit > 0:
        query += f" LIMIT {limit}"
    cur.execute(query)
    rows = cur.fetchall()
    logger.info("Supplement 수집 대상: %d건", len(rows))

    remaining = {"remaining": 50}
    # 카테고리별 이미지 캐시
    category_cache: dict[str, list[str]] = {}
    updated = 0

    for idx, (supp_id, product_name, category) in enumerate(rows, 1):
        cat_key = (category or "").strip()
        logger.info(
            "%s [Supplement #%d] %s (카테고리: %s)",
            _progress(idx, len(rows)),
            supp_id,
            product_name,
            cat_key,
        )

        # 캐시에 없으면 Unsplash에서 가져오기
        if cat_key not in category_cache:
            search_query = DEFAULT_SUPPLEMENT_QUERY
            for kr_cat, en_query in SUPPLEMENT_CATEGORY_MAP.items():
                if kr_cat in cat_key:
                    search_query = en_query
                    break

            logger.info("  카테고리 검색: %s", search_query)
            urls = unsplash_search_multiple(search_query, 5, remaining)
            category_cache[cat_key] = urls

            if remaining.get("remaining", 50) <= 2:
                logger.warning("Rate limit 임박 — Supplement 수집 중단")
                break

            time.sleep(UNSPLASH_DELAY)

        cached_urls = category_cache.get(cat_key, [])
        if not cached_urls:
            logger.info("  이미지 없음 — 건너뜀")
            continue

        # 랜덤 선택 (시각적 다양성)
        image_url = random.choice(cached_urls)

        if dry_run:
            logger.info("  [DRY-RUN] URL: %s", image_url[:80])
        else:
            cur.execute(
                "UPDATE supplements SET image_url = %s, updated_at = NOW() WHERE id = %s",
                (image_url, supp_id),
            )
            conn.commit()
            logger.info("  업데이트 완료")
        updated += 1

    cur.close()
    return updated


# ── Main ───────────────────────────────────────────

def main():
    """CLI 진입점."""
    parser = argparse.ArgumentParser(
        description="이미지 수집 파이프라인 — Food, Herbal, Supplement"
    )
    parser.add_argument(
        "--type",
        choices=["food", "herbal", "supplement", "all"],
        required=True,
        help="수집 대상 타입",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DB 업데이트 없이 URL만 출력",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="이미 이미지가 있는 항목도 재수집",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="수집할 최대 건수 (0 = 전체)",
    )
    args = parser.parse_args()

    conn = get_db_connection()
    total = 0

    try:
        if args.type in ("food", "all"):
            logger.info("=== Food 이미지 수집 시작 ===")
            count = collect_food_images(
                conn, dry_run=args.dry_run, force=args.force, limit=args.limit
            )
            logger.info("Food 수집 완료: %d건", count)
            total += count

        if args.type in ("herbal", "all"):
            logger.info("=== Herbal 이미지 수집 시작 ===")
            count = collect_herbal_images(
                conn, dry_run=args.dry_run, force=args.force, limit=args.limit
            )
            logger.info("Herbal 수집 완료: %d건", count)
            total += count

        if args.type in ("supplement", "all"):
            logger.info("=== Supplement 이미지 수집 시작 ===")
            count = collect_supplement_images(
                conn, dry_run=args.dry_run, force=args.force, limit=args.limit
            )
            logger.info("Supplement 수집 완료: %d건", count)
            total += count

        logger.info("=== 전체 수집 완료: %d건 ===", total)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
