"""nedrug.mfds.go.kr 웹 스크래핑을 통한 약물 성분 보강 스크립트.

의약품안전나라(nedrug) 상세 페이지에서 성분정보 테이블을 파싱하여
drugs.ingredients JSONB를 채운다.

사용법:
    python -m scripts.data-import.enrich_from_nedrug
    python -m scripts.data-import.enrich_from_nedrug --dry-run
    python -m scripts.data-import.enrich_from_nedrug --batch-size 100
"""

import argparse
import asyncio
import json
import logging
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text

from src.backend.core.database import async_session_factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("enrich_from_nedrug")

NEDRUG_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail"

# 단위 통일 맵
UNIT_MAP = {
    "밀리그램": "mg",
    "밀리그람": "mg",
    "마이크로그램": "mcg",
    "마이크로그람": "mcg",
    "그램": "g",
    "그람": "g",
    "밀리리터": "ml",
    "밀리리타": "ml",
    "리터": "L",
    "국제단위": "IU",
}


def normalize_unit(unit: str | None) -> str | None:
    """한글 단위를 영문 약어로 통일."""
    if not unit:
        return None
    return UNIT_MAP.get(unit, unit)


def parse_ingredients_from_html(html: str) -> list[dict]:
    """nedrug 상세 페이지 HTML에서 성분 정보를 추출한다."""
    idx = html.find("성분정보")
    if idx < 0:
        return []

    section = html[idx:idx + 100000]

    json_strs = re.findall(r"var aasda = (\{.*?\});", section, re.DOTALL)
    if not json_strs:
        return []

    ingredients = []
    seen = set()
    for js in json_strs:
        try:
            obj = json.loads(js)
        except json.JSONDecodeError:
            continue

        name = obj.get("ingrName", "")
        if not name or name in seen:
            continue
        seen.add(name)

        amount = obj.get("ingrTotqy", "")
        unit = obj.get("ingrUnitName", "")

        ingredients.append({
            "name": name.strip(),
            "amount": str(amount).strip() if amount else None,
            "unit": normalize_unit(unit.strip()) if unit else None,
        })

    return ingredients


async def fetch_ingredients(client, item_seq: str) -> list[dict] | None:
    """단일 약물의 성분 정보를 nedrug에서 가져온다."""
    try:
        resp = await client.get(
            NEDRUG_URL,
            params={"itemSeq": item_seq},
            follow_redirects=True,
            timeout=20.0,
        )
        if resp.status_code != 200:
            return None
        return parse_ingredients_from_html(resp.text)
    except Exception as e:
        logger.debug("요청 실패 (item_seq=%s): %s", item_seq, e)
        return None


async def enrich_all(dry_run: bool = False, batch_size: int = 50, delay: float = 0.3) -> dict[str, int]:
    """nedrug 스크래핑으로 남은 약물 성분을 보강한다."""
    stats = {"total": 0, "updated": 0, "skipped": 0, "errors": 0}

    async with async_session_factory() as session:
        result = await session.execute(text(
            "SELECT id, item_seq, item_name FROM drugs "
            "WHERE (ingredients IS NULL OR ingredients::text IN ('[]', 'null')) "
            "AND item_seq IS NOT NULL AND item_seq != '' "
            "ORDER BY id"
        ))
        rows = result.fetchall()
        stats["total"] = len(rows)
        logger.info("보강 대상 약물: %d건", stats["total"])

        if stats["total"] == 0:
            return stats

        import httpx

        async with httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (YakMeogeo DataCollector)"},
        ) as client:
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                batch_start = time.time()

                for drug_id, item_seq, item_name in batch:
                    ingredients = await fetch_ingredients(client, item_seq)

                    if ingredients is None:
                        stats["errors"] += 1
                        continue

                    if not ingredients:
                        stats["skipped"] += 1
                        continue

                    if not dry_run:
                        await session.execute(
                            text("UPDATE drugs SET ingredients = CAST(:ingredients AS jsonb) WHERE id = :id"),
                            {
                                "id": drug_id,
                                "ingredients": json.dumps(ingredients, ensure_ascii=False),
                            },
                        )
                    stats["updated"] += 1

                    await asyncio.sleep(delay)

                if not dry_run:
                    await session.commit()

                elapsed = time.time() - batch_start
                done = min(i + batch_size, stats["total"])
                remaining = stats["total"] - done
                rate = batch_size / elapsed if elapsed > 0 else 0
                eta_min = remaining / rate / 60 if rate > 0 else 0

                logger.info(
                    "진행: %d/%d (갱신: %d, 건너뜀: %d, 오류: %d) [ETA: %.0f분]",
                    done, stats["total"],
                    stats["updated"], stats["skipped"], stats["errors"],
                    eta_min,
                )

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="nedrug.mfds.go.kr 기반 성분 보강")
    parser.add_argument("--dry-run", action="store_true", help="실제 수정 없이 시뮬레이션")
    parser.add_argument("--batch-size", type=int, default=50, help="배치 크기 (기본: 50)")
    parser.add_argument("--delay", type=float, default=0.3, help="요청 간 딜레이 초 (기본: 0.3)")
    args = parser.parse_args()

    logger.info("nedrug 스크래핑 성분 보강 시작 (dry_run=%s, batch=%d, delay=%.1f)",
                args.dry_run, args.batch_size, args.delay)

    start = time.time()
    stats = asyncio.run(enrich_all(
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        delay=args.delay,
    ))
    elapsed = time.time() - start

    logger.info("=" * 50)
    logger.info("완료 — 전체: %d, 갱신: %d, 건너뜀: %d, 오류: %d (%.1f분)",
                stats["total"], stats["updated"], stats["skipped"], stats["errors"],
                elapsed / 60)
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
