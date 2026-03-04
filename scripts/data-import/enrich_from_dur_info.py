"""drug_dur_info 테이블의 ingr_name을 활용한 약물 성분 보강 스크립트.

외부 API 없이 이미 DB에 있는 DUR 안전성 데이터에서 성분명을 추출한다.
drug_dur_info.ingr_name / ingr_eng_name → drugs.ingredients JSONB

사용법:
    python -m scripts.data-import.enrich_from_dur_info
    python -m scripts.data-import.enrich_from_dur_info --dry-run
"""

import argparse
import asyncio
import json
import logging
import sys
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
logger = logging.getLogger("enrich_from_dur_info")


async def enrich_all(dry_run: bool = False) -> dict[str, int]:
    """drug_dur_info의 ingr_name으로 drugs.ingredients를 보강한다."""
    stats = {"total": 0, "updated": 0, "skipped": 0}

    async with async_session_factory() as session:
        # 성분이 없는 약물 중 drug_dur_info에 ingr_name이 있는 것
        result = await session.execute(text("""
            SELECT d.id, d.item_seq, d.item_name,
                   array_agg(DISTINCT ddi.ingr_name) AS ingr_names,
                   array_agg(DISTINCT ddi.ingr_eng_name) AS ingr_eng_names
            FROM drugs d
            JOIN drug_dur_info ddi ON d.item_seq = ddi.item_seq
            WHERE (d.ingredients IS NULL OR d.ingredients::text IN ('[]', 'null'))
              AND ddi.ingr_name IS NOT NULL AND ddi.ingr_name != ''
            GROUP BY d.id, d.item_seq, d.item_name
            ORDER BY d.id
        """))
        rows = result.fetchall()
        stats["total"] = len(rows)
        logger.info("보강 대상 약물: %d건", stats["total"])

        if stats["total"] == 0:
            logger.info("보강할 약물이 없습니다.")
            return stats

        for i, row in enumerate(rows):
            drug_id, item_seq, item_name, ingr_names, ingr_eng_names = row

            # NULL 제거 및 성분 리스트 구성
            ingredients = []
            seen = set()
            for kor, eng in zip(ingr_names, ingr_eng_names):
                if not kor or kor in seen:
                    continue
                seen.add(kor)
                ingredient = {
                    "name": kor.strip(),
                    "name_en": eng.strip() if eng else None,
                    "amount": None,
                    "unit": None,
                }
                ingredients.append(ingredient)

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

            if (i + 1) % 500 == 0:
                if not dry_run:
                    await session.commit()
                logger.info(
                    "진행: %d/%d (갱신: %d, 건너뜀: %d)",
                    i + 1, stats["total"], stats["updated"], stats["skipped"],
                )

        if not dry_run:
            await session.commit()

        logger.info(
            "진행: %d/%d (갱신: %d, 건너뜀: %d)",
            stats["total"], stats["total"], stats["updated"], stats["skipped"],
        )

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="drug_dur_info 기반 성분 보강")
    parser.add_argument("--dry-run", action="store_true", help="실제 수정 없이 시뮬레이션")
    args = parser.parse_args()

    logger.info("drug_dur_info 기반 성분 보강 시작 (dry_run=%s)", args.dry_run)
    stats = asyncio.run(enrich_all(dry_run=args.dry_run))

    logger.info("=" * 50)
    logger.info("완료 — 전체: %d, 갱신: %d, 건너뜀: %d",
                stats["total"], stats["updated"], stats["skipped"])
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
