"""한약재-약물 / 한약재-영양제 상호작용 생성 스크립트.

근거 기반(evidence_based) 상호작용 지식 베이스를 활용하여
DB의 실제 한약재/약물/영양제를 매칭하고 상호작용 레코드를 생성한다.

사용법:
    python -m scripts.data-import.generate_herbal_interactions
    python -m scripts.data-import.generate_herbal_interactions --dry-run
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
logger = logging.getLogger("gen_herbal_interactions")


# ============================================================
# 근거 기반 한약재-약물 상호작용 지식 베이스 (25+ 규칙)
# ============================================================

DRUG_HERBAL_RULES: list[dict] = [
    # ─── 인삼/홍삼 + 항응고제 ───
    {
        "herbal_keywords": ["인삼", "홍삼"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "warning",
        "description": "인삼/홍삼이 와파린의 항응고 효과를 변동시켜 INR 불안정을 유발할 수 있습니다.",
        "mechanism": "진세노사이드에 의한 CYP 효소 영향 + 항혈소판 작용 → INR 변동",
        "recommendation": "와파린 복용 중 인삼/홍삼 섭취 시 INR을 자주 모니터링하세요.",
        "evidence_level": "probable",
    },
    # ─── 인삼/홍삼 + 혈당강하제 ───
    {
        "herbal_keywords": ["인삼", "홍삼"],
        "drug_keywords": ["메트포르민", "글리메피리드", "글리벤클라미드", "글리클라지드"],
        "severity": "warning",
        "description": "인삼/홍삼의 혈당 강하 작용이 당뇨약과 합쳐져 저혈당 위험이 증가할 수 있습니다.",
        "mechanism": "진세노사이드가 인슐린 감수성 개선 및 인슐린 분비 촉진 → 혈당 과도 저하",
        "recommendation": "병용 시 혈당을 자주 모니터링하세요. 저혈당 증상(어지러움, 떨림, 발한)에 주의.",
        "evidence_level": "probable",
    },
    # ─── 감초 + 이뇨제 ───
    {
        "herbal_keywords": ["감초"],
        "drug_keywords": ["히드로클로로티아지드", "푸로세미드", "토라세미드", "클로르탈리돈"],
        "severity": "warning",
        "description": "감초의 글리시리진이 위알도스테론증을 유발하여 이뇨제에 의한 저칼륨혈증을 악화시킵니다.",
        "mechanism": "글리시리진 → 11β-HSD2 억제 → 코르티솔의 미네랄코르티코이드 활성 → 칼륨 배설 촉진",
        "recommendation": "감초 함유 처방과 이뇨제 병용 시 혈중 칼륨을 정기적으로 확인하세요.",
        "evidence_level": "established",
    },
    # ─── 감초 + 항고혈압제 ───
    {
        "herbal_keywords": ["감초"],
        "drug_keywords": ["에날라프릴", "리시노프릴", "암로디핀", "발사르탄", "로사르탄", "텔미사르탄"],
        "severity": "warning",
        "description": "감초가 나트륨/수분 저류를 유발하여 항고혈압제의 혈압 강하 효과를 감소시킵니다.",
        "mechanism": "위알도스테론증 → 나트륨/수분 저류 → 혈압 상승 → 항고혈압제 효과 상쇄",
        "recommendation": "항고혈압제 복용 중 감초 함유 처방 사용 시 혈압을 자주 확인하세요.",
        "evidence_level": "established",
    },
    # ─── 감초 + 디곡신(강심배당체) ───
    {
        "herbal_keywords": ["감초"],
        "drug_keywords": ["디곡신", "디기톡신"],
        "severity": "danger",
        "description": "감초에 의한 저칼륨혈증이 디곡신의 심장 독성을 크게 증가시킵니다. 부정맥 위험.",
        "mechanism": "감초 → 저칼륨혈증 → 심근 세포의 디곡신 감수성 증가 → 부정맥",
        "recommendation": "디곡신 복용 중에는 감초 함유 처방을 피하세요. 부득이 시 칼륨 모니터링 필수.",
        "evidence_level": "established",
    },
    # ─── 당귀 + 항응고제 ───
    {
        "herbal_keywords": ["당귀"],
        "drug_keywords": ["와파린", "워파린", "클로피도그렐", "아스피린"],
        "severity": "warning",
        "description": "당귀의 활혈 작용(쿠마린 유도체 함유)이 항응고제와 병용 시 출혈 위험을 증가시킵니다.",
        "mechanism": "데커신/데커시놀의 항혈소판 작용 + 쿠마린 유도체의 항응고 작용",
        "recommendation": "항응고제 복용 중 당귀 사용 시 출혈 징후를 주의하세요. 수술 전 2주 중단.",
        "evidence_level": "probable",
    },
    # ─── 마황 + MAO 억제제 ───
    {
        "herbal_keywords": ["마황"],
        "drug_keywords": ["모클로베마이드", "페넬진", "트라닐시프로민", "셀레길린", "라사길린"],
        "severity": "danger",
        "description": "마황의 에페드린과 MAO 억제제 병용 시 고혈압 위기, 뇌출혈 등 생명 위협적 부작용 발생 위험.",
        "mechanism": "MAO 억제로 에페드린 대사 차단 → 노르에피네프린 과잉 축적 → 급격한 혈압 상승",
        "recommendation": "절대 병용 금기. MAO 억제제 복용 중 및 중단 후 2주간 마황 사용 금지.",
        "evidence_level": "established",
    },
    # ─── 마황 + 교감신경흥분제 ───
    {
        "herbal_keywords": ["마황"],
        "drug_keywords": ["슈도에페드린", "페닐에프린", "메틸페니데이트", "암페타민"],
        "severity": "danger",
        "description": "마황과 교감신경흥분제를 병용하면 심혈관 부작용(빈맥, 고혈압, 부정맥)이 크게 증가합니다.",
        "mechanism": "교감신경 흥분 작용 중첩 → 심박수 증가, 혈압 상승, 부정맥 위험",
        "recommendation": "절대 병용하지 마세요. 심혈관 사고 위험.",
        "evidence_level": "established",
    },
    # ─── 마황 + 항고혈압제 ───
    {
        "herbal_keywords": ["마황"],
        "drug_keywords": ["에날라프릴", "리시노프릴", "암로디핀", "발사르탄", "로사르탄", "아테놀올", "프로프라놀올"],
        "severity": "warning",
        "description": "마황의 에페드린이 혈압을 높여 항고혈압제의 효과를 감소시킵니다.",
        "mechanism": "에페드린의 교감신경 흥분 → 혈압 상승 → 항고혈압제 효과 상쇄",
        "recommendation": "고혈압 환자는 마황 함유 처방 사용을 피하세요.",
        "evidence_level": "established",
    },
    # ─── 은행잎 + 항응고제/항혈소판제 ───
    {
        "herbal_keywords": ["은행잎"],
        "drug_keywords": ["와파린", "워파린", "아스피린", "클로피도그렐", "헤파린"],
        "severity": "warning",
        "description": "은행잎 추출물이 혈소판 활성화 인자(PAF)를 억제하여 출혈 위험을 증가시킵니다.",
        "mechanism": "징코라이드B의 PAF 억제 + 플라보노이드의 항혈소판 작용 → 출혈 시간 연장",
        "recommendation": "항응고제 복용 중 은행잎 사용 시 출혈에 주의. 수술 2주 전 중단.",
        "evidence_level": "established",
    },
    # ─── 대황 + 디곡신 ───
    {
        "herbal_keywords": ["대황"],
        "drug_keywords": ["디곡신", "디기톡신"],
        "severity": "warning",
        "description": "대황의 사하(瀉下) 작용으로 전해질 불균형(특히 저칼륨혈증)이 발생하여 디곡신 독성이 증가합니다.",
        "mechanism": "센노사이드에 의한 설사 → 칼륨 손실 → 저칼륨혈증 → 디곡신 독성 증가",
        "recommendation": "대황과 디곡신 병용 시 전해질(특히 칼륨)을 정기적으로 모니터링하세요.",
        "evidence_level": "probable",
    },
    # ─── 대황 + 이뇨제 ───
    {
        "herbal_keywords": ["대황"],
        "drug_keywords": ["히드로클로로티아지드", "푸로세미드", "토라세미드"],
        "severity": "caution",
        "description": "대황의 사하 작용과 이뇨제의 수분/전해질 배설이 합쳐져 탈수, 저칼륨혈증 위험이 증가합니다.",
        "mechanism": "설사에 의한 수분/전해질 손실 + 이뇨에 의한 손실 → 전해질 불균형",
        "recommendation": "병용 시 수분 섭취를 충분히 하고 전해질을 모니터링하세요.",
        "evidence_level": "probable",
    },
    # ─── 황기 + 면역억제제 ───
    {
        "herbal_keywords": ["황기"],
        "drug_keywords": ["사이클로스포린", "타크로리무스", "프레드니솔론", "메토트렉세이트"],
        "severity": "warning",
        "description": "황기의 면역 증강 작용이 면역억제제의 효과를 상쇄하여 이식 거부반응 등의 위험이 있습니다.",
        "mechanism": "황기의 아스트라갈로사이드IV가 T세포, NK세포를 활성화 → 면역억제제 효과 감소",
        "recommendation": "면역억제제 복용 중 황기 사용을 피하세요. 자가면역질환 환자도 주의.",
        "evidence_level": "probable",
    },
    # ─── 천마 + 항경련제 ───
    {
        "herbal_keywords": ["천마"],
        "drug_keywords": ["발프로산", "카르바마제핀", "페니토인", "라모트리진", "가바펜틴"],
        "severity": "caution",
        "description": "천마의 진정/항경련 작용이 항경련제와 합쳐져 과도한 진정 효과가 나타날 수 있습니다.",
        "mechanism": "가스트로딘의 GABA 수용체 조절 작용 + 항경련제의 중추신경 억제 → 진정 효과 상승",
        "recommendation": "병용 시 졸음, 현기증에 주의하세요. 운전 등 주의력이 필요한 활동을 피하세요.",
        "evidence_level": "possible",
    },
    # ─── 구기자 + 항응고제 ───
    {
        "herbal_keywords": ["구기자"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "caution",
        "description": "구기자가 와파린의 항응고 효과를 증강시켜 INR 상승 및 출혈 위험이 있습니다.",
        "mechanism": "구기자의 CYP2C9 억제 가능성 → 와파린 대사 저하 → INR 상승",
        "recommendation": "와파린 복용 중 구기자를 대량 섭취할 경우 INR을 확인하세요.",
        "evidence_level": "possible",
    },
    # ─── 오미자 + CYP3A4 기질약물 ───
    {
        "herbal_keywords": ["오미자"],
        "drug_keywords": ["사이클로스포린", "타크로리무스", "심바스타틴", "아토르바스타틴"],
        "severity": "warning",
        "description": "오미자의 리그난 성분이 CYP3A4를 억제하여 약물 혈중 농도를 높일 수 있습니다.",
        "mechanism": "쉬잔드린B 등 리그난이 CYP3A4, P-gp를 억제 → 약물 대사 저하",
        "recommendation": "CYP3A4 기질 약물과 오미자 병용 시 약물 농도 모니터링이 필요합니다.",
        "evidence_level": "probable",
    },
    # ─── 백작약/적작약 + 항응고제 ───
    {
        "herbal_keywords": ["작약", "백작약", "적작약"],
        "drug_keywords": ["와파린", "워파린", "아스피린", "클로피도그렐"],
        "severity": "caution",
        "description": "작약의 활혈 작용이 항응고제와 병용 시 출혈 위험을 약간 증가시킬 수 있습니다.",
        "mechanism": "페오니플로린의 항혈소판 작용",
        "recommendation": "항응고제 복용 중 작약 고용량 사용 시 출혈에 주의하세요.",
        "evidence_level": "possible",
    },
    # ─── 시호 + 면역억제제 ───
    {
        "herbal_keywords": ["시호"],
        "drug_keywords": ["사이클로스포린", "타크로리무스", "프레드니솔론"],
        "severity": "warning",
        "description": "시호의 사이코사포닌이 면역 조절/간보호 작용을 가져 면역억제제의 효과를 변동시킬 수 있습니다.",
        "mechanism": "사이코사포닌의 인터페론 유사 작용 + 면역 세포 활성화 → 면역억제 효과 감소 가능",
        "recommendation": "면역억제제 복용 중 시호 사용 시 약물 농도 및 면역 지표를 모니터링하세요.",
        "evidence_level": "possible",
    },
    # ─── 황금 + 항응고제 ───
    {
        "herbal_keywords": ["황금"],
        "drug_keywords": ["와파린", "워파린", "아스피린"],
        "severity": "caution",
        "description": "황금의 바이칼린이 항혈소판 작용을 가져 항응고제와 병용 시 출혈 위험이 있습니다.",
        "mechanism": "바이칼레인의 리폭시게나아제 억제 + 항혈소판 작용",
        "recommendation": "항응고제 복용 중 황금 고용량 사용 시 출혈에 주의하세요.",
        "evidence_level": "possible",
    },
    # ─── 황련(베르베린) + 사이클로스포린 ───
    {
        "herbal_keywords": ["황련"],
        "drug_keywords": ["사이클로스포린"],
        "severity": "warning",
        "description": "황련의 베르베린이 CYP3A4를 억제하여 사이클로스포린의 혈중 농도를 높일 수 있습니다.",
        "mechanism": "베르베린의 CYP3A4 억제 + P-gp 억제 → 사이클로스포린 대사 저하 + 흡수 증가",
        "recommendation": "사이클로스포린 복용 중 황련 사용 시 약물 농도를 면밀히 모니터링하세요.",
        "evidence_level": "probable",
    },
    # ─── 단삼 + 와파린 ───
    {
        "herbal_keywords": ["단삼"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "warning",
        "description": "단삼의 활혈거어 작용이 와파린과 합쳐져 출혈 위험을 증가시킵니다.",
        "mechanism": "탄시논의 항혈소판 작용 + 살비안올산의 항응고 작용 + CYP 억제",
        "recommendation": "와파린 복용 중 단삼 사용을 피하세요. 병용 시 INR 모니터링 필수.",
        "evidence_level": "probable",
    },
    # ─── 단삼 + 디곡신 ───
    {
        "herbal_keywords": ["단삼"],
        "drug_keywords": ["디곡신", "디기톡신"],
        "severity": "caution",
        "description": "단삼이 디곡신의 혈중 농도를 증가시킬 수 있습니다.",
        "mechanism": "단삼의 P-gp 억제 → 디곡신 배설 감소 → 혈중 농도 상승",
        "recommendation": "단삼과 디곡신 병용 시 디곡신 농도를 모니터링하세요.",
        "evidence_level": "possible",
    },
    # ─── 홍화 + 항응고제 ───
    {
        "herbal_keywords": ["홍화"],
        "drug_keywords": ["와파린", "워파린", "아스피린", "클로피도그렐"],
        "severity": "warning",
        "description": "홍화의 강력한 활혈 작용이 항응고제와 병용 시 출혈 위험을 크게 증가시킵니다.",
        "mechanism": "히드록시사플로르옐로우A의 항혈소판 작용 + 항응고 작용",
        "recommendation": "항응고제 복용 중 홍화 사용을 피하세요.",
        "evidence_level": "probable",
    },
    # ─── 산조인 + 진정제/수면제 ───
    {
        "herbal_keywords": ["산조인"],
        "drug_keywords": ["졸피뎀", "트리아졸람", "알프라졸람", "로라제팜", "디아제팜"],
        "severity": "caution",
        "description": "산조인의 진정 작용이 수면제/진정제와 합쳐져 과도한 졸음이 나타날 수 있습니다.",
        "mechanism": "주주보사이드A의 GABA 수용체 조절 → 진정 효과 상승",
        "recommendation": "병용 시 낮 시간 졸음, 현기증에 주의하세요. 용량 조절이 필요할 수 있습니다.",
        "evidence_level": "possible",
    },
    # ─── 갈근(칡) + 에스트로겐 약물 ───
    {
        "herbal_keywords": ["갈근"],
        "drug_keywords": ["에티닐에스트라디올", "에스트라디올", "타목시펜"],
        "severity": "caution",
        "description": "갈근의 이소플라본(푸에라린)이 에스트로겐 수용체에 작용하여 호르몬 약물과 상호작용 가능.",
        "mechanism": "식물성 에스트로겐이 에스트로겐 수용체에 경쟁적 결합 → 호르몬 효과 변동",
        "recommendation": "호르몬 관련 약물 복용 중 갈근 사용 시 의사와 상담하세요.",
        "evidence_level": "possible",
    },
    # ─── 반하 + 부자 (십팔반 — 전통 배합 금기) ───
    {
        "herbal_keywords": ["반하"],
        "drug_keywords": ["아코니틴"],
        "severity": "danger",
        "description": "반하와 부자(오두류)는 전통 의학에서 십팔반(十八反) 배합 금기입니다.",
        "mechanism": "아코니틴과 반하 알칼로이드의 독성 상승 작용",
        "recommendation": "전통 의학 원칙에 따라 반하와 부자류를 병용하지 마세요.",
        "evidence_level": "traditional",
    },
    # ─── 진피/귤피 + CYP 기질약물 ───
    {
        "herbal_keywords": ["진피", "귤피"],
        "drug_keywords": ["심바스타틴", "아토르바스타틴", "사이클로스포린"],
        "severity": "caution",
        "description": "진피의 감귤류 성분이 CYP3A4에 영향을 줄 수 있습니다.",
        "mechanism": "감귤류 플라보노이드의 CYP3A4 억제 가능성",
        "recommendation": "CYP3A4 기질 약물과 진피 고용량 병용 시 약물 농도에 주의하세요.",
        "evidence_level": "possible",
    },
    # ─── 계지 + 항응고제 ───
    {
        "herbal_keywords": ["계지"],
        "drug_keywords": ["와파린", "워파린"],
        "severity": "caution",
        "description": "계지의 쿠마린 성분이 항응고 작용을 가져 와파린 효과를 강화할 수 있습니다.",
        "mechanism": "천연 쿠마린의 항응고 작용",
        "recommendation": "와파린 복용 중 계지 함유 처방 사용 시 INR을 확인하세요.",
        "evidence_level": "possible",
    },
]

# ============================================================
# 한약재-영양제 상호작용 규칙
# ============================================================

SUPPLEMENT_HERBAL_RULES: list[dict] = [
    {
        "herbal_keywords": ["인삼", "홍삼"],
        "supp_keywords": ["오메가", "EPA", "DHA", "크릴오일"],
        "severity": "caution",
        "description": "인삼/홍삼의 항혈소판 작용과 오메가3의 혈소판 응집 억제 작용이 합쳐져 출혈 경향이 증가할 수 있습니다.",
        "mechanism": "양쪽 모두 항혈소판 작용 → 출혈 시간 연장",
        "recommendation": "고용량 병용 시 출혈 징후에 주의하세요.",
    },
    {
        "herbal_keywords": ["감초"],
        "supp_keywords": ["칼륨", "염화칼륨"],
        "severity": "caution",
        "description": "감초의 칼륨 배설 촉진 작용과 칼륨 보충제의 효과가 상충할 수 있습니다.",
        "mechanism": "감초 → 위알도스테론증 → 칼륨 배설 촉진 → 칼륨 보충 효과 감소",
        "recommendation": "감초 함유 처방 복용 중 칼륨 수치를 확인하세요.",
    },
    {
        "herbal_keywords": ["당귀"],
        "supp_keywords": ["은행잎", "징코"],
        "severity": "caution",
        "description": "당귀와 은행잎 모두 항혈소판 작용이 있어 병용 시 출혈 위험이 증가합니다.",
        "mechanism": "당귀의 쿠마린 유도체 + 은행잎의 PAF 억제 → 항혈소판 효과 상승",
        "recommendation": "출혈 징후에 주의하세요. 수술 전 2주간 모두 중단 권장.",
    },
    {
        "herbal_keywords": ["황기"],
        "supp_keywords": ["에키네시아"],
        "severity": "info",
        "description": "황기와 에키네시아 모두 면역 증강 작용이 있어 면역 반응이 과도하게 활성화될 수 있습니다.",
        "mechanism": "면역 세포(T세포, NK세포) 활성화 작용 중첩",
        "recommendation": "자가면역질환 환자는 병용을 피하세요. 건강한 사람에게는 시너지 가능.",
    },
    {
        "herbal_keywords": ["천마"],
        "supp_keywords": ["멜라토닌"],
        "severity": "caution",
        "description": "천마의 진정 작용과 멜라토닌의 수면 유도 작용이 합쳐져 과도한 졸음이 나타날 수 있습니다.",
        "mechanism": "중추신경 억제 작용 상승 → 과진정, 낮 시간 졸음",
        "recommendation": "병용 시 용량을 줄이고 낮 시간 졸음에 주의하세요.",
    },
    {
        "herbal_keywords": ["은행잎"],
        "supp_keywords": ["오메가", "EPA", "DHA"],
        "severity": "caution",
        "description": "은행잎과 오메가3 모두 항혈소판 작용이 있어 병용 시 출혈 위험이 증가할 수 있습니다.",
        "mechanism": "PAF 억제(은행잎) + 혈소판 응집 억제(오메가3) → 출혈 경향 증가",
        "recommendation": "수술 전 2주간 모두 중단 권장. 출혈 징후 관찰.",
    },
    {
        "herbal_keywords": ["인삼", "홍삼"],
        "supp_keywords": ["홍삼", "인삼", "진세노사이드"],
        "severity": "info",
        "description": "한약재 인삼과 영양제 홍삼을 동시에 복용하면 진세노사이드 과량 섭취가 될 수 있습니다.",
        "mechanism": "진세노사이드 중복 → 과량 시 불면, 불안, 고혈압 가능",
        "recommendation": "인삼/홍삼의 총 섭취량을 권장 범위 내로 유지하세요.",
    },
    {
        "herbal_keywords": ["산조인"],
        "supp_keywords": ["멜라토닌"],
        "severity": "caution",
        "description": "산조인과 멜라토닌 모두 수면 유도 작용이 있어 과도한 진정 효과 가능.",
        "mechanism": "GABA 수용체 조절(산조인) + 수면-각성 리듬 조절(멜라토닌) → 과진정",
        "recommendation": "병용 시 용량을 줄이세요. 아침 졸음에 주의.",
    },
    {
        "herbal_keywords": ["오미자"],
        "supp_keywords": ["밀크씨슬", "실리마린"],
        "severity": "info",
        "description": "오미자와 밀크씨슬 모두 간보호 작용이 있어 시너지 효과가 기대됩니다.",
        "mechanism": "쉬잔드린(오미자)과 실리마린(밀크씨슬) 모두 간세포 보호 + 항산화 작용",
        "recommendation": "간건강 목적으로 병용 가능. 단, 간질환 치료약 복용 중이라면 의사와 상담.",
    },
    {
        "herbal_keywords": ["하수오"],
        "supp_keywords": ["밀크씨슬", "실리마린"],
        "severity": "caution",
        "description": "하수오는 간독성 보고가 있으므로 밀크씨슬과 함께 복용하더라도 간 기능 모니터링이 필요합니다.",
        "mechanism": "하수오의 에모딘/안트라퀴논에 의한 간독성 가능 + 실리마린의 간보호",
        "recommendation": "하수오 복용 시 간 기능 검사를 정기적으로 받으세요.",
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
    """근거 기반 한약재-약물/한약재-영양제 상호작용을 생성한다."""
    stats = {"herbal_drug": 0, "herbal_supp": 0, "skipped_dup": 0}

    async with async_session_factory() as session:
        # 모든 한약재 로드
        herbal_rows = await session.execute(text(
            "SELECT id, name, korean_name FROM herbal_medicines"
        ))
        herbals = herbal_rows.fetchall()

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

        logger.info("한약재 %d건, 약물 %d건, 영양제 %d건, 기존 evidence_based %d건",
                     len(herbals), len(drugs), len(supplements), len(existing_ids))

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

        # 한약재-약물 상호작용 생성
        for rule in DRUG_HERBAL_RULES:
            matched_herbals = []
            for herbal_id, herbal_name, korean_name in herbals:
                search_text = f"{herbal_name} {korean_name or ''}"
                if match_keywords(search_text, rule["herbal_keywords"]):
                    matched_herbals.append((herbal_id, herbal_name))

            if not matched_herbals:
                continue

            matched_drugs = []
            for drug_id, item_name, ingredients_text in drugs:
                search_text = f"{item_name} {ingredients_text or ''}"
                if match_keywords(search_text, rule["drug_keywords"]):
                    matched_drugs.append((drug_id, item_name))

            if not matched_drugs:
                continue

            for herbal_id, herbal_name in matched_herbals:
                for drug_id, drug_name in matched_drugs:
                    source_id = f"EB_H{herbal_id}_D{drug_id}"
                    if source_id in existing_ids:
                        stats["skipped_dup"] += 1
                        continue

                    if not dry_run:
                        await session.execute(insert_sql, {
                            "a_type": "herbal",
                            "a_id": herbal_id,
                            "a_name": herbal_name,
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
                    stats["herbal_drug"] += 1

            logger.info("규칙 [%s x %s]: 한약재 %d x 약물 %d",
                         rule["herbal_keywords"][0], rule["drug_keywords"][0],
                         len(matched_herbals), len(matched_drugs))

        # 한약재-영양제 상호작용 생성
        for rule in SUPPLEMENT_HERBAL_RULES:
            matched_herbals = []
            for herbal_id, herbal_name, korean_name in herbals:
                search_text = f"{herbal_name} {korean_name or ''}"
                if match_keywords(search_text, rule["herbal_keywords"]):
                    matched_herbals.append((herbal_id, herbal_name))

            if not matched_herbals:
                continue

            matched_supps = []
            for supp_id, product_name, main_ingredient in supplements:
                search_text = f"{product_name} {main_ingredient or ''}"
                if match_keywords(search_text, rule["supp_keywords"]):
                    matched_supps.append((supp_id, product_name))

            if not matched_supps:
                continue

            for herbal_id, herbal_name in matched_herbals:
                for supp_id, supp_name in matched_supps:
                    source_id = f"EB_H{herbal_id}_S{supp_id}"
                    if source_id in existing_ids:
                        stats["skipped_dup"] += 1
                        continue

                    if not dry_run:
                        await session.execute(insert_sql, {
                            "a_type": "herbal",
                            "a_id": herbal_id,
                            "a_name": herbal_name,
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
                    stats["herbal_supp"] += 1

        if not dry_run:
            await session.commit()

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="한약재-약물/영양제 상호작용 생성")
    parser.add_argument("--dry-run", action="store_true", help="실제 DB 수정 없이 시뮬레이션")
    args = parser.parse_args()

    logger.info("한약재 상호작용 생성 시작 (dry_run=%s)", args.dry_run)
    stats = asyncio.run(generate_interactions(dry_run=args.dry_run))

    logger.info("=" * 60)
    logger.info("완료 — 한약재-약물: %d건, 한약재-영양제: %d건, 중복 건너뜀: %d건",
                stats["herbal_drug"], stats["herbal_supp"], stats["skipped_dup"])
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
