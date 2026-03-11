"""식품-약물 상호작용 생성 스크립트.

근거 기반(evidence_based) 상호작용 지식 베이스를 활용하여
DB의 실제 식품/약물을 매칭하고 상호작용 레코드를 생성한다.

사용법:
    python -m scripts.data-import.generate_food_interactions
    python -m scripts.data-import.generate_food_interactions --dry-run
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
logger = logging.getLogger("gen_food_interactions")


# ============================================================
# 근거 기반 식품-약물 상호작용 지식 베이스 (30+ 규칙)
# ============================================================

DRUG_FOOD_RULES: list[dict] = [
    # ─── 자몽 + 스타틴 (CYP3A4 억제) ───
    {
        "food_keywords": ["자몽", "그레이프프루트"],
        "drug_keywords": ["심바스타틴", "아토르바스타틴", "로바스타틴"],
        "severity": "danger",
        "description": "자몽은 CYP3A4 효소를 억제하여 스타틴 계열 약물의 혈중 농도를 크게 높일 수 있습니다.",
        "mechanism": "자몽의 푸라노쿠마린 성분이 소장의 CYP3A4 효소를 비가역적으로 억제",
        "recommendation": "이 약물 복용 중에는 자몽 및 자몽주스 섭취를 피하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 자몽 + 칼슘채널차단제 ───
    {
        "food_keywords": ["자몽", "그레이프프루트"],
        "drug_keywords": ["암로디핀", "펠로디핀", "니페디핀", "니카르디핀", "니솔디핀"],
        "severity": "warning",
        "description": "자몽이 칼슘채널차단제의 혈중 농도를 높여 과도한 혈압 저하, 두통, 부종을 유발할 수 있습니다.",
        "mechanism": "CYP3A4 억제에 의한 약물 대사 저하 → 혈중 농도 상승",
        "recommendation": "자몽 및 자몽주스를 피하거나, 약물 복용 후 최소 4시간 간격을 두세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 자몽 + 면역억제제 ───
    {
        "food_keywords": ["자몽", "그레이프프루트"],
        "drug_keywords": ["사이클로스포린", "타크로리무스"],
        "severity": "danger",
        "description": "자몽이 면역억제제의 혈중 농도를 급격히 높여 신독성, 간독성 등 심각한 부작용을 유발할 수 있습니다.",
        "mechanism": "CYP3A4 억제에 의한 약물 대사 저하 → 혈중 농도 급상승",
        "recommendation": "면역억제제 복용 중에는 자몽을 절대 섭취하지 마세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 자몽 + 항부정맥제 ───
    {
        "food_keywords": ["자몽", "그레이프프루트"],
        "drug_keywords": ["아미오다론", "드로네다론"],
        "severity": "danger",
        "description": "자몽이 항부정맥제의 혈중 농도를 높여 QT 연장 등 심각한 부정맥을 유발할 수 있습니다.",
        "mechanism": "CYP3A4 억제에 의한 약물 대사 저하",
        "recommendation": "절대 병용하지 마세요. 생명 위협적 부정맥 위험.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 우유/유제품 + 테트라사이클린 ───
    {
        "food_keywords": ["우유", "치즈", "요거트", "유제품"],
        "drug_keywords": ["테트라사이클린", "독시사이클린", "미노사이클린"],
        "severity": "warning",
        "description": "우유의 칼슘이 테트라사이클린계 항생제와 불용성 복합체를 형성하여 항생제 흡수를 크게 감소시킵니다.",
        "mechanism": "Ca²⁺ 이온과 킬레이트 형성 → 장관 흡수율 50~80% 감소",
        "recommendation": "항생제 복용 전후 2시간 동안 유제품 섭취를 피하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 우유/유제품 + 퀴놀론 항생제 ───
    {
        "food_keywords": ["우유", "치즈", "요거트", "유제품"],
        "drug_keywords": ["시프로플록사신", "레보플록사신", "목시플록사신", "오플록사신"],
        "severity": "warning",
        "description": "우유의 칼슘이 퀴놀론계 항생제의 흡수를 현저히 감소시킵니다.",
        "mechanism": "다가 양이온(Ca²⁺)과 킬레이트 형성 → 흡수율 최대 85% 감소",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 유제품을 섭취하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 비타민K 식품 + 와파린 ───
    {
        "food_keywords": ["시금치", "케일", "브로콜리", "양배추", "파슬리", "깻잎", "부추", "쑥", "청국장", "낫토"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "danger",
        "description": "비타민K가 풍부한 식품은 와파린의 항응고 효과를 직접적으로 길항하여 혈전 위험을 증가시킵니다.",
        "mechanism": "비타민K는 응고인자(II, VII, IX, X) 합성의 보조인자로, 와파린의 비타민K 에폭시드 환원효소 억제 효과를 상쇄",
        "recommendation": "와파린 복용 중 비타민K 식품 섭취량을 매일 일정하게 유지하세요. 갑자기 많이 먹거나 중단하지 마세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 바나나/칼륨 식품 + ACE 억제제 ───
    {
        "food_keywords": ["바나나", "오렌지", "고구마", "감자", "토마토", "수박"],
        "drug_keywords": ["에날라프릴", "리시노프릴", "라미프릴", "캅토프릴", "페린도프릴"],
        "severity": "caution",
        "description": "칼륨이 풍부한 식품과 ACE 억제제를 병용하면 고칼륨혈증 위험이 증가할 수 있습니다.",
        "mechanism": "ACE 억제제가 알도스테론 분비를 감소시켜 칼륨 배설 저하 + 고칼륨 식품 섭취 → 고칼륨혈증",
        "recommendation": "고칼륨 식품의 과도한 섭취를 피하고, 정기적으로 혈중 칼륨 수치를 확인하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 바나나/칼륨 식품 + 칼륨보존이뇨제 ───
    {
        "food_keywords": ["바나나", "오렌지", "고구마", "감자", "토마토"],
        "drug_keywords": ["스피로노락톤", "트리암테렌", "아밀로라이드", "에플레레논"],
        "severity": "warning",
        "description": "칼륨보존이뇨제와 고칼륨 식품을 함께 섭취하면 심각한 고칼륨혈증(부정맥, 심정지)이 발생할 수 있습니다.",
        "mechanism": "칼륨보존이뇨제가 신장의 칼륨 배설을 억제 + 고칼륨 식품 → 혈중 칼륨 위험 수준 상승",
        "recommendation": "고칼륨 식품의 대량 섭취를 피하세요. 정기적인 혈중 칼륨 모니터링이 필요합니다.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 치즈/간장/와인(티라민) + MAO 억제제 ───
    {
        "food_keywords": ["치즈", "간장", "된장", "와인", "맥주", "김치", "청국장", "소시지", "살라미"],
        "drug_keywords": ["모클로베마이드", "페넬진", "트라닐시프로민", "셀레길린", "라사길린"],
        "severity": "danger",
        "description": "티라민 함유 식품과 MAO 억제제를 병용하면 고혈압 위기(hypertensive crisis)가 발생할 수 있습니다.",
        "mechanism": "MAO 억제제가 티라민 분해를 차단 → 티라민 축적 → 노르에피네프린 대량 방출 → 급격한 혈압 상승",
        "recommendation": "MAO 억제제 복용 중 및 중단 후 2주간 티라민 함유 식품을 엄격히 제한하세요. 심한 두통, 목 뻣뻣함 시 즉시 응급실.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 커피/카페인 + 테오필린 ───
    {
        "food_keywords": ["커피", "카페인", "에너지드링크"],
        "drug_keywords": ["테오필린", "아미노필린"],
        "severity": "warning",
        "description": "카페인과 테오필린은 구조가 유사한 크산틴 유도체로, 병용 시 부작용(빈맥, 불면, 진전)이 증폭됩니다.",
        "mechanism": "CYP1A2 경쟁적 대사 + 아데노신 수용체 길항 작용 중첩",
        "recommendation": "테오필린 복용 중 카페인 섭취를 최소화하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 커피/카페인 + 항정신병약 ───
    {
        "food_keywords": ["커피", "카페인", "에너지드링크"],
        "drug_keywords": ["클로자핀", "올란자핀"],
        "severity": "caution",
        "description": "카페인이 CYP1A2 기질인 항정신병약의 혈중 농도에 영향을 줄 수 있습니다.",
        "mechanism": "CYP1A2 경쟁적 대사 → 클로자핀 등의 혈중 농도 변동",
        "recommendation": "카페인 섭취량을 일정하게 유지하세요. 갑자기 카페인을 많이 늘리거나 줄이면 약물 농도가 변합니다.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 알코올 + 아세트아미노펜 ───
    {
        "food_keywords": ["알코올", "술", "맥주", "소주", "와인"],
        "drug_keywords": ["아세트아미노펜", "타이레놀", "파라세타몰"],
        "severity": "danger",
        "description": "알코올과 아세트아미노펜을 병용하면 간독성 위험이 크게 증가합니다.",
        "mechanism": "알코올이 CYP2E1을 유도 → 아세트아미노펜의 독성 대사산물(NAPQI) 생성 증가 → 간세포 손상",
        "recommendation": "음주 시 아세트아미노펜을 복용하지 마세요. 만성 음주자는 1일 2g 이하로 제한.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 알코올 + 메트포르민 ───
    {
        "food_keywords": ["알코올", "술", "맥주", "소주", "와인"],
        "drug_keywords": ["메트포르민"],
        "severity": "warning",
        "description": "알코올과 메트포르민을 병용하면 젖산증(lactic acidosis) 위험이 증가합니다.",
        "mechanism": "알코올이 간의 젖산 대사를 억제 + 메트포르민의 젖산 생성 촉진 → 젖산증",
        "recommendation": "메트포르민 복용 중에는 음주를 피하거나 최소화하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 알코올 + 항우울제(SSRI) ───
    {
        "food_keywords": ["알코올", "술", "맥주", "소주", "와인"],
        "drug_keywords": ["플루옥세틴", "파록세틴", "세르트랄린", "에스시탈로프람", "시탈로프람"],
        "severity": "warning",
        "description": "알코올이 항우울제의 중추신경 억제 효과를 증폭시켜 과도한 졸음, 판단력 저하를 유발할 수 있습니다.",
        "mechanism": "중추신경계 억제 작용 상승 + 세로토닌 시스템 교란",
        "recommendation": "항우울제 복용 중에는 음주를 피하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 알코올 + 벤조디아제핀 ───
    {
        "food_keywords": ["알코올", "술", "맥주", "소주", "와인"],
        "drug_keywords": ["알프라졸람", "로라제팜", "디아제팜", "클로나제팜", "트리아졸람"],
        "severity": "danger",
        "description": "알코올과 벤조디아제핀을 병용하면 호흡 억제, 의식 저하 등 생명 위협적 부작용이 발생할 수 있습니다.",
        "mechanism": "GABA 수용체에 대한 중추신경 억제 작용 상승 → 호흡 억제, 과진정",
        "recommendation": "절대 병용하지 마세요. 사망 위험이 있습니다.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 감초 + 이뇨제 ───
    {
        "food_keywords": ["감초"],
        "drug_keywords": ["히드로클로로티아지드", "푸로세미드", "토라세미드", "클로르탈리돈"],
        "severity": "warning",
        "description": "감초의 글리시리진이 위알도스테론증을 유발하여 이뇨제에 의한 저칼륨혈증을 악화시킵니다.",
        "mechanism": "글리시리진이 11β-HSD2를 억제 → 코르티솔이 미네랄코르티코이드 수용체 활성화 → 나트륨 저류 + 칼륨 배설 촉진",
        "recommendation": "이뇨제 복용 중에는 감초 및 감초 함유 식품/음료를 피하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 감초 + 항고혈압제 ───
    {
        "food_keywords": ["감초"],
        "drug_keywords": ["에날라프릴", "리시노프릴", "암로디핀", "발사르탄", "로사르탄", "텔미사르탄"],
        "severity": "warning",
        "description": "감초가 나트륨 저류와 수분 저류를 유발하여 항고혈압제의 효과를 감소시킬 수 있습니다.",
        "mechanism": "위알도스테론증 → 나트륨/수분 저류 → 혈압 상승 → 항고혈압제 효과 상쇄",
        "recommendation": "항고혈압제 복용 중에는 감초 섭취를 피하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 크랜베리 + 와파린 ───
    {
        "food_keywords": ["크랜베리"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "warning",
        "description": "크랜베리주스가 와파린의 항응고 효과를 증강시켜 출혈 위험을 높일 수 있습니다.",
        "mechanism": "크랜베리의 플라보노이드가 CYP2C9를 억제 → 와파린 대사 저하 → INR 상승",
        "recommendation": "와파린 복용 중 크랜베리주스 대량 섭취를 피하세요. INR을 정기적으로 확인.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 세인트존스워트 + 다수 약물 ───
    {
        "food_keywords": ["세인트존스워트", "St. John's Wort"],
        "drug_keywords": ["사이클로스포린", "타크로리무스", "와파린", "워파린", "디곡신"],
        "severity": "danger",
        "description": "세인트존스워트가 CYP3A4 등 약물대사효소를 강력하게 유도하여 약물 혈중 농도를 급격히 낮춥니다.",
        "mechanism": "하이퍼포린이 PXR(pregnane X receptor)을 활성화 → CYP3A4, CYP2C9, P-gp 유도 → 약물 대사 촉진",
        "recommendation": "이 약물들과 세인트존스워트를 절대 병용하지 마세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 세인트존스워트 + SSRI ───
    {
        "food_keywords": ["세인트존스워트", "St. John's Wort"],
        "drug_keywords": ["플루옥세틴", "파록세틴", "세르트랄린", "에스시탈로프람"],
        "severity": "danger",
        "description": "세로토닌 증후군 위험. 세인트존스워트의 세로토닌 재흡수 억제 작용이 SSRI와 중첩됩니다.",
        "mechanism": "세로토닌 재흡수 억제 효과 중첩 → 세로토닌 과잉 축적 → 세로토닌 증후군",
        "recommendation": "절대 병용하지 마세요. 체온 상승, 근경직, 의식 변화 시 즉시 응급실.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 세인트존스워트 + 경구피임약 ───
    {
        "food_keywords": ["세인트존스워트", "St. John's Wort"],
        "drug_keywords": ["에티닐에스트라디올", "레보노르게스트렐", "드로스피레논"],
        "severity": "warning",
        "description": "세인트존스워트가 경구피임약의 대사를 촉진하여 피임 실패 위험이 있습니다.",
        "mechanism": "CYP3A4 유도 → 에스트로겐/프로게스틴 대사 촉진 → 혈중 농도 저하",
        "recommendation": "세인트존스워트 복용 중에는 추가 피임법을 사용하세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 두유/콩(이소플라본) + 갑상선약 ───
    {
        "food_keywords": ["두유", "두부", "콩", "대두"],
        "drug_keywords": ["레보티록신", "갑상선호르몬", "씬지로이드"],
        "severity": "caution",
        "description": "콩의 이소플라본이 레보티록신의 장 흡수를 저해하고 갑상선 호르몬 합성에 영향을 줄 수 있습니다.",
        "mechanism": "이소플라본이 갑상선 퍼옥시다제(TPO)를 억제 + 약물의 장 흡수 저해",
        "recommendation": "레보티록신 복용 후 최소 4시간 간격을 두고 콩 제품을 섭취하세요.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 마늘 + 항응고제 ───
    {
        "food_keywords": ["마늘"],
        "drug_keywords": ["와파린", "워파린", "클로피도그렐", "아스피린"],
        "severity": "caution",
        "description": "마늘의 항혈소판 작용으로 항응고제와 병용 시 출혈 위험이 증가할 수 있습니다.",
        "mechanism": "알리신/아조엔의 항혈소판 작용 + 피브리노겐 형성 억제",
        "recommendation": "고용량 마늘/마늘 보충제와 항응고제 병용 시 출혈 징후를 관찰하세요. 수술 2주 전 중단.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 생강 + 항응고제 ───
    {
        "food_keywords": ["생강"],
        "drug_keywords": ["와파린", "워파린", "클로피도그렐", "아스피린"],
        "severity": "caution",
        "description": "생강의 항혈소판 작용으로 항응고제와 병용 시 출혈 위험이 약간 증가할 수 있습니다.",
        "mechanism": "진저롤의 트롬복산 합성효소 억제 → 혈소판 응집 저해",
        "recommendation": "고용량 생강 섭취와 항응고제 병용 시 주의하세요.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 녹차 + 와파린 ───
    {
        "food_keywords": ["녹차", "말차"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "caution",
        "description": "녹차에 함유된 비타민K가 와파린의 항응고 효과를 감소시킬 수 있습니다.",
        "mechanism": "녹차의 비타민K1이 응고인자 합성을 촉진 → 와파린 효과 감소",
        "recommendation": "녹차 섭취량을 일정하게 유지하세요. 대량 음용을 피하세요.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 미역/다시마 + 갑상선약 ───
    {
        "food_keywords": ["미역", "다시마", "해조류", "김"],
        "drug_keywords": ["레보티록신", "갑상선호르몬"],
        "severity": "caution",
        "description": "해조류의 과량 요오드가 갑상선 기능에 영향을 주어 갑상선약의 용량 조절이 필요할 수 있습니다.",
        "mechanism": "과량 요오드 섭취 → 울프-차이코프 효과(갑상선 호르몬 합성 일시 억제) 또는 요드 유도 갑상선기능항진증",
        "recommendation": "갑상선 질환 치료 중 해조류 섭취량을 일정하게 유지하고, TSH를 정기적으로 확인하세요.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 감초 + 디곡신 ───
    {
        "food_keywords": ["감초"],
        "drug_keywords": ["디곡신", "디기톡신"],
        "severity": "danger",
        "description": "감초에 의한 저칼륨혈증이 디곡신의 심장 독성을 크게 증가시킵니다.",
        "mechanism": "감초 → 저칼륨혈증 → 디곡신의 Na⁺/K⁺ ATPase 억제 효과 증폭 → 부정맥",
        "recommendation": "디곡신 복용 중에는 감초를 절대 섭취하지 마세요.",
        "source": "evidence_based",
        "evidence_level": "established",
    },
    # ─── 후추(피페린) + CYP3A4 기질약물 ───
    {
        "food_keywords": ["후추", "흑후추", "피페린"],
        "drug_keywords": ["카르바마제핀", "페니토인"],
        "severity": "caution",
        "description": "후추의 피페린이 약물의 생체이용률을 높여 혈중 농도가 상승할 수 있습니다.",
        "mechanism": "피페린이 CYP3A4, CYP2D6를 억제하고 P-gp를 억제 → 약물 대사 저하 및 흡수 증가",
        "recommendation": "항경련제 복용 중 후추 대량 섭취에 주의하세요.",
        "source": "evidence_based",
        "evidence_level": "possible",
    },
    # ─── 강황/커큐민 + 항응고제 ───
    {
        "food_keywords": ["강황", "울금", "커큐민"],
        "drug_keywords": ["와파린", "워파린", "클로피도그렐", "아스피린"],
        "severity": "caution",
        "description": "커큐민의 항혈소판 및 항응고 작용으로 출혈 위험이 증가할 수 있습니다.",
        "mechanism": "커큐민이 트롬복산 합성 억제 + CYP1A2/CYP3A4 억제 → 항응고 효과 강화",
        "recommendation": "고용량 강황/커큐민 보충제와 항응고제 병용 시 출혈에 주의하세요.",
        "source": "evidence_based",
        "evidence_level": "possible",
    },
    # ─── 숯불구이 + CYP1A2 기질약물 ───
    {
        "food_keywords": ["숯불구이", "훈제", "바베큐"],
        "drug_keywords": ["클로자핀", "올란자핀", "테오필린"],
        "severity": "caution",
        "description": "숯불구이의 다환방향족탄화수소(PAH)가 CYP1A2를 유도하여 약물 대사를 촉진시킵니다.",
        "mechanism": "PAH → AhR 수용체 활성화 → CYP1A2 유도 → 약물 대사 촉진 → 혈중 농도 저하",
        "recommendation": "이 약물 복용 중 숯불구이 대량 섭취를 피하세요.",
        "source": "evidence_based",
        "evidence_level": "possible",
    },
    # ─── 계피 + 항응고제 ───
    {
        "food_keywords": ["계피", "시나몬"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "caution",
        "description": "계피의 쿠마린 성분이 항응고 작용을 가져 와파린 효과를 강화할 수 있습니다.",
        "mechanism": "천연 쿠마린의 항응고 작용 + CYP2A6 억제",
        "recommendation": "카시아 계피(쿠마린 고함량) 대량 섭취 시 주의. INR 모니터링 권장.",
        "source": "evidence_based",
        "evidence_level": "possible",
    },
    # ─── 인삼 + 항응고제 ───
    {
        "food_keywords": ["인삼", "인삼차"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "warning",
        "description": "인삼이 와파린의 효과를 감소시키거나 증가시켜 INR 변동을 유발할 수 있습니다.",
        "mechanism": "진세노사이드에 의한 CYP 효소 영향 + 항혈소판 작용 → INR 변동",
        "recommendation": "와파린 복용 중 인삼 섭취 시 INR을 자주 모니터링하세요.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
    # ─── 인삼 + 혈당강하제 ───
    {
        "food_keywords": ["인삼", "인삼차"],
        "drug_keywords": ["메트포르민", "글리메피리드", "글리벤클라미드", "글리클라지드"],
        "severity": "caution",
        "description": "인삼의 혈당 강하 작용이 당뇨약과 합쳐져 저혈당 위험이 증가할 수 있습니다.",
        "mechanism": "진세노사이드가 인슐린 감수성을 개선하고 인슐린 분비를 촉진",
        "recommendation": "병용 시 혈당을 자주 모니터링하세요.",
        "source": "evidence_based",
        "evidence_level": "probable",
    },
]

# 식품-영양제 상호작용 규칙
FOOD_SUPPLEMENT_RULES: list[dict] = [
    {
        "food_keywords": ["커피", "카페인", "녹차"],
        "supp_keywords": ["철분", "황산제일철", "헴철"],
        "severity": "caution",
        "description": "커피/녹차의 폴리페놀과 탄닌이 비헴철의 흡수를 저해합니다.",
        "mechanism": "폴리페놀-철 복합체 형성 → 철분 흡수율 최대 60% 감소",
        "recommendation": "철분 보충제와 커피/녹차는 최소 2시간 간격을 두고 섭취하세요.",
    },
    {
        "food_keywords": ["우유", "유제품", "치즈", "요거트"],
        "supp_keywords": ["철분", "황산제일철"],
        "severity": "caution",
        "description": "우유의 칼슘이 철분 흡수를 경쟁적으로 저해합니다.",
        "mechanism": "Ca²⁺와 Fe²⁺가 DMT1 수송체에서 경쟁",
        "recommendation": "철분 보충제와 유제품은 2시간 이상 간격을 두세요.",
    },
    {
        "food_keywords": ["감귤류", "레몬", "오렌지"],
        "supp_keywords": ["철분", "황산제일철"],
        "severity": "info",
        "description": "감귤류의 비타민C가 비헴철의 흡수를 촉진합니다.",
        "mechanism": "아스코르브산이 Fe³⁺를 Fe²⁺로 환원 → 흡수율 증가",
        "recommendation": "철분 보충제와 감귤류를 함께 섭취하면 흡수 효과가 좋습니다.",
    },
]


def match_keywords(text: str, keywords: list[str]) -> bool:
    """텍스트에 키워드 중 하나라도 포함되면 True."""
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def match_food(food_name: str, common_names_text: str, keywords: list[str]) -> bool:
    """식품 이름 또는 common_names에 키워드가 포함되면 True."""
    search_text = f"{food_name} {common_names_text or ''}"
    return match_keywords(search_text, keywords)


async def generate_interactions(dry_run: bool = False) -> dict[str, int]:
    """근거 기반 식품-약물/식품-영양제 상호작용을 생성한다."""
    stats = {"food_drug": 0, "food_supp": 0, "skipped_dup": 0}

    async with async_session_factory() as session:
        # 모든 식품 로드
        food_rows = await session.execute(text(
            "SELECT id, name, common_names::text FROM foods"
        ))
        foods = food_rows.fetchall()

        # 모든 약물 로드
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

        logger.info("식품 %d건, 약물 %d건, 영양제 %d건, 기존 evidence_based %d건",
                     len(foods), len(drugs), len(supplements), len(existing_ids))

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
                'evidence_based', :source_id, :evidence_level
            )
        """)

        # 식품-약물 상호작용 생성
        for rule in DRUG_FOOD_RULES:
            matched_foods = []
            for food_id, food_name, common_names_text in foods:
                if match_food(food_name, common_names_text, rule["food_keywords"]):
                    matched_foods.append((food_id, food_name))

            if not matched_foods:
                continue

            matched_drugs = []
            for drug_id, item_name, ingredients_text in drugs:
                search_text = f"{item_name} {ingredients_text or ''}"
                if match_keywords(search_text, rule["drug_keywords"]):
                    matched_drugs.append((drug_id, item_name))

            if not matched_drugs:
                continue

            for food_id, food_name in matched_foods:
                for drug_id, drug_name in matched_drugs:
                    source_id = f"EB_F{food_id}_D{drug_id}"
                    if source_id in existing_ids:
                        stats["skipped_dup"] += 1
                        continue

                    if not dry_run:
                        await session.execute(insert_sql, {
                            "a_type": "food",
                            "a_id": food_id,
                            "a_name": food_name,
                            "b_type": "drug",
                            "b_id": drug_id,
                            "b_name": drug_name,
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "mechanism": rule["mechanism"],
                            "recommendation": rule["recommendation"],
                            "source_id": source_id,
                            "evidence_level": rule.get("evidence_level", "established"),
                        })
                    existing_ids.add(source_id)
                    stats["food_drug"] += 1

            logger.info("규칙 [%s x %s]: 식품 %d x 약물 %d",
                         rule["food_keywords"][0], rule["drug_keywords"][0],
                         len(matched_foods), len(matched_drugs))

        # 식품-영양제 상호작용 생성
        for rule in FOOD_SUPPLEMENT_RULES:
            matched_foods = []
            for food_id, food_name, common_names_text in foods:
                if match_food(food_name, common_names_text, rule["food_keywords"]):
                    matched_foods.append((food_id, food_name))

            if not matched_foods:
                continue

            matched_supps = []
            for supp_id, product_name, main_ingredient in supplements:
                search_text = f"{product_name} {main_ingredient or ''}"
                if match_keywords(search_text, rule["supp_keywords"]):
                    matched_supps.append((supp_id, product_name))

            if not matched_supps:
                continue

            for food_id, food_name in matched_foods:
                for supp_id, supp_name in matched_supps:
                    source_id = f"EB_F{food_id}_S{supp_id}"
                    if source_id in existing_ids:
                        stats["skipped_dup"] += 1
                        continue

                    if not dry_run:
                        await session.execute(insert_sql, {
                            "a_type": "food",
                            "a_id": food_id,
                            "a_name": food_name,
                            "b_type": "supplement",
                            "b_id": supp_id,
                            "b_name": supp_name,
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "mechanism": rule["mechanism"],
                            "recommendation": rule["recommendation"],
                            "source_id": source_id,
                            "evidence_level": "probable",
                        })
                    existing_ids.add(source_id)
                    stats["food_supp"] += 1

        if not dry_run:
            await session.commit()

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="식품-약물 상호작용 생성")
    parser.add_argument("--dry-run", action="store_true", help="실제 DB 수정 없이 시뮬레이션")
    args = parser.parse_args()

    logger.info("식품-약물 상호작용 생성 시작 (dry_run=%s)", args.dry_run)
    stats = asyncio.run(generate_interactions(dry_run=args.dry_run))

    logger.info("=" * 60)
    logger.info("완료 — 식품-약물: %d건, 식품-영양제: %d건, 중복 건너뜀: %d건",
                stats["food_drug"], stats["food_supp"], stats["skipped_dup"])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
