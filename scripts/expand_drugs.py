"""약물 데이터 대폭 확장 스크립트.

3단계로 진행:
  1단계: 허가상세 API → 신규 약물 대량 INSERT + 효능/용법/성분 (12K → 44K)
  2단계: e약은요 API → 효능/용법/부작용 보강 (환자용 설명)
  3단계: 낱알식별 API → 이미지/외형정보 보강

사용법:
  python scripts/expand_drugs.py --step all
  python scripts/expand_drugs.py --step 1   # 허가상세만
  python scripts/expand_drugs.py --step 2   # e약은요만
  python scripts/expand_drugs.py --step 3   # 낱알식별만
"""

import asyncio
import json
import logging
import os
import re
import sys
import argparse
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

# ── DB 접속 ──────────────────────────────────────────
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "")
SERVICE_KEY = os.getenv("DATA_GO_KR_SERVICE_KEY", "")

if not DATABASE_URL_SYNC:
    sys.exit("ERROR: DATABASE_URL_SYNC 환경변수가 필요합니다.")
if not SERVICE_KEY:
    sys.exit("ERROR: DATA_GO_KR_SERVICE_KEY 환경변수가 필요합니다.")

import psycopg2
from psycopg2.extras import execute_values

# HTML 태그 제거
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = _HTML_TAG_RE.sub(" ", text)
    cleaned = cleaned.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    cleaned = cleaned.replace("&nbsp;", " ").replace("&quot;", '"')
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else None


def parse_ingredients(material_name: str | None) -> list[dict]:
    """성분 텍스트를 구조화된 리스트로 파싱."""
    if not material_name:
        return []
    cleaned = strip_html(material_name)
    if not cleaned:
        return []

    ingredients = []
    if "|" in cleaned:
        separator = ";" if ";" in cleaned else ","
        parts = cleaned.split(separator)
        for part in parts:
            part = part.strip()
            if not part or part.startswith("총량"):
                continue
            fields = [f.strip() for f in part.split("|")]
            # "성분명 : XXX" 형식 처리
            name = None
            amount = None
            unit = None
            for f in fields:
                if f.startswith("성분명 :") or f.startswith("성분명:"):
                    name = f.split(":", 1)[1].strip()
                elif f.startswith("분량 :") or f.startswith("분량:"):
                    amount = f.split(":", 1)[1].strip()
                elif f.startswith("단위 :") or f.startswith("단위:"):
                    unit = f.split(":", 1)[1].strip()

            if name:
                ingredients.append({"name": name, "amount": amount or None, "unit": unit or None})
            elif fields[0] and not fields[0].startswith("총량"):
                ingredients.append({
                    "name": fields[0],
                    "amount": fields[1] if len(fields) > 1 and fields[1] else None,
                    "unit": fields[2] if len(fields) > 2 and fields[2] else None,
                })
    elif cleaned:
        ingredients.append({"name": cleaned, "amount": None, "unit": None})
    return ingredients


# ── API 요청 헬퍼 ──────────────────────────────────────
REQUEST_DELAY = 0.15
MAX_RETRIES = 3


async def api_request(
    client: httpx.AsyncClient,
    url: str,
    params: dict,
) -> dict | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = await client.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 * attempt)
            else:
                logger.warning("API 실패 (%s): %s", url.split("/")[-1], e)
    return None


def extract_body_items(data: dict) -> tuple[list, int]:
    """공공데이터포털 표준 응답에서 items + totalCount 추출."""
    body = data.get("body", {})
    total = int(body.get("totalCount", 0))
    items = body.get("items", [])
    if isinstance(items, dict):
        items = [items]
    return items or [], total


# ══════════════════════════════════════════════════════
# 1단계: 허가상세 API → 신규 약물 대량 INSERT + 효능/용법/성분
# ══════════════════════════════════════════════════════

PERMISSION_URL = (
    "https://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService07"
    "/getDrugPrdtPrmsnDtlInq06"
)


async def step1_permission(conn):
    """허가상세 API에서 전체 의약품을 수집하여 DB에 upsert한다."""
    logger.info("═══ 1단계: 허가상세 API → 약물 대량 추가 + 상세정보 시작 ═══")

    cur = conn.cursor()
    cur.execute("SELECT item_seq FROM drugs")
    existing = {row[0] for row in cur.fetchall()}
    logger.info("기존 약물: %d건", len(existing))

    async with httpx.AsyncClient() as client:
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": "1",
            "numOfRows": "100",
            "type": "json",
        }
        first = await api_request(client, PERMISSION_URL, params)
        if not first:
            logger.error("허가상세 첫 페이지 실패")
            return

        items, total = extract_body_items(first)
        total_pages = (total + 99) // 100
        logger.info("허가상세 전체: %d건 (%d페이지)", total, total_pages)

        inserted = 0
        updated = 0
        skipped = 0
        errors = 0

        def process_and_upsert(items_list):
            nonlocal inserted, updated, skipped, errors
            for item in items_list:
                try:
                    seq = str(item.get("ITEM_SEQ", "") or "").strip()
                    name = str(item.get("ITEM_NAME", "") or "").strip()
                    if not seq or not name:
                        skipped += 1
                        continue

                    material = item.get("MATERIAL_NAME") or ""
                    ingr = parse_ingredients(material)

                    # 효능/용법/주의사항 추출 (HTML 태그 제거)
                    efcy = strip_html(item.get("EE_DOC_DATA"))
                    usage = strip_html(item.get("UD_DOC_DATA"))
                    nb = strip_html(item.get("NB_DOC_DATA"))

                    # class_no: ATC_CODE 사용
                    class_no = (item.get("ATC_CODE") or "").strip()[:10] or None

                    cur.execute(
                        """INSERT INTO drugs (
                            item_seq, item_name, entp_name, etc_otc_code,
                            class_no, chart, bar_code, material_name, ingredients,
                            efcy_qesitm, use_method_qesitm, atpn_qesitm,
                            deposit_method_qesitm, slug
                        ) VALUES (
                            %(item_seq)s, %(item_name)s, %(entp_name)s, %(etc_otc_code)s,
                            %(class_no)s, %(chart)s, %(bar_code)s, %(material_name)s,
                            %(ingredients)s::jsonb,
                            %(efcy)s, %(usage)s, %(nb)s,
                            %(storage)s, %(slug)s
                        )
                        ON CONFLICT (item_seq) DO UPDATE SET
                            item_name = EXCLUDED.item_name,
                            entp_name = COALESCE(EXCLUDED.entp_name, drugs.entp_name),
                            etc_otc_code = COALESCE(EXCLUDED.etc_otc_code, drugs.etc_otc_code),
                            class_no = COALESCE(EXCLUDED.class_no, drugs.class_no),
                            chart = COALESCE(EXCLUDED.chart, drugs.chart),
                            bar_code = COALESCE(EXCLUDED.bar_code, drugs.bar_code),
                            material_name = COALESCE(EXCLUDED.material_name, drugs.material_name),
                            ingredients = CASE
                                WHEN drugs.ingredients IS NULL OR drugs.ingredients::text = '[]' OR drugs.ingredients::text = 'null'
                                THEN EXCLUDED.ingredients
                                ELSE drugs.ingredients
                            END,
                            efcy_qesitm = COALESCE(drugs.efcy_qesitm, EXCLUDED.efcy_qesitm),
                            use_method_qesitm = COALESCE(drugs.use_method_qesitm, EXCLUDED.use_method_qesitm),
                            atpn_qesitm = COALESCE(drugs.atpn_qesitm, EXCLUDED.atpn_qesitm),
                            deposit_method_qesitm = COALESCE(drugs.deposit_method_qesitm, EXCLUDED.deposit_method_qesitm),
                            updated_at = NOW()""",
                        {
                            "item_seq": seq,
                            "item_name": name,
                            "entp_name": (item.get("ENTP_NAME") or "").strip() or None,
                            "etc_otc_code": (item.get("ETC_OTC_CODE") or "").strip() or None,
                            "class_no": class_no,
                            "chart": strip_html(item.get("CHART")),
                            "bar_code": (item.get("BAR_CODE") or "").strip()[:50] or None,
                            "material_name": strip_html(material) if material else None,
                            "ingredients": json.dumps(ingr, ensure_ascii=False),
                            "efcy": efcy,
                            "usage": usage,
                            "nb": nb,
                            "storage": strip_html(item.get("STORAGE_METHOD")),
                            "slug": f"drug-{seq}",
                        },
                    )
                    if seq in existing:
                        updated += 1
                    else:
                        inserted += 1
                        existing.add(seq)

                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        logger.warning("아이템 처리 오류: %s", e)

            conn.commit()

        # 첫 페이지 처리
        process_and_upsert(items)

        # 나머지 페이지
        for page in range(2, total_pages + 1):
            await asyncio.sleep(REQUEST_DELAY)
            params["pageNo"] = str(page)
            data = await api_request(client, PERMISSION_URL, params)
            if not data:
                errors += 1
                continue
            page_items, _ = extract_body_items(data)
            process_and_upsert(page_items)

            if page % 50 == 0:
                logger.info(
                    "  허가상세 진행: %d/%d페이지 (신규: %d, 갱신: %d)",
                    page, total_pages, inserted, updated,
                )

    cur.close()
    logger.info(
        "═══ 1단계 완료 — 신규: %d, 갱신: %d, 건너뜀: %d, 오류: %d ═══",
        inserted, updated, skipped, errors,
    )


# ══════════════════════════════════════════════════════
# 2단계: e약은요 API → 효능/용법/부작용 보강 (환자용 설명)
# ══════════════════════════════════════════════════════

EDRUG_URL = "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"


async def step2_edrug(conn):
    """e약은요 API에서 효능/용법/부작용 등 환자용 설명을 보강한다."""
    logger.info("═══ 2단계: e약은요 API → 환자용 설명 보강 시작 ═══")

    cur = conn.cursor()

    async with httpx.AsyncClient() as client:
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": "1",
            "numOfRows": "100",
            "type": "json",
        }
        first = await api_request(client, EDRUG_URL, params)
        if not first:
            logger.error("e약은요 첫 페이지 실패")
            return

        items, total = extract_body_items(first)
        total_pages = (total + 99) // 100
        logger.info("e약은요 전체: %d건 (%d페이지)", total, total_pages)

        updated = 0
        errors = 0

        def process_edrug_items(items_list):
            nonlocal updated, errors
            for item in items_list:
                try:
                    seq = str(item.get("itemSeq", "") or "").strip()
                    if not seq:
                        continue

                    efcy = strip_html(item.get("efcyQesitm"))
                    usage = strip_html(item.get("useMethodQesitm"))
                    warn = strip_html(item.get("atpnWarnQesitm"))
                    atpn = strip_html(item.get("atpnQesitm"))
                    intrc = strip_html(item.get("intrcQesitm"))
                    se = strip_html(item.get("seQesitm"))
                    deposit = strip_html(item.get("depositMethodQesitm"))
                    image = (item.get("itemImage") or "").strip() or None

                    # e약은요 데이터가 더 읽기 좋으므로 기존 허가상세 데이터를 덮어씀
                    cur.execute(
                        """UPDATE drugs SET
                            efcy_qesitm = COALESCE(%(efcy)s, drugs.efcy_qesitm),
                            use_method_qesitm = COALESCE(%(usage)s, drugs.use_method_qesitm),
                            atpn_warn_qesitm = COALESCE(%(warn)s, drugs.atpn_warn_qesitm),
                            atpn_qesitm = COALESCE(%(atpn)s, drugs.atpn_qesitm),
                            intrc_qesitm = COALESCE(%(intrc)s, drugs.intrc_qesitm),
                            se_qesitm = COALESCE(%(se)s, drugs.se_qesitm),
                            deposit_method_qesitm = COALESCE(%(deposit)s, drugs.deposit_method_qesitm),
                            item_image = COALESCE(%(image)s, drugs.item_image),
                            updated_at = NOW()
                        WHERE item_seq = %(seq)s""",
                        {"seq": seq, "efcy": efcy, "usage": usage, "warn": warn,
                         "atpn": atpn, "intrc": intrc, "se": se, "deposit": deposit,
                         "image": image},
                    )
                    if cur.rowcount > 0:
                        updated += 1

                except Exception as e:
                    errors += 1

        # 첫 페이지
        process_edrug_items(items)

        for page in range(2, total_pages + 1):
            await asyncio.sleep(REQUEST_DELAY)
            params["pageNo"] = str(page)
            data = await api_request(client, EDRUG_URL, params)
            if not data:
                errors += 1
                continue
            page_items, _ = extract_body_items(data)
            process_edrug_items(page_items)

            if page % 10 == 0:
                conn.commit()
                logger.info("  e약은요 진행: %d/%d페이지 (보강: %d)", page, total_pages, updated)

        conn.commit()

    cur.close()
    logger.info("═══ 2단계 완료 — 보강: %d, 오류: %d ═══", updated, errors)


# ══════════════════════════════════════════════════════
# 3단계: 낱알식별 API → 이미지/외형정보 보강
# ══════════════════════════════════════════════════════

IDENTIFY_URL = (
    "https://apis.data.go.kr/1471000/MdcinGrnIdntfcInfoService03"
    "/getMdcinGrnIdntfcInfoList03"
)


async def step3_identify(conn):
    """낱알식별 API에서 이미지 URL을 보강한다."""
    logger.info("═══ 3단계: 낱알식별 API → 이미지 보강 시작 ═══")

    cur = conn.cursor()

    # 이미지가 없는 약물의 item_seq 목록
    cur.execute(
        "SELECT item_seq FROM drugs WHERE item_image IS NULL OR item_image = ''"
    )
    target_seqs = {row[0] for row in cur.fetchall()}
    logger.info("이미지 없는 약물: %d건", len(target_seqs))

    if not target_seqs:
        logger.info("보강 대상 없음 — 건너뜀")
        cur.close()
        return

    async with httpx.AsyncClient() as client:
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": "1",
            "numOfRows": "100",
            "type": "json",
        }
        first = await api_request(client, IDENTIFY_URL, params)
        if not first:
            logger.error("낱알식별 첫 페이지 실패")
            return

        items, total = extract_body_items(first)
        total_pages = (total + 99) // 100
        logger.info("낱알식별 전체: %d건 (%d페이지)", total, total_pages)

        updated = 0
        errors = 0

        def process_identify_items(items_list):
            nonlocal updated, errors
            for item in items_list:
                try:
                    seq = str(item.get("ITEM_SEQ", "") or "").strip()
                    if not seq or seq not in target_seqs:
                        continue

                    image_url = (item.get("ITEM_IMAGE") or "").strip()
                    if not image_url:
                        continue

                    cur.execute(
                        """UPDATE drugs SET
                            item_image = %(image)s,
                            updated_at = NOW()
                        WHERE item_seq = %(seq)s
                          AND (item_image IS NULL OR item_image = '')""",
                        {"seq": seq, "image": image_url},
                    )
                    if cur.rowcount > 0:
                        updated += 1
                        target_seqs.discard(seq)

                except Exception as e:
                    errors += 1

        process_identify_items(items)

        for page in range(2, total_pages + 1):
            await asyncio.sleep(REQUEST_DELAY)
            params["pageNo"] = str(page)
            data = await api_request(client, IDENTIFY_URL, params)
            if not data:
                errors += 1
                continue
            page_items, _ = extract_body_items(data)
            process_identify_items(page_items)

            if page % 50 == 0:
                conn.commit()
                logger.info("  낱알식별 진행: %d/%d페이지 (이미지 보강: %d)", page, total_pages, updated)

        conn.commit()

    cur.close()
    logger.info("═══ 3단계 완료 — 이미지 보강: %d, 오류: %d ═══", updated, errors)


# ══════════════════════════════════════════════════════
# 최종 통계
# ══════════════════════════════════════════════════════

def print_stats(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE efcy_qesitm IS NOT NULL AND efcy_qesitm != '') as has_efficacy,
            COUNT(*) FILTER (WHERE use_method_qesitm IS NOT NULL AND use_method_qesitm != '') as has_usage,
            COUNT(*) FILTER (WHERE ingredients IS NOT NULL AND ingredients::text != '[]' AND ingredients::text != 'null') as has_ingredients,
            COUNT(*) FILTER (WHERE item_image IS NOT NULL AND item_image != '') as has_image
        FROM drugs
    """)
    row = cur.fetchone()
    cur.close()

    logger.info("══════════════════════════════════════")
    logger.info("  최종 통계")
    logger.info("══════════════════════════════════════")
    logger.info("  전체 약물:    %d", row[0])
    logger.info("  효능 있음:    %d (%d%%)", row[1], row[1] * 100 // max(row[0], 1))
    logger.info("  용법 있음:    %d (%d%%)", row[2], row[2] * 100 // max(row[0], 1))
    logger.info("  성분 있음:    %d (%d%%)", row[3], row[3] * 100 // max(row[0], 1))
    logger.info("  이미지 있음:  %d (%d%%)", row[4], row[4] * 100 // max(row[0], 1))
    logger.info("══════════════════════════════════════")


# ══════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════

async def main(step: str):
    db_url = DATABASE_URL_SYNC
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = psycopg2.connect(db_url)

    try:
        if step in ("1", "all"):
            await step1_permission(conn)
        if step in ("2", "all"):
            await step2_edrug(conn)
        if step in ("3", "all"):
            await step3_identify(conn)

        print_stats(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="약물 데이터 확장")
    parser.add_argument("--step", default="all", choices=["1", "2", "3", "all"])
    args = parser.parse_args()

    asyncio.run(main(args.step))
