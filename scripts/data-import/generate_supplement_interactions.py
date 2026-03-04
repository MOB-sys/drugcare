"""약-영양제 / 영양제-영양제 상호작용 생성 스크립트.

근거 기반(evidence_based) 상호작용 지식 베이스를 활용하여
DB의 실제 약물/영양제를 매칭하고 상호작용 레코드를 생성한다.

사용법:
    python -m scripts.data-import.generate_supplement_interactions
    python -m scripts.data-import.generate_supplement_interactions --dry-run
"""

import argparse
import asyncio
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
logger = logging.getLogger("gen_supp_interactions")


# ============================================================
# 근거 기반 상호작용 지식 베이스
# ============================================================
# 각 규칙: (영양제 성분 키워드, 약물 성분 키워드, severity, description, mechanism, recommendation)
DRUG_SUPPLEMENT_RULES: list[dict] = [
    # ─── 오메가-3 / 크릴오일 + 항응고제 ───
    {
        "supp_keywords": ["오메가", "EPA", "DHA", "크릴오일", "어유"],
        "drug_keywords": ["와파린", "워파린", "헤파린", "리바록사반", "아픽사반", "다비가트란", "에독사반", "클로피도그렐"],
        "severity": "warning",
        "description": "오메가-3 지방산이 혈소판 응집을 억제하여 항응고제와 병용 시 출혈 위험이 증가할 수 있습니다.",
        "mechanism": "오메가-3의 항혈소판 작용과 항응고제의 상승 효과",
        "recommendation": "병용 시 출혈 징후를 모니터링하고, INR 수치를 정기적으로 확인하세요.",
    },
    # ─── 칼슘 + 항생제(테트라사이클린/퀴놀론) ───
    {
        "supp_keywords": ["칼슘", "탄산칼슘"],
        "drug_keywords": ["테트라사이클린", "독시사이클린", "미노사이클린", "시프로플록사신", "레보플록사신", "목시플록사신", "오플록사신"],
        "severity": "warning",
        "description": "칼슘이 항생제와 불용성 복합체를 형성하여 항생제의 흡수를 감소시킬 수 있습니다.",
        "mechanism": "킬레이트 형성에 의한 장관 흡수 저하",
        "recommendation": "칼슘 보충제와 항생제는 최소 2시간 간격을 두고 복용하세요.",
    },
    # ─── 철분 + 항생제 ───
    {
        "supp_keywords": ["철분", "헴철", "황산제일철", "킬레이트 철"],
        "drug_keywords": ["테트라사이클린", "독시사이클린", "미노사이클린", "시프로플록사신", "레보플록사신", "목시플록사신"],
        "severity": "warning",
        "description": "철분이 항생제와 킬레이트를 형성하여 양쪽 모두의 흡수를 감소시킬 수 있습니다.",
        "mechanism": "킬레이트 형성에 의한 장관 흡수 저하",
        "recommendation": "철분 보충제와 항생제는 최소 2시간 간격을 두고 복용하세요.",
    },
    # ─── 철분 + 레보티록신 ───
    {
        "supp_keywords": ["철분", "헴철", "황산제일철", "킬레이트 철"],
        "drug_keywords": ["레보티록신", "갑상선호르몬"],
        "severity": "warning",
        "description": "철분이 레보티록신의 흡수를 감소시켜 갑상선 기능 저하 치료 효과가 줄어들 수 있습니다.",
        "mechanism": "킬레이트 형성에 의한 흡수 저하",
        "recommendation": "철분과 갑상선호르몬제는 최소 4시간 간격을 두고 복용하세요.",
    },
    # ─── 마그네슘 + 항생제 ───
    {
        "supp_keywords": ["마그네슘", "산화마그네슘"],
        "drug_keywords": ["테트라사이클린", "독시사이클린", "시프로플록사신", "레보플록사신"],
        "severity": "caution",
        "description": "마그네슘이 일부 항생제의 흡수를 감소시킬 수 있습니다.",
        "mechanism": "양이온 킬레이트 형성",
        "recommendation": "마그네슘과 항생제는 최소 2시간 간격을 두고 복용하세요.",
    },
    # ─── 비타민K + 와파린 ───
    {
        "supp_keywords": ["비타민K", "메나퀴논", "MK-7"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "danger",
        "description": "비타민K가 와파린의 항응고 효과를 직접적으로 길항하여 혈전 위험이 증가할 수 있습니다.",
        "mechanism": "비타민K는 응고인자 합성에 필요하며, 와파린의 작용 기전을 직접 상쇄",
        "recommendation": "와파린 복용 중 비타민K 보충제 병용을 피하세요. 반드시 의사와 상담하세요.",
    },
    # ─── 은행잎(징코) + 항응고제/항혈소판제 ───
    {
        "supp_keywords": ["은행잎", "징코"],
        "drug_keywords": ["와파린", "워파린", "아스피린", "클로피도그렐", "헤파린"],
        "severity": "warning",
        "description": "은행잎 추출물이 혈소판 활성화 인자(PAF)를 억제하여 출혈 위험을 증가시킬 수 있습니다.",
        "mechanism": "PAF 억제에 의한 항혈소판 작용 상승",
        "recommendation": "수술 2주 전 은행잎 보충제 복용을 중단하고, 항응고제와 병용 시 주의하세요.",
    },
    # ─── 마늘 + 항응고제 ───
    {
        "supp_keywords": ["마늘", "알리인"],
        "drug_keywords": ["와파린", "워파린", "클로피도그렐", "아스피린"],
        "severity": "caution",
        "description": "마늘 보충제가 항혈소판 작용으로 출혈 위험을 약간 증가시킬 수 있습니다.",
        "mechanism": "아조엔(ajoene) 등 마늘 성분의 항혈소판 작용",
        "recommendation": "고용량 마늘 보충제와 항응고제 병용 시 출혈 징후를 관찰하세요.",
    },
    # ─── 코엔자임Q10 + 와파린 ───
    {
        "supp_keywords": ["코엔자임Q10", "CoQ10"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "caution",
        "description": "코엔자임Q10이 와파린의 항응고 효과를 감소시킬 수 있습니다.",
        "mechanism": "CoQ10의 구조가 비타민K와 유사하여 응고인자 합성을 촉진할 수 있음",
        "recommendation": "와파린 복용 중 CoQ10 보충 시 INR 모니터링이 필요합니다.",
    },
    # ─── 비타민E(고용량) + 항응고제 ───
    {
        "supp_keywords": ["비타민E", "토코페롤"],
        "drug_keywords": ["와파린", "워파린", "아스피린", "클로피도그렐"],
        "severity": "caution",
        "description": "고용량 비타민E가 항응고 작용을 강화하여 출혈 위험을 증가시킬 수 있습니다.",
        "mechanism": "비타민K 의존성 응고인자 억제",
        "recommendation": "고용량(400IU 이상) 비타민E와 항응고제 병용 시 주의가 필요합니다.",
    },
    # ─── 녹차추출물 + 철분 ───
    {
        "supp_keywords": ["녹차", "카테킨"],
        "drug_keywords": ["철분", "황산제일철"],
        "severity": "caution",
        "description": "녹차의 탄닌/카테킨이 철분 흡수를 방해할 수 있습니다.",
        "mechanism": "폴리페놀-철 복합체 형성",
        "recommendation": "녹차 추출물과 철분 보충제는 시간 간격을 두고 복용하세요.",
    },
    # ─── 비타민D + 티아지드 이뇨제 ───
    {
        "supp_keywords": ["비타민D", "콜레칼시페롤", "D3"],
        "drug_keywords": ["히드로클로로티아지드", "클로르탈리돈"],
        "severity": "caution",
        "description": "비타민D가 칼슘 흡수를 증가시키고, 티아지드 이뇨제가 칼슘 배설을 감소시켜 고칼슘혈증 위험이 있습니다.",
        "mechanism": "칼슘 항상성의 이중 변화",
        "recommendation": "정기적인 혈중 칼슘 농도 모니터링이 권장됩니다.",
    },
    # ─── 멜라토닌 + 진정제/수면제 ───
    {
        "supp_keywords": ["멜라토닌"],
        "drug_keywords": ["졸피뎀", "트리아졸람", "알프라졸람", "로라제팜", "디아제팜", "클로나제팜"],
        "severity": "warning",
        "description": "멜라토닌과 진정제/수면제를 병용하면 과도한 졸음과 진정 효과가 나타날 수 있습니다.",
        "mechanism": "중추신경계 억제 작용의 상승",
        "recommendation": "병용 시 낮 시간 졸음, 현기증에 주의하세요. 의사와 상담 후 복용하세요.",
    },
    # ─── 홍국(모나콜린K) + 스타틴 ───
    {
        "supp_keywords": ["홍국", "모나콜린"],
        "drug_keywords": ["아토르바스타틴", "로수바스타틴", "심바스타틴", "프라바스타틴", "플루바스타틴", "피타바스타틴"],
        "severity": "danger",
        "description": "홍국의 모나콜린K는 로바스타틴과 동일 물질로, 스타틴과 병용 시 횡문근융해증 등 심각한 근육 부작용 위험이 높습니다.",
        "mechanism": "HMG-CoA 환원효소 이중 억제에 의한 근독성 증가",
        "recommendation": "스타틴 복용 중에는 홍국 보충제를 복용하지 마세요.",
    },
    # ─── 홍삼/인삼 + 와파린 ───
    {
        "supp_keywords": ["홍삼", "인삼", "진세노사이드"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "warning",
        "description": "홍삼이 와파린의 효과를 감소시켜 혈전 위험이 증가할 수 있습니다.",
        "mechanism": "홍삼의 CYP 효소 유도 및 항혈소판 작용",
        "recommendation": "와파린 복용 중 홍삼 보충제 복용 시 INR 모니터링이 필요합니다.",
    },
    # ─── 홍삼 + 당뇨약 ───
    {
        "supp_keywords": ["홍삼", "인삼", "진세노사이드"],
        "drug_keywords": ["메트포르민", "글리메피리드", "글리벤클라미드", "글리클라지드"],
        "severity": "caution",
        "description": "홍삼이 혈당 강하 작용을 가져 당뇨약과 병용 시 저혈당 위험이 있을 수 있습니다.",
        "mechanism": "홍삼의 인슐린 감수성 개선 및 혈당 저하 작용",
        "recommendation": "병용 시 혈당을 자주 모니터링하세요.",
    },
    # ─── 엽산 + 메토트렉세이트 ───
    {
        "supp_keywords": ["엽산", "활성엽산", "5-MTHF"],
        "drug_keywords": ["메토트렉세이트", "메소트렉세이트"],
        "severity": "warning",
        "description": "엽산이 메토트렉세이트의 항엽산 작용을 길항하여 치료 효과를 감소시킬 수 있습니다. 단, 부작용 경감 목적으로 의사 지시 하에 사용하기도 합니다.",
        "mechanism": "엽산 대사 경로의 경쟁적 길항",
        "recommendation": "메토트렉세이트 복용 중 엽산 보충은 반드시 의사 지시에 따라 하세요.",
    },
    # ─── 쏘팔메토 + 항응고제 ───
    {
        "supp_keywords": ["쏘팔메토"],
        "drug_keywords": ["와파린", "워파린", "아스피린"],
        "severity": "caution",
        "description": "쏘팔메토가 COX를 억제하여 항응고제와 병용 시 출혈 위험을 약간 증가시킬 수 있습니다.",
        "mechanism": "COX 억제에 의한 항혈소판 작용",
        "recommendation": "수술 전 쏘팔메토 보충제 중단을 고려하세요.",
    },
    # ─── 글루코사민 + 와파린 ───
    {
        "supp_keywords": ["글루코사민"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "caution",
        "description": "글루코사민이 와파린의 항응고 효과를 증가시켜 INR 상승 및 출혈 위험이 있을 수 있습니다.",
        "mechanism": "정확한 기전 불명, INR 상승 보고 사례 존재",
        "recommendation": "병용 시 INR을 정기적으로 확인하세요.",
    },
    # ─── 폴리코사놀 + 항응고제 ───
    {
        "supp_keywords": ["폴리코사놀"],
        "drug_keywords": ["와파린", "워파린", "아스피린"],
        "severity": "caution",
        "description": "폴리코사놀이 혈소판 응집을 억제하여 항응고제와 병용 시 출혈 위험을 증가시킬 수 있습니다.",
        "mechanism": "혈소판 응집 억제",
        "recommendation": "출혈 징후를 관찰하세요.",
    },
]

# 영양제-영양제 상호작용 규칙
SUPP_SUPP_RULES: list[dict] = [
    {
        "supp_a_keywords": ["철분", "헴철", "황산제일철"],
        "supp_b_keywords": ["칼슘", "탄산칼슘"],
        "severity": "caution",
        "description": "칼슘이 철분의 흡수를 경쟁적으로 저해할 수 있습니다.",
        "mechanism": "장관 내 흡수 경쟁",
        "recommendation": "철분과 칼슘 보충제는 최소 2시간 간격을 두고 복용하세요.",
    },
    {
        "supp_a_keywords": ["녹차", "카테킨"],
        "supp_b_keywords": ["철분", "헴철", "황산제일철"],
        "severity": "caution",
        "description": "녹차의 탄닌이 철분 흡수를 방해할 수 있습니다.",
        "mechanism": "폴리페놀-철 복합체 형성",
        "recommendation": "시간 간격을 두고 복용하세요.",
    },
    {
        "supp_a_keywords": ["홍국", "모나콜린"],
        "supp_b_keywords": ["코엔자임Q10", "CoQ10"],
        "severity": "info",
        "description": "홍국이 CoQ10 합성을 억제할 수 있어, 병용 보충이 권장됩니다.",
        "mechanism": "HMG-CoA 환원효소 억제로 CoQ10 합성 경로도 영향",
        "recommendation": "홍국 보충 시 CoQ10 함께 복용을 고려하세요.",
    },
    {
        "supp_a_keywords": ["비타민C", "아스코르브산"],
        "supp_b_keywords": ["철분", "헴철", "황산제일철"],
        "severity": "info",
        "description": "비타민C가 비헴철의 흡수를 촉진합니다. 함께 복용하면 철분 흡수율이 높아집니다.",
        "mechanism": "Fe3+를 Fe2+로 환원하여 장관 흡수 촉진",
        "recommendation": "철분 보충 시 비타민C와 함께 복용하면 효과적입니다.",
    },
]


def match_keywords(text: str, keywords: list[str]) -> bool:
    """텍스트에 키워드 중 하나라도 포함되면 True."""
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


async def generate_interactions(dry_run: bool = False) -> dict[str, int]:
    """근거 기반 약-영양제/영양제-영양제 상호작용을 생성한다."""
    stats = {"drug_supp": 0, "supp_supp": 0, "skipped_dup": 0}

    async with async_session_factory() as session:
        # 모든 약물 로드 (id, item_name, ingredients)
        drug_rows = await session.execute(text(
            "SELECT id, item_name, ingredients::text FROM drugs"
        ))
        drugs = drug_rows.fetchall()

        # 모든 영양제 로드
        supp_rows = await session.execute(text(
            "SELECT id, product_name, main_ingredient FROM supplements"
        ))
        supplements = supp_rows.fetchall()

        # 기존 상호작용 source_id 셋 (중복 방지)
        existing = await session.execute(text(
            "SELECT source_id FROM interactions WHERE source = 'evidence_based' AND source_id IS NOT NULL"
        ))
        existing_ids = {r[0] for r in existing.fetchall()}

        logger.info("약물 %d건, 영양제 %d건, 기존 evidence_based %d건",
                     len(drugs), len(supplements), len(existing_ids))

        insert_sql = text("""
            INSERT INTO interactions (
                item_a_type, item_a_id, item_a_name,
                item_b_type, item_b_id, item_b_name,
                severity, description, mechanism, recommendation,
                source, source_id, evidence_level
            ) VALUES (
                :a_type, :a_id, :a_name,
                :b_type, :b_id, :b_name,
                :severity, :description, :mechanism, :recommendation,
                'evidence_based', :source_id, 'established'
            )
            ON CONFLICT (item_a_type, item_a_id, item_b_type, item_b_id, severity, source)
            DO NOTHING
        """)

        # 약-영양제 상호작용 생성
        for rule in DRUG_SUPPLEMENT_RULES:
            # 매칭 영양제 찾기
            matched_supps = []
            for supp_id, product_name, main_ingredient in supplements:
                search_text = f"{product_name} {main_ingredient or ''}"
                if match_keywords(search_text, rule["supp_keywords"]):
                    matched_supps.append((supp_id, product_name))

            if not matched_supps:
                continue

            # 매칭 약물 찾기 (성분명 기반)
            matched_drugs = []
            for drug_id, item_name, ingredients_text in drugs:
                search_text = f"{item_name} {ingredients_text or ''}"
                if match_keywords(search_text, rule["drug_keywords"]):
                    matched_drugs.append((drug_id, item_name))

            if not matched_drugs:
                continue

            # 상호작용 레코드 생성
            for supp_id, supp_name in matched_supps:
                for drug_id, drug_name in matched_drugs:
                    source_id = f"EB_S{supp_id}_D{drug_id}"
                    if source_id in existing_ids:
                        stats["skipped_dup"] += 1
                        continue

                    if not dry_run:
                        await session.execute(insert_sql, {
                            "a_type": "supplement",
                            "a_id": supp_id,
                            "a_name": supp_name,
                            "b_type": "drug",
                            "b_id": drug_id,
                            "b_name": drug_name,
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "mechanism": rule["mechanism"],
                            "recommendation": rule["recommendation"],
                            "source_id": source_id,
                        })
                    existing_ids.add(source_id)
                    stats["drug_supp"] += 1

            logger.info("규칙 [%s x %s]: 영양제 %d x 약물 %d = %d 조합",
                         rule["supp_keywords"][0], rule["drug_keywords"][0],
                         len(matched_supps), len(matched_drugs),
                         len(matched_supps) * len(matched_drugs))

        # 영양제-영양제 상호작용 생성
        for rule in SUPP_SUPP_RULES:
            matched_a = []
            matched_b = []
            for supp_id, product_name, main_ingredient in supplements:
                search_text = f"{product_name} {main_ingredient or ''}"
                if match_keywords(search_text, rule["supp_a_keywords"]):
                    matched_a.append((supp_id, product_name))
                if match_keywords(search_text, rule["supp_b_keywords"]):
                    matched_b.append((supp_id, product_name))

            for a_id, a_name in matched_a:
                for b_id, b_name in matched_b:
                    if a_id == b_id:
                        continue
                    source_id = f"EB_SS{a_id}_{b_id}"
                    if source_id in existing_ids:
                        stats["skipped_dup"] += 1
                        continue

                    if not dry_run:
                        await session.execute(insert_sql, {
                            "a_type": "supplement",
                            "a_id": a_id,
                            "a_name": a_name,
                            "b_type": "supplement",
                            "b_id": b_id,
                            "b_name": b_name,
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "mechanism": rule["mechanism"],
                            "recommendation": rule["recommendation"],
                            "source_id": source_id,
                        })
                    existing_ids.add(source_id)
                    stats["supp_supp"] += 1

        if not dry_run:
            await session.commit()

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="약-영양제 상호작용 생성")
    parser.add_argument("--dry-run", action="store_true", help="실제 DB 수정 없이 시뮬레이션")
    args = parser.parse_args()

    logger.info("약-영양제 상호작용 생성 시작 (dry_run=%s)", args.dry_run)
    stats = asyncio.run(generate_interactions(dry_run=args.dry_run))

    logger.info("=" * 60)
    logger.info("완료 — 약-영양제: %d건, 영양제-영양제: %d건, 중복 건너뜀: %d건",
                stats["drug_supp"], stats["supp_supp"], stats["skipped_dup"])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
