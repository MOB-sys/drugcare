"""DUR 병용금기 데이터 빠른 추가 수집 스크립트.

기존 수집기(async SQLAlchemy)가 느려서 psycopg2 배치 처리로 대체.
"""

import asyncio
import json
import logging
import os
import re
import sys
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "")
SERVICE_KEY = os.getenv("DATA_GO_KR_SERVICE_KEY", "")

if not DATABASE_URL_SYNC or not SERVICE_KEY:
    sys.exit("ERROR: DATABASE_URL_SYNC, DATA_GO_KR_SERVICE_KEY 필요")

import psycopg2

DUR_URL = (
    "https://apis.data.go.kr/1471000/DURPrdlstInfoService03"
    "/getUsjntTabooInfoList03"
)

_HTML_RE = re.compile(r"<[^>]+>")


def strip_html(t):
    if not t:
        return None
    return re.sub(r"\s+", " ", _HTML_RE.sub(" ", t)).strip() or None


async def main():
    db_url = DATABASE_URL_SYNC.replace("postgresql+asyncpg://", "postgresql://")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1. 약물 lookup 로드
    cur.execute("SELECT item_seq, id, item_name FROM drugs")
    drug_lookup = {row[0]: {"id": row[1], "name": row[2]} for row in cur.fetchall()}
    logger.info("약물 lookup: %d건", len(drug_lookup))

    # 2. 기존 source_id + pair 로드
    cur.execute("SELECT source_id FROM interactions WHERE source = 'DUR' AND source_id IS NOT NULL")
    existing_ids = {row[0] for row in cur.fetchall()}
    logger.info("기존 DUR 상호작용: %d건", len(existing_ids))

    cur.execute("SELECT item_a_id, item_b_id FROM interactions WHERE source = 'DUR'")
    existing_pairs = {(row[0], row[1]) for row in cur.fetchall()}
    logger.info("기존 DUR pair: %d건", len(existing_pairs))

    # 3. API 수집
    async with httpx.AsyncClient() as client:
        params = {"serviceKey": SERVICE_KEY, "pageNo": "1", "numOfRows": "100", "type": "json"}

        resp = await client.get(DUR_URL, params=params, timeout=30)
        data = resp.json()
        total = int(data.get("body", {}).get("totalCount", 0))
        total_pages = (total + 99) // 100
        logger.info("DUR 전체: %d건 (%d페이지)", total, total_pages)

        inserted = 0
        skipped = 0
        errors = 0
        new_drugs = 0
        seen_pairs: set[tuple[int, int]] = set()

        def process_items(items):
            nonlocal inserted, skipped, errors, new_drugs
            for item in items:
                try:
                    dur_seq = str(item.get("DUR_SEQ", ""))
                    seq_a = str(item.get("ITEM_SEQ", "") or "").strip()
                    seq_b = str(item.get("MIXTURE_ITEM_SEQ", "") or "").strip()
                    name_a = str(item.get("ITEM_NAME", "") or "").strip()
                    name_b = str(item.get("MIXTURE_ITEM_NAME", "") or "").strip()

                    if not seq_a or not seq_b or not name_a or not name_b:
                        skipped += 1
                        continue

                    source_id = f"DUR-{dur_seq}-{seq_a}-{seq_b}"
                    if source_id in existing_ids:
                        skipped += 1
                        continue

                    # 약물이 DB에 없으면 INSERT
                    for seq, name in [(seq_a, name_a), (seq_b, name_b)]:
                        if seq not in drug_lookup:
                            try:
                                cur.execute(
                                    """INSERT INTO drugs (item_seq, item_name, slug)
                                    VALUES (%s, %s, %s)
                                    ON CONFLICT (item_seq) DO NOTHING
                                    RETURNING id""",
                                    (seq, name, f"drug-{seq}"),
                                )
                                row = cur.fetchone()
                                if row:
                                    drug_lookup[seq] = {"id": row[0], "name": name}
                                    new_drugs += 1
                                else:
                                    cur.execute("SELECT id, item_name FROM drugs WHERE item_seq = %s", (seq,))
                                    row = cur.fetchone()
                                    if row:
                                        drug_lookup[seq] = {"id": row[0], "name": row[1]}
                            except Exception:
                                conn.rollback()
                                continue

                    if seq_a not in drug_lookup or seq_b not in drug_lookup:
                        skipped += 1
                        continue

                    drug_a = drug_lookup[seq_a]
                    drug_b = drug_lookup[seq_b]

                    description = strip_html(item.get("PROHBT_CONTENT"))
                    ingr_a = item.get("INGR_KOR_NAME") or ""
                    ingr_b = item.get("MIXTURE_INGR_KOR_NAME") or ""
                    mechanism = f"{ingr_a} + {ingr_b}" if ingr_a and ingr_b else None

                    # pair 기반 중복 체크 (전부 메모리)
                    pair_key = (drug_a["id"], drug_b["id"])
                    reverse_key = (drug_b["id"], drug_a["id"])
                    if pair_key in existing_pairs or reverse_key in existing_pairs:
                        skipped += 1
                        continue
                    if source_id in existing_ids:
                        skipped += 1
                        continue

                    cur.execute(
                        """INSERT INTO interactions (
                            item_a_type, item_a_id, item_a_name,
                            item_b_type, item_b_id, item_b_name,
                            severity, description, mechanism,
                            source, source_id, evidence_level
                        ) VALUES (
                            'drug', %s, %s,
                            'drug', %s, %s,
                            'danger', %s, %s,
                            'DUR', %s, 'high'
                        )""",
                        (
                            drug_a["id"], name_a,
                            drug_b["id"], name_b,
                            description, mechanism,
                            source_id,
                        ),
                    )
                    inserted += 1
                    existing_pairs.add(pair_key)
                    existing_ids.add(source_id)

                except Exception as e:
                    conn.rollback()
                    errors += 1
                    if errors <= 5:
                        logger.warning("처리 오류: %s", e)

        # 첫 페이지
        first_items = data.get("body", {}).get("items", [])
        if isinstance(first_items, dict):
            first_items = [first_items]
        process_items(first_items or [])
        conn.commit()

        for page in range(2, total_pages + 1):
            await asyncio.sleep(0.15)
            params["pageNo"] = str(page)
            try:
                resp = await client.get(DUR_URL, params=params, timeout=30)
                pdata = resp.json()
                items = pdata.get("body", {}).get("items", [])
                if isinstance(items, dict):
                    items = [items]
                process_items(items or [])
            except Exception as e:
                errors += 1
                if errors <= 5:
                    logger.warning("페이지 %d 오류: %s", page, e)

            if page % 100 == 0:
                conn.commit()
                logger.info(
                    "진행: %d/%d페이지 (신규: %d, 건너뜀: %d, 신규약물: %d)",
                    page, total_pages, inserted, skipped, new_drugs,
                )

        conn.commit()

    cur.close()

    # 최종 통계
    cur2 = conn.cursor()
    cur2.execute("SELECT COUNT(*) FROM interactions")
    total_intrs = cur2.fetchone()[0]
    cur2.execute("SELECT COUNT(*) FROM drugs")
    total_drugs = cur2.fetchone()[0]
    cur2.close()
    conn.close()

    logger.info("══════════════════════════════════════")
    logger.info("  DUR 수집 완료")
    logger.info("══════════════════════════════════════")
    logger.info("  신규 삽입:    %d", inserted)
    logger.info("  건너뜀:      %d", skipped)
    logger.info("  오류:        %d", errors)
    logger.info("  신규 약물:    %d", new_drugs)
    logger.info("  전체 상호작용: %d", total_intrs)
    logger.info("  전체 약물:    %d", total_drugs)
    logger.info("══════════════════════════════════════")


if __name__ == "__main__":
    asyncio.run(main())
