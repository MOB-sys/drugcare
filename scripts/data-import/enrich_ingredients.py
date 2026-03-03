"""약물 성분(ingredients) 보강 스크립트.

외부 API 없이 기존 DB 데이터만으로 ingredients JSONB를 채운다.

전략:
1. item_name에서 괄호 안 성분명 추출 → ingredients JSONB 생성
2. item_name에서 용량/단위 파싱 (예: "100밀리그램" → amount=100, unit=mg)
3. 수출용/의료기관용 등 비성분 괄호는 제외

사용법:
    python -m scripts.data-import.enrich_ingredients
    python -m scripts.data-import.enrich_ingredients --dry-run
"""

import argparse
import asyncio
import json
import logging
import re
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
logger = logging.getLogger("enrich_ingredients")

# 괄호 안이 성분이 아닌 경우 (제외 패턴)
EXCLUDE_PATTERNS = re.compile(
    r"^(수출용|의료기관용|병원용|약국용|보험용|일반용|전문용|동물용|"
    r"향정|마약|생물|방사성|첨가제변경|명칭변경|포장변경|허가사항변경|"
    r"제형변경|성상변경|유효기간|보험삭제|자진취하|품목갱신|임시|재심사|"
    r"정제|캡슐|시럽|현탁액|주사|연고|크림|패치|겔|액|산제|과립|"
    r"\d+(?:정|캡슐|ml|g|매).*포장)$",
    re.IGNORECASE,
)

# 용량 패턴: 숫자+단위
AMOUNT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(밀리그램|밀리그람|마이크로그램|마이크로그람|그램|그람|밀리리터|밀리리타|"
    r"mg|mcg|g|ml|iu|IU|국제단위|단위|%)",
)

# 단위 통일
UNIT_MAP = {
    "밀리그램": "mg",
    "밀리그람": "mg",
    "마이크로그램": "mcg",
    "마이크로그람": "mcg",
    "그램": "g",
    "그람": "g",
    "밀리리터": "ml",
    "밀리리타": "ml",
    "mg": "mg",
    "mcg": "mcg",
    "g": "g",
    "ml": "ml",
    "iu": "IU",
    "IU": "IU",
    "국제단위": "IU",
    "단위": "U",
    "%": "%",
}


def parse_ingredient_from_name(item_name: str) -> list[dict[str, str | None]]:
    """약물명에서 성분 정보를 추출한다.

    Args:
        item_name: 약물명 (예: "타이레놀정500밀리그램(아세트아미노펜)")

    Returns:
        성분 리스트 [{"name": str, "amount": str|None, "unit": str|None}]
    """
    # 괄호 안 내용 추출
    paren_matches = re.findall(r"\(([^)]+)\)", item_name)
    if not paren_matches:
        return []

    ingredients = []
    for match in paren_matches:
        match = match.strip()
        if EXCLUDE_PATTERNS.match(match):
            continue
        if not match or len(match) < 2:
            continue

        # 성분명으로 간주
        ingredient: dict[str, str | None] = {"name": match, "amount": None, "unit": None}

        # 약물명에서 용량 추출 (괄호 바깥)
        name_before_paren = item_name.split("(")[0]
        amount_match = AMOUNT_PATTERN.search(name_before_paren)
        if amount_match:
            ingredient["amount"] = amount_match.group(1)
            ingredient["unit"] = UNIT_MAP.get(amount_match.group(2), amount_match.group(2))

        ingredients.append(ingredient)

    return ingredients


async def enrich_all(dry_run: bool = False) -> dict[str, int]:
    """전체 약물의 ingredients를 보강한다.

    Args:
        dry_run: True면 실제 DB 수정 없이 시뮬레이션.

    Returns:
        통계 딕셔너리.
    """
    stats = {"total": 0, "updated": 0, "skipped": 0, "already_has": 0}

    async with async_session_factory() as session:
        # ingredients가 비어있는 약물만 조회
        result = await session.execute(text(
            "SELECT id, item_name FROM drugs "
            "WHERE ingredients IS NULL OR ingredients::text = '[]' OR ingredients::text = 'null' "
            "ORDER BY id"
        ))
        rows = result.fetchall()
        stats["total"] = len(rows)
        logger.info("보강 대상 약물: %d건", stats["total"])

        batch_size = 500
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]

            for drug_id, item_name in batch:
                ingredients = parse_ingredient_from_name(item_name)

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

            if not dry_run:
                await session.commit()

            logger.info(
                "진행: %d/%d (갱신: %d, 건너뜀: %d)",
                min(i + batch_size, stats["total"]),
                stats["total"],
                stats["updated"],
                stats["skipped"],
            )

    return stats


def main() -> None:
    """메인 실행."""
    parser = argparse.ArgumentParser(description="약물 성분(ingredients) 보강")
    parser.add_argument("--dry-run", action="store_true", help="실제 수정 없이 시뮬레이션")
    args = parser.parse_args()

    logger.info("약물 성분 보강 시작 (dry_run=%s)", args.dry_run)
    stats = asyncio.run(enrich_all(dry_run=args.dry_run))

    logger.info("=" * 50)
    logger.info("완료 — 전체: %d, 갱신: %d, 건너뜀: %d",
                stats["total"], stats["updated"], stats["skipped"])
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
