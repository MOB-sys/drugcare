"""nedrug.mfds.go.kr에서 약물 상세정보(효능효과/용법용량/주의사항) 보강 스크립트.

대상: efcy_qesitm, use_method_qesitm, atpn_qesitm이 비어있는 약물
소스: nedrug.mfds.go.kr 상세 페이지 HTML 파싱

사용법:
    python -m scripts.data-import.enrich_drug_details
    python -m scripts.data-import.enrich_drug_details --dry-run
"""

import argparse
import asyncio
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
logger = logging.getLogger("enrich_drug_details")

NEDRUG_URL = "https://nedrug.mfds.go.kr/pbp/CCBBB01/getItemDetail"


def extract_section(html: str, keywords: list[str]) -> str | None:
    """HTML에서 특정 섹션의 info_box 내용을 추출한다."""
    for kw in keywords:
        idx = html.find(kw)
        if idx < 0:
            continue
        snippet = html[idx:idx + 5000]
        box = re.search(r'<div class="info_box"[^>]*>(.*?)</div>', snippet, re.DOTALL)
        if box:
            text_content = re.sub(r'<[^>]+>', '', box.group(1)).strip()
            # 연속 공백/줄바꿈 정리
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            if text_content and len(text_content) > 5:
                return text_content
    return None


def extract_image_url(html: str) -> str | None:
    """약물 이미지 URL을 추출한다 (base64 아닌 URL만)."""
    # nedrug에서 큰 이미지 URL 패턴
    matches = re.findall(
        r'(https?://nedrug\.mfds\.go\.kr/pbp/cmn/itemImageDownload/[^\s"\']+)',
        html,
    )
    if matches:
        return matches[0]

    # 대체: 제품이미지 영역의 img src
    img_section = re.search(
        r'class="[^"]*product[^"]*"[^>]*>.*?<img[^>]+src="([^"]+)"',
        html,
        re.DOTALL | re.I,
    )
    if img_section:
        url = img_section.group(1)
        if not url.startswith('data:'):
            return url

    return None


async def fetch_drug_details(client, item_seq: str) -> dict | None:
    """단일 약물의 상세정보를 nedrug에서 가져온다."""
    try:
        resp = await client.get(
            NEDRUG_URL,
            params={"itemSeq": item_seq},
            follow_redirects=True,
            timeout=20.0,
        )
        if resp.status_code != 200:
            return None

        html = resp.text
        result = {}

        efcy = extract_section(html, [
            "효능효과는 무엇입니까",
            "이 약의 효능",
            "효과는 무엇입니까",
        ])
        if efcy:
            result["efcy_qesitm"] = efcy

        usage = extract_section(html, [
            "용법용량은 무엇입니까",
            "이 약은 어떻게",
            "용법용량",
        ])
        if usage:
            result["use_method_qesitm"] = usage

        warning = extract_section(html, [
            "사용상 주의사항은 무엇입니까",
            "주의사항은 무엇입니까",
        ])
        if warning:
            result["atpn_qesitm"] = warning

        image_url = extract_image_url(html)
        if image_url:
            result["item_image"] = image_url

        return result if result else None

    except Exception as e:
        logger.debug("요청 실패 (item_seq=%s): %s", item_seq, e)
        return None


async def enrich_all(dry_run: bool = False, batch_size: int = 50, delay: float = 0.3) -> dict[str, int]:
    """nedrug에서 약물 상세정보를 보강한다."""
    stats = {"total": 0, "updated": 0, "skipped": 0, "errors": 0,
             "efcy": 0, "usage": 0, "warning": 0, "image": 0}

    async with async_session_factory() as session:
        # 효능효과/용법용량/주의사항 중 하나라도 비어있는 약물
        result = await session.execute(text("""
            SELECT id, item_seq, item_name FROM drugs
            WHERE item_seq IS NOT NULL AND item_seq <> ''
              AND (
                efcy_qesitm IS NULL OR efcy_qesitm = ''
                OR use_method_qesitm IS NULL OR use_method_qesitm = ''
                OR atpn_qesitm IS NULL OR atpn_qesitm = ''
              )
            ORDER BY id
        """))
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
                    details = await fetch_drug_details(client, item_seq)

                    if details is None:
                        stats["errors"] += 1
                        continue

                    if not details:
                        stats["skipped"] += 1
                        continue

                    # 업데이트 쿼리 동적 생성
                    set_clauses = []
                    params = {"id": drug_id}

                    if "efcy_qesitm" in details:
                        set_clauses.append("efcy_qesitm = :efcy")
                        params["efcy"] = details["efcy_qesitm"]
                        stats["efcy"] += 1

                    if "use_method_qesitm" in details:
                        set_clauses.append("use_method_qesitm = :usage")
                        params["usage"] = details["use_method_qesitm"]
                        stats["usage"] += 1

                    if "atpn_qesitm" in details:
                        set_clauses.append("atpn_qesitm = :warning")
                        params["warning"] = details["atpn_qesitm"]
                        stats["warning"] += 1

                    if "item_image" in details:
                        set_clauses.append("item_image = :image")
                        params["image"] = details["item_image"]
                        stats["image"] += 1

                    if set_clauses and not dry_run:
                        sql = f"UPDATE drugs SET {', '.join(set_clauses)} WHERE id = :id"
                        await session.execute(text(sql), params)

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
                    "진행: %d/%d (갱신: %d, 건너뜀: %d, 오류: %d) "
                    "[효능:%d 용법:%d 주의:%d 이미지:%d] [ETA: %.0f분]",
                    done, stats["total"],
                    stats["updated"], stats["skipped"], stats["errors"],
                    stats["efcy"], stats["usage"], stats["warning"], stats["image"],
                    eta_min,
                )

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="nedrug 기반 약물 상세정보 보강")
    parser.add_argument("--dry-run", action="store_true", help="실제 수정 없이 시뮬레이션")
    parser.add_argument("--batch-size", type=int, default=50, help="배치 크기 (기본: 50)")
    parser.add_argument("--delay", type=float, default=0.3, help="요청 간 딜레이 초 (기본: 0.3)")
    args = parser.parse_args()

    logger.info("nedrug 상세정보 보강 시작 (dry_run=%s)", args.dry_run)

    start = time.time()
    stats = asyncio.run(enrich_all(
        dry_run=args.dry_run,
        batch_size=args.batch_size,
        delay=args.delay,
    ))
    elapsed = time.time() - start

    logger.info("=" * 60)
    logger.info("완료 — 전체: %d, 갱신: %d, 건너뜀: %d, 오류: %d (%.1f분)",
                stats["total"], stats["updated"], stats["skipped"], stats["errors"],
                elapsed / 60)
    logger.info("효능: %d, 용법: %d, 주의: %d, 이미지: %d",
                stats["efcy"], stats["usage"], stats["warning"], stats["image"])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
