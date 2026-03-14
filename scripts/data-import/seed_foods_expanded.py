"""식품 확장 시드 데이터 적재 스크립트.

기존 seed_foods.py의 79종을 보완하여 ~170종 NEW 식품을 추가한다.
(기존 slug과 중복 없음 — ON CONFLICT (slug) DO NOTHING 안전장치 포함)

카테고리: 과일, 채소, 해산물, 육류, 곡류, 유제품, 음료, 발효식품, 조미료/향신료, 견과류, 기타

사용법:
    python -m scripts.data-import.seed_foods_expanded
    python -m scripts.data-import.seed_foods_expanded --dry-run
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text

from src.backend.core.database import async_session_factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("seed_foods_expanded")


# ============================================================
# 확장 식품 시드 데이터 (~170종, 기존 79종과 중복 없음)
# ============================================================

FOODS_EXPANDED: list[dict[str, Any]] = [
    # ══════════════════════════════════════════════════════════
    # ── 과일 (+15) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "블루베리",
        "slug": "food-blueberry",
        "category": "과일",
        "description": "안토시아닌이 풍부한 항산화 과일. CYP3A4 경미한 억제 가능성이 보고되어 일부 약물 대사에 영향을 줄 수 있음",
        "common_names": ["블루베리", "blueberry"],
        "nutrients": [{"name": "안토시아닌", "note": "CYP3A4 경미한 억제 가능"}, {"name": "비타민C", "note": "항산화"}, {"name": "프테로스틸벤", "note": "항산화"}],
    },
    {
        "name": "라즈베리",
        "slug": "food-raspberry",
        "category": "과일",
        "description": "엘라그산이 풍부하여 CYP 효소에 경미한 영향 가능. 식이섬유가 약물 흡수를 지연시킬 수 있음",
        "common_names": ["라즈베리", "산딸기", "raspberry"],
        "nutrients": [{"name": "엘라그산", "note": "CYP 효소 영향"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "딸기",
        "slug": "food-strawberry",
        "category": "과일",
        "description": "비타민C가 풍부하여 철분 흡수를 촉진. 옥살산 함유로 칼슘 관련 약물과 킬레이트 형성 가능",
        "common_names": ["딸기", "strawberry"],
        "nutrients": [{"name": "비타민C", "note": "철분 흡수 촉진"}, {"name": "옥살산", "note": "칼슘 킬레이트"}, {"name": "피세틴", "note": "항산화"}],
    },
    {
        "name": "사과",
        "slug": "food-apple",
        "category": "과일",
        "description": "펙틴이 풍부하여 일부 약물의 흡수를 지연시킬 수 있음. 사과주스는 OATP 수송체를 억제하여 펙소페나딘 등 약물 흡수 감소",
        "common_names": ["사과", "apple", "사과주스"],
        "nutrients": [{"name": "펙틴", "note": "약물 흡수 지연"}, {"name": "퀘르세틴", "note": "CYP 효소 영향"}, {"name": "플로리진", "note": "SGLT 억제"}],
    },
    {
        "name": "배",
        "slug": "food-pear",
        "category": "과일",
        "description": "식이섬유와 소르비톨이 풍부하여 일부 약물 흡수에 영향. 칼륨 함유",
        "common_names": ["배", "pear"],
        "nutrients": [{"name": "소르비톨", "note": "삼투성 완하 작용"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "복숭아",
        "slug": "food-peach",
        "category": "과일",
        "description": "칼륨이 풍부하여 칼륨보존이뇨제, ACE 억제제 복용자 대량 섭취 시 주의",
        "common_names": ["복숭아", "peach", "백도", "황도"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 190mg"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "자두",
        "slug": "food-plum",
        "category": "과일",
        "description": "소르비톨 함유로 완하 작용. 건자두(프룬)는 비타민K를 함유하여 와파린과 상호작용 가능",
        "common_names": ["자두", "프룬", "plum", "prune"],
        "nutrients": [{"name": "소르비톨", "note": "완하 작용"}, {"name": "비타민K", "note": "건자두에 함유"}, {"name": "칼륨", "note": "전해질"}],
    },
    {
        "name": "체리",
        "slug": "food-cherry",
        "category": "과일",
        "description": "안토시아닌이 풍부. 타르트체리는 멜라토닌을 함유하여 진정제, 수면제와 상가 작용 가능",
        "common_names": ["체리", "버찌", "cherry", "타르트체리"],
        "nutrients": [{"name": "안토시아닌", "note": "항산화·항염"}, {"name": "멜라토닌", "note": "타르트체리에 함유, 수면제 상가"}],
    },
    {
        "name": "파인애플",
        "slug": "food-pineapple",
        "category": "과일",
        "description": "브로멜라인(단백질 분해효소)이 항혈소판 작용을 하여 항응고제 병용 시 출혈 위험 증가",
        "common_names": ["파인애플", "pineapple"],
        "nutrients": [{"name": "브로멜라인", "note": "항혈소판·항염 작용"}, {"name": "망간", "note": "미네랄"}],
    },
    {
        "name": "파파야",
        "slug": "food-papaya",
        "category": "과일",
        "description": "파파인(단백질 분해효소)이 와파린의 항응고 효과를 증강시킬 수 있음. INR 상승 보고",
        "common_names": ["파파야", "papaya"],
        "nutrients": [{"name": "파파인", "note": "와파린 INR 상승 보고"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "무화과",
        "slug": "food-fig",
        "category": "과일",
        "description": "칼륨과 식이섬유가 풍부. 건무화과는 비타민K를 함유하여 와파린 복용자 주의",
        "common_names": ["무화과", "fig"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 232mg"}, {"name": "비타민K", "note": "건조 시 농축"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "감",
        "slug": "food-persimmon",
        "category": "과일",
        "description": "탄닌이 풍부하여 철분제 흡수를 저해. 식이섬유가 약물 흡수에 영향 가능",
        "common_names": ["감", "곶감", "persimmon", "단감"],
        "nutrients": [{"name": "탄닌", "note": "철분 흡수 저해"}, {"name": "베타카로틴", "note": "비타민A 전구체"}],
    },
    {
        "name": "대추",
        "slug": "food-jujube",
        "category": "과일",
        "description": "사포닌과 플라보노이드 함유. 진정 작용이 있어 수면제, 항불안제와 상가 작용 가능",
        "common_names": ["대추", "jujube", "홍대추"],
        "nutrients": [{"name": "사포닌", "note": "진정 작용"}, {"name": "플라보노이드", "note": "항산화"}, {"name": "비타민C", "note": "건조 시 감소"}],
    },
    {
        "name": "멜론",
        "slug": "food-melon",
        "category": "과일",
        "description": "칼륨이 풍부하여 칼륨보존이뇨제, ACE 억제제와 병용 시 고칼륨혈증 주의",
        "common_names": ["멜론", "참외", "melon", "cantaloupe"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 267mg"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "코코넛",
        "slug": "food-coconut",
        "category": "과일",
        "description": "중쇄지방산(MCT)이 풍부하여 지용성 약물 흡수에 영향. 칼륨 함유",
        "common_names": ["코코넛", "coconut", "야자"],
        "nutrients": [{"name": "중쇄지방산(MCT)", "note": "지용성 약물 흡수 영향"}, {"name": "칼륨", "note": "전해질"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 채소 (+25) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "마늘쫑",
        "slug": "food-garlic-scape",
        "category": "채소",
        "description": "마늘과 유사한 황화합물을 함유하여 항혈소판 작용. 항응고제 병용 시 출혈 위험 증가 가능",
        "common_names": ["마늘쫑", "마늘종", "garlic scape"],
        "nutrients": [{"name": "알리신", "note": "항혈소판 작용"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "배추",
        "slug": "food-napa-cabbage",
        "category": "채소",
        "description": "비타민K를 함유한 십자화과 채소. 와파린 복용자 섭취량 일정 유지 권장. 고이트로겐 미량 함유",
        "common_names": ["배추", "napa cabbage", "Chinese cabbage"],
        "nutrients": [{"name": "비타민K", "note": "100g당 약 43μg"}, {"name": "고이트로겐", "note": "갑상선 영향(미량)"}],
    },
    {
        "name": "무",
        "slug": "food-radish",
        "category": "채소",
        "description": "이소티오시아네이트가 CYP 효소에 영향을 줄 수 있음. 십자화과 채소로 갑상선 기능 관련 주의",
        "common_names": ["무", "radish", "무우"],
        "nutrients": [{"name": "이소티오시아네이트", "note": "CYP 효소 영향"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "콩나물",
        "slug": "food-bean-sprout",
        "category": "채소",
        "description": "비타민C와 아스파라긴산이 풍부. 이소플라본 미량 함유로 에스트로겐 관련 약물 주의",
        "common_names": ["콩나물", "bean sprout", "숙주나물"],
        "nutrients": [{"name": "비타민C", "note": "항산화"}, {"name": "이소플라본", "note": "미량, 식물성 에스트로겐"}, {"name": "아스파라긴산", "note": "해독 작용"}],
    },
    {
        "name": "숙주",
        "slug": "food-mung-bean-sprout",
        "category": "채소",
        "description": "녹두에서 발아한 채소. 칼륨 함유로 칼륨 관련 약물 복용자 주의",
        "common_names": ["숙주", "숙주나물", "mung bean sprout"],
        "nutrients": [{"name": "칼륨", "note": "전해질"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "고추냉이 (와사비)",
        "slug": "food-wasabi",
        "category": "채소",
        "description": "이소티오시아네이트가 풍부하여 CYP 효소 억제 가능. 항혈소판 작용 보고",
        "common_names": ["와사비", "고추냉이", "wasabi"],
        "nutrients": [{"name": "알릴이소티오시아네이트", "note": "CYP 억제·항혈소판"}, {"name": "6-MITC", "note": "항염 성분"}],
    },
    {
        "name": "미나리",
        "slug": "food-water-parsley",
        "category": "채소",
        "description": "비타민K가 풍부한 한국 전통 채소. 와파린 복용자 과량 섭취 주의. 해독 작용",
        "common_names": ["미나리", "water parsley", "water dropwort"],
        "nutrients": [{"name": "비타민K", "note": "고함량"}, {"name": "퀘르세틴", "note": "항산화"}, {"name": "이소람네틴", "note": "해독"}],
    },
    {
        "name": "쑥갓",
        "slug": "food-crown-daisy",
        "category": "채소",
        "description": "비타민K와 베타카로틴이 풍부. 와파린 복용자 주의. 특유의 향 성분이 진정 작용",
        "common_names": ["쑥갓", "crown daisy", "chrysanthemum greens"],
        "nutrients": [{"name": "비타민K", "note": "와파린 길항"}, {"name": "베타카로틴", "note": "비타민A 전구체"}],
    },
    {
        "name": "시래기",
        "slug": "food-dried-radish-leaves",
        "category": "채소",
        "description": "비타민K와 칼슘이 풍부한 건조 무청. 와파린 복용자 주의. 식이섬유가 약물 흡수 지연",
        "common_names": ["시래기", "무청", "dried radish leaves"],
        "nutrients": [{"name": "비타민K", "note": "건조 시 농축"}, {"name": "칼슘", "note": "식물성 칼슘"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "비트",
        "slug": "food-beet",
        "category": "채소",
        "description": "질산염이 풍부하여 체내 산화질소로 전환되어 혈압강하제와 저혈압 상가 작용 가능",
        "common_names": ["비트", "비트루트", "beet", "beetroot"],
        "nutrients": [{"name": "질산염", "note": "산화질소 → 혈압 강하"}, {"name": "베타인", "note": "간 보호"}, {"name": "옥살산", "note": "칼슘 킬레이트"}],
    },
    {
        "name": "우엉",
        "slug": "food-burdock",
        "category": "채소",
        "description": "이눌린(프리바이오틱스) 함유. 이뇨 작용이 있어 리튬 약물 농도에 영향 가능. 혈당 강하 작용",
        "common_names": ["우엉", "burdock", "우엉뿌리"],
        "nutrients": [{"name": "이눌린", "note": "프리바이오틱스"}, {"name": "아르크티제닌", "note": "항염·혈당 강하"}],
    },
    {
        "name": "연근",
        "slug": "food-lotus-root",
        "category": "채소",
        "description": "탄닌과 식이섬유가 풍부하여 철분제 및 일부 약물의 흡수를 저해할 수 있음",
        "common_names": ["연근", "lotus root"],
        "nutrients": [{"name": "탄닌", "note": "철분 흡수 저해"}, {"name": "비타민C", "note": "항산화"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "더덕",
        "slug": "food-deodeok",
        "category": "채소",
        "description": "사포닌이 풍부한 한국 전통 산채. 혈당 강하 및 면역 조절 작용으로 당뇨약, 면역억제제와 상호작용 가능",
        "common_names": ["더덕", "deodeok", "codonopsis lanceolata"],
        "nutrients": [{"name": "사포닌", "note": "혈당 강하·면역 조절"}, {"name": "이눌린", "note": "프리바이오틱스"}],
    },
    {
        "name": "도라지",
        "slug": "food-bellflower-root",
        "category": "채소",
        "description": "사포닌(플라티코딘)이 풍부. 거담 작용. 면역 조절 효과로 면역억제제와 상호작용 가능",
        "common_names": ["도라지", "bellflower root", "platycodon"],
        "nutrients": [{"name": "플라티코딘", "note": "거담·면역 조절"}, {"name": "이눌린", "note": "프리바이오틱스"}],
    },
    {
        "name": "치커리",
        "slug": "food-chicory",
        "category": "채소",
        "description": "이눌린이 풍부한 프리바이오틱스 식품. 약물 흡수를 지연시킬 수 있음. CYP1A2 영향 보고",
        "common_names": ["치커리", "chicory", "엔다이브"],
        "nutrients": [{"name": "이눌린", "note": "프리바이오틱스, 약물 흡수 지연"}, {"name": "락투신", "note": "진정 작용"}],
    },
    {
        "name": "루꼴라",
        "slug": "food-arugula",
        "category": "채소",
        "description": "비타민K를 함유한 십자화과 채소. 와파린 복용자 주의. 이소티오시아네이트 함유",
        "common_names": ["루꼴라", "아루굴라", "로켓", "arugula", "rocket"],
        "nutrients": [{"name": "비타민K", "note": "100g당 약 109μg"}, {"name": "이소티오시아네이트", "note": "CYP 영향"}],
    },
    {
        "name": "고춧잎",
        "slug": "food-pepper-leaf",
        "category": "채소",
        "description": "비타민K와 플라보노이드가 풍부. 와파린 복용자 과량 섭취 시 주의",
        "common_names": ["고춧잎", "pepper leaf"],
        "nutrients": [{"name": "비타민K", "note": "고함량"}, {"name": "루테올린", "note": "항산화·항염"}],
    },
    {
        "name": "호박",
        "slug": "food-pumpkin",
        "category": "채소",
        "description": "베타카로틴이 풍부하여 비타민A 보충제와 중복 주의. 칼륨 함유",
        "common_names": ["호박", "단호박", "늙은호박", "pumpkin", "squash"],
        "nutrients": [{"name": "베타카로틴", "note": "비타민A 전구체"}, {"name": "칼륨", "note": "전해질"}],
    },
    {
        "name": "가지",
        "slug": "food-eggplant",
        "category": "채소",
        "description": "나스닌(안토시아닌) 함유. 솔라닌 미량 함유로 콜린에스테라제 억제 가능성",
        "common_names": ["가지", "eggplant", "aubergine"],
        "nutrients": [{"name": "나스닌", "note": "안토시아닌 항산화"}, {"name": "솔라닌", "note": "미량, 콜린에스테라제 억제 가능"}],
    },
    {
        "name": "피망/파프리카",
        "slug": "food-bell-pepper",
        "category": "채소",
        "description": "비타민C가 매우 풍부하여 철분 흡수를 촉진. 비타민C 대량 섭취 시 에스트로겐 약물 혈중 농도 변화 가능",
        "common_names": ["피망", "파프리카", "bell pepper"],
        "nutrients": [{"name": "비타민C", "note": "100g당 약 128mg"}, {"name": "베타카로틴", "note": "적색 파프리카"}],
    },
    {
        "name": "옥수수",
        "slug": "food-corn",
        "category": "채소",
        "description": "식이섬유가 풍부하여 약물 흡수를 지연시킬 수 있음. 옥수수수염은 이뇨 작용",
        "common_names": ["옥수수", "corn", "maize"],
        "nutrients": [{"name": "식이섬유", "note": "약물 흡수 지연"}, {"name": "제아잔틴", "note": "항산화"}],
    },
    {
        "name": "표고버섯",
        "slug": "food-shiitake",
        "category": "채소",
        "description": "렌티난(베타글루칸) 함유로 면역 자극 작용. 면역억제제(사이클로스포린 등)와 상호작용 가능",
        "common_names": ["표고버섯", "표고", "shiitake"],
        "nutrients": [{"name": "렌티난", "note": "면역 자극"}, {"name": "에리타데닌", "note": "콜레스테롤 저하"}],
    },
    {
        "name": "양송이버섯",
        "slug": "food-button-mushroom",
        "category": "채소",
        "description": "CYP19(아로마타제) 억제 작용 보고. 에스트로겐 관련 약물과 상호작용 가능",
        "common_names": ["양송이", "양송이버섯", "button mushroom"],
        "nutrients": [{"name": "에르고스테롤", "note": "비타민D 전구체"}, {"name": "아로마타제 억제 성분", "note": "에스트로겐 대사 영향"}],
    },
    {
        "name": "느타리버섯",
        "slug": "food-oyster-mushroom",
        "category": "채소",
        "description": "베타글루칸 함유로 면역 조절 작용. 콜레스테롤 저하 효과로 스타틴과 상가 작용 가능",
        "common_names": ["느타리", "느타리버섯", "oyster mushroom"],
        "nutrients": [{"name": "베타글루칸", "note": "면역 조절"}, {"name": "로바스타틴", "note": "천연 스타틴 미량"}],
    },
    {
        "name": "팽이버섯",
        "slug": "food-enoki-mushroom",
        "category": "채소",
        "description": "식이섬유가 풍부하여 약물 흡수를 지연시킬 수 있음. 면역 조절 작용",
        "common_names": ["팽이버섯", "팽이", "enoki mushroom"],
        "nutrients": [{"name": "식이섬유", "note": "약물 흡수 지연"}, {"name": "베타글루칸", "note": "면역 조절"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 해산물 (+20) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "연어",
        "slug": "food-salmon",
        "category": "해산물",
        "description": "오메가3(EPA/DHA)가 매우 풍부하여 항응고제, 항혈소판제 병용 시 출혈 위험 증가. 비타민D 고함량",
        "common_names": ["연어", "salmon", "훈제연어"],
        "nutrients": [{"name": "오메가3(EPA/DHA)", "note": "항혈소판 작용"}, {"name": "비타민D", "note": "100g당 약 11μg"}, {"name": "아스타잔틴", "note": "항산화"}],
    },
    {
        "name": "삼치",
        "slug": "food-spanish-mackerel",
        "category": "해산물",
        "description": "오메가3 풍부. 히스타민 생성 가능 어종으로 항히스타민제 효과 감소 가능. 수은 함량 주의",
        "common_names": ["삼치", "spanish mackerel"],
        "nutrients": [{"name": "오메가3", "note": "EPA/DHA"}, {"name": "히스타민", "note": "신선도 저하 시 생성"}],
    },
    {
        "name": "꽁치",
        "slug": "food-pacific-saury",
        "category": "해산물",
        "description": "오메가3 풍부한 등푸른생선. 히스타민 생성 가능. 항응고제 병용 시 출혈 위험",
        "common_names": ["꽁치", "pacific saury", "sanma"],
        "nutrients": [{"name": "오메가3", "note": "EPA/DHA"}, {"name": "비타민D", "note": "고함량"}, {"name": "히스타민", "note": "신선도 저하 시"}],
    },
    {
        "name": "가자미",
        "slug": "food-flatfish",
        "category": "해산물",
        "description": "저지방 고단백 흰살 생선. 비타민D 함유. 약물 상호작용은 상대적으로 적으나 비타민D 보충제와 중복 주의",
        "common_names": ["가자미", "광어", "flatfish", "flounder"],
        "nutrients": [{"name": "비타민D", "note": "미량"}, {"name": "셀레늄", "note": "항산화 미네랄"}],
    },
    {
        "name": "대구",
        "slug": "food-cod",
        "category": "해산물",
        "description": "저지방 고단백. 대구간유는 비타민A·D가 극히 풍부하여 비타민 과잉 보충 위험",
        "common_names": ["대구", "cod", "대구간유"],
        "nutrients": [{"name": "비타민D", "note": "간유에 고함량"}, {"name": "비타민A", "note": "간유에 고함량"}, {"name": "셀레늄", "note": "항산화"}],
    },
    {
        "name": "오징어",
        "slug": "food-squid",
        "category": "해산물",
        "description": "타우린이 풍부. 콜레스테롤 함량이 높아 스타틴 복용자 대량 섭취 시 약효 감소 가능",
        "common_names": ["오징어", "squid"],
        "nutrients": [{"name": "타우린", "note": "간 보호·해독"}, {"name": "콜레스테롤", "note": "고함량"}],
    },
    {
        "name": "문어",
        "slug": "food-octopus",
        "category": "해산물",
        "description": "타우린이 매우 풍부. 철분과 아연 함유. 미네랄 관련 약물 흡수에 영향 가능",
        "common_names": ["문어", "octopus"],
        "nutrients": [{"name": "타우린", "note": "간 보호"}, {"name": "아연", "note": "미네랄"}, {"name": "철분", "note": "헴철"}],
    },
    {
        "name": "바지락",
        "slug": "food-clam",
        "category": "해산물",
        "description": "철분과 비타민B12가 풍부. 철분제와 병용 시 과잉 섭취 주의",
        "common_names": ["바지락", "조개", "clam"],
        "nutrients": [{"name": "헴철", "note": "고흡수율 철분"}, {"name": "비타민B12", "note": "고함량"}, {"name": "아연", "note": "미네랄"}],
    },
    {
        "name": "홍합",
        "slug": "food-mussel",
        "category": "해산물",
        "description": "오메가3와 철분이 풍부. 항응고제 병용 시 출혈 위험. 요오드 함유",
        "common_names": ["홍합", "mussel", "담치"],
        "nutrients": [{"name": "오메가3", "note": "항혈소판"}, {"name": "철분", "note": "헴철"}, {"name": "요오드", "note": "갑상선 영향"}],
    },
    {
        "name": "굴",
        "slug": "food-oyster",
        "category": "해산물",
        "description": "아연이 극히 풍부하여 아연 보충제와 과잉 섭취 위험. 테트라사이클린 계열 항생제 흡수 저해",
        "common_names": ["굴", "석화", "oyster"],
        "nutrients": [{"name": "아연", "note": "100g당 약 16mg, 항생제 킬레이트"}, {"name": "철분", "note": "헴철"}, {"name": "구리", "note": "미량원소"}],
    },
    {
        "name": "전복",
        "slug": "food-abalone",
        "category": "해산물",
        "description": "타우린과 미네랄이 풍부. 철분·아연 함유로 일부 항생제 흡수에 영향 가능",
        "common_names": ["전복", "abalone"],
        "nutrients": [{"name": "타우린", "note": "간 보호"}, {"name": "셀레늄", "note": "항산화"}, {"name": "아연", "note": "미네랄"}],
    },
    {
        "name": "게",
        "slug": "food-crab",
        "category": "해산물",
        "description": "키토산(껍질)이 지방과 약물의 흡수를 방해할 수 있음. 콜레스테롤 함유",
        "common_names": ["게", "꽃게", "대게", "crab"],
        "nutrients": [{"name": "키토산", "note": "지방·약물 흡수 저해"}, {"name": "아스타잔틴", "note": "항산화"}, {"name": "구리", "note": "미량원소"}],
    },
    {
        "name": "멍게",
        "slug": "food-sea-squirt",
        "category": "해산물",
        "description": "신시올 등 독특한 불포화 알코올 함유. 항산화 작용. 약물 상호작용 연구는 제한적",
        "common_names": ["멍게", "sea squirt", "우렁쉥이"],
        "nutrients": [{"name": "신시올", "note": "항산화"}, {"name": "바나듐", "note": "미량원소, 혈당 영향 가능"}],
    },
    {
        "name": "해삼",
        "slug": "food-sea-cucumber",
        "category": "해산물",
        "description": "사포닌과 콘드로이틴 함유. 항응고 작용이 보고되어 와파린 등 항응고제와 상가 작용 주의",
        "common_names": ["해삼", "sea cucumber"],
        "nutrients": [{"name": "사포닌", "note": "항응고 작용"}, {"name": "콘드로이틴", "note": "관절 건강"}, {"name": "글리코사미노글리칸", "note": "헤파린 유사 작용"}],
    },
    {
        "name": "파래",
        "slug": "food-green-laver",
        "category": "해산물",
        "description": "요오드와 철분이 풍부. 갑상선약(레보티록신) 복용자 과량 섭취 시 갑상선 기능 변화 주의",
        "common_names": ["파래", "green laver"],
        "nutrients": [{"name": "요오드", "note": "갑상선 영향"}, {"name": "철분", "note": "비헴철"}, {"name": "마그네슘", "note": "미네랄"}],
    },
    {
        "name": "매생이",
        "slug": "food-maesaengi",
        "category": "해산물",
        "description": "칼슘과 철분이 풍부한 해조류. 항생제(퀴놀론, 테트라사이클린) 흡수를 저해할 수 있음",
        "common_names": ["매생이", "maesaengi", "capsosiphon fulvescens"],
        "nutrients": [{"name": "칼슘", "note": "항생제 킬레이트"}, {"name": "철분", "note": "비헴철"}],
    },
    {
        "name": "톳",
        "slug": "food-hijiki",
        "category": "해산물",
        "description": "요오드와 칼슘이 풍부한 해조류. 무기비소 함량이 높을 수 있어 과량 섭취 주의. 갑상선약 상호작용",
        "common_names": ["톳", "hijiki"],
        "nutrients": [{"name": "요오드", "note": "갑상선약 상호작용"}, {"name": "칼슘", "note": "고함량"}, {"name": "무기비소", "note": "과량 주의"}],
    },
    {
        "name": "멸치",
        "slug": "food-anchovy",
        "category": "해산물",
        "description": "칼슘이 매우 풍부(뼈째 섭취). 히스타민 생성 가능. 퓨린 함량이 높아 통풍약과 상호작용",
        "common_names": ["멸치", "anchovy"],
        "nutrients": [{"name": "칼슘", "note": "뼈째 섭취 시 고함량"}, {"name": "퓨린", "note": "요산 상승, 통풍약 길항"}, {"name": "히스타민", "note": "신선도 저하 시"}],
    },
    {
        "name": "장어",
        "slug": "food-eel",
        "category": "해산물",
        "description": "비타민A가 극히 풍부하여 비타민A 보충제와 과잉 위험. 오메가3 함유",
        "common_names": ["장어", "뱀장어", "민물장어", "eel"],
        "nutrients": [{"name": "비타민A(레티놀)", "note": "과잉 섭취 위험"}, {"name": "오메가3", "note": "EPA/DHA"}, {"name": "비타민D", "note": "고함량"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 육류/계란 (+10) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "닭고기",
        "slug": "food-chicken",
        "category": "육류",
        "description": "고단백 식품. 나이아신(비타민B3) 풍부. 고단백 식이는 일부 약물(레보도파) 흡수를 저해할 수 있음",
        "common_names": ["닭고기", "chicken", "닭가슴살"],
        "nutrients": [{"name": "단백질", "note": "레보도파 흡수 경쟁"}, {"name": "나이아신", "note": "비타민B3"}, {"name": "비타민B6", "note": "레보도파 대사"}],
    },
    {
        "name": "돼지고기",
        "slug": "food-pork",
        "category": "육류",
        "description": "비타민B1(티아민)이 풍부. 고지방 부위는 지용성 약물 흡수를 증가시킬 수 있음",
        "common_names": ["돼지고기", "pork", "삼겹살"],
        "nutrients": [{"name": "비타민B1", "note": "티아민"}, {"name": "포화지방", "note": "지용성 약물 흡수 증가"}, {"name": "헴철", "note": "고흡수율 철분"}],
    },
    {
        "name": "소고기",
        "slug": "food-beef",
        "category": "육류",
        "description": "헴철과 아연이 풍부. 고단백 식이는 레보도파 흡수를 경쟁적으로 저해. 퓨린 함유로 통풍약 주의",
        "common_names": ["소고기", "beef", "한우"],
        "nutrients": [{"name": "헴철", "note": "고흡수율 철분"}, {"name": "아연", "note": "미네랄"}, {"name": "퓨린", "note": "요산 상승"}],
    },
    {
        "name": "양고기",
        "slug": "food-lamb",
        "category": "육류",
        "description": "카르니틴이 풍부. 고지방으로 지용성 약물 흡수에 영향. 퓨린 함유",
        "common_names": ["양고기", "lamb", "양갈비"],
        "nutrients": [{"name": "L-카르니틴", "note": "지방 대사"}, {"name": "헴철", "note": "철분"}, {"name": "퓨린", "note": "요산 상승"}],
    },
    {
        "name": "오리고기",
        "slug": "food-duck",
        "category": "육류",
        "description": "불포화지방산 비율이 높은 가금류. 지용성 약물 흡수에 영향. 철분 함유",
        "common_names": ["오리고기", "duck", "훈제오리"],
        "nutrients": [{"name": "불포화지방산", "note": "올레산"}, {"name": "헴철", "note": "철분"}, {"name": "비타민B군", "note": "에너지 대사"}],
    },
    {
        "name": "계란",
        "slug": "food-egg",
        "category": "육류",
        "description": "비오틴 함유로 비오틴 관련 검사 수치에 영향. 콜린이 풍부. 철분·칼슘이 약물 킬레이트 형성 가능",
        "common_names": ["계란", "달걀", "egg"],
        "nutrients": [{"name": "비오틴", "note": "혈액검사 간섭"}, {"name": "콜린", "note": "신경전달물질 전구체"}, {"name": "철분", "note": "노른자에 집중"}],
    },
    {
        "name": "메추리알",
        "slug": "food-quail-egg",
        "category": "육류",
        "description": "콜레스테롤이 닭알보다 높음. 비타민A·B12 풍부. 스타틴 복용자 다량 섭취 시 주의",
        "common_names": ["메추리알", "메추리란", "quail egg"],
        "nutrients": [{"name": "콜레스테롤", "note": "100g당 약 844mg"}, {"name": "비타민A", "note": "레티놀"}, {"name": "비타민B12", "note": "조혈"}],
    },
    {
        "name": "곱창",
        "slug": "food-intestine",
        "category": "육류",
        "description": "콜레스테롤과 퓨린이 높아 스타틴·통풍약과 상호작용 가능. 고지방으로 지용성 약물 흡수 변화",
        "common_names": ["곱창", "대창", "intestine"],
        "nutrients": [{"name": "콜레스테롤", "note": "고함량"}, {"name": "퓨린", "note": "요산 상승"}, {"name": "포화지방", "note": "지용성 약물 흡수 영향"}],
    },
    {
        "name": "족발",
        "slug": "food-pigs-feet",
        "category": "육류",
        "description": "콜라겐과 포화지방이 풍부. 고지방 식사는 지용성 약물 생체이용률을 변화시킬 수 있음",
        "common_names": ["족발", "pig's feet", "돼지족"],
        "nutrients": [{"name": "콜라겐", "note": "단백질"}, {"name": "포화지방", "note": "지용성 약물 흡수 영향"}],
    },
    {
        "name": "돼지간",
        "slug": "food-pork-liver",
        "category": "육류",
        "description": "비타민A(레티놀)가 극히 풍부하여 비타민A 보충제와 과잉 독성 위험. 이소트레티노인 병용 금기",
        "common_names": ["돼지간", "pork liver"],
        "nutrients": [{"name": "비타민A(레티놀)", "note": "100g당 약 6,500μg, 이소트레티노인 병용 금기"}, {"name": "헴철", "note": "고흡수율"}, {"name": "구리", "note": "미량원소"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 곡류/콩류 (+15) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "쌀 (백미)",
        "slug": "food-white-rice",
        "category": "곡류",
        "description": "고탄수화물 식품. 인슐린 분비를 촉진하여 당뇨약과 상가 작용으로 저혈당 위험 가능",
        "common_names": ["쌀", "백미", "white rice", "밥"],
        "nutrients": [{"name": "탄수화물", "note": "혈당 상승"}, {"name": "비타민B1", "note": "도정 시 감소"}],
    },
    {
        "name": "보리",
        "slug": "food-barley",
        "category": "곡류",
        "description": "베타글루칸(수용성 식이섬유)이 풍부하여 약물 흡수를 지연시킬 수 있음. 혈당·콜레스테롤 강하 효과",
        "common_names": ["보리", "barley", "보리밥"],
        "nutrients": [{"name": "베타글루칸", "note": "약물 흡수 지연"}, {"name": "식이섬유", "note": "혈당·콜레스테롤 강하"}],
    },
    {
        "name": "수수",
        "slug": "food-sorghum",
        "category": "곡류",
        "description": "탄닌이 풍부하여 철분제 흡수를 저해할 수 있음. 글루텐 프리 곡물",
        "common_names": ["수수", "sorghum"],
        "nutrients": [{"name": "탄닌", "note": "철분 흡수 저해"}, {"name": "폴리페놀", "note": "항산화"}],
    },
    {
        "name": "기장",
        "slug": "food-millet",
        "category": "곡류",
        "description": "고이트로겐을 함유하여 갑상선약(레보티록신) 흡수에 영향 가능. 마그네슘 풍부",
        "common_names": ["기장", "millet", "조"],
        "nutrients": [{"name": "고이트로겐", "note": "갑상선 영향"}, {"name": "마그네슘", "note": "미네랄"}],
    },
    {
        "name": "메밀 (모밀)",
        "slug": "food-buckwheat",
        "category": "곡류",
        "description": "루틴(비타민P)이 풍부하여 혈관 투과성을 낮추고 항응고제 효과에 영향 가능",
        "common_names": ["메밀", "모밀", "buckwheat", "소바"],
        "nutrients": [{"name": "루틴", "note": "혈관 강화, 항응고제 영향"}, {"name": "마그네슘", "note": "미네랄"}],
    },
    {
        "name": "검은콩",
        "slug": "food-black-bean",
        "category": "곡류",
        "description": "이소플라본과 안토시아닌이 풍부. 에스트로겐 관련 약물 및 갑상선약과 상호작용 가능",
        "common_names": ["검은콩", "서리태", "black bean"],
        "nutrients": [{"name": "이소플라본", "note": "식물성 에스트로겐"}, {"name": "안토시아닌", "note": "항산화"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "녹두",
        "slug": "food-mung-bean",
        "category": "곡류",
        "description": "해독 작용으로 한의학에서 사용. 일부 약물의 효과를 감소시킬 수 있다는 전통적 견해",
        "common_names": ["녹두", "mung bean"],
        "nutrients": [{"name": "비텍신", "note": "항산화"}, {"name": "이소비텍신", "note": "항산화"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "렌틸콩",
        "slug": "food-lentil",
        "category": "곡류",
        "description": "피트산과 식이섬유가 풍부하여 철분제, 아연 보충제 등 미네랄 약물 흡수를 저해",
        "common_names": ["렌틸콩", "렌즈콩", "lentil"],
        "nutrients": [{"name": "피트산", "note": "미네랄 킬레이트"}, {"name": "엽산", "note": "조혈"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "병아리콩",
        "slug": "food-chickpea",
        "category": "곡류",
        "description": "이소플라본 함유. 식이섬유와 피트산으로 미네랄 약물 흡수 저해. 혈당 강하 효과",
        "common_names": ["병아리콩", "chickpea", "가반조"],
        "nutrients": [{"name": "이소플라본", "note": "식물성 에스트로겐"}, {"name": "피트산", "note": "미네랄 킬레이트"}, {"name": "사포닌", "note": "콜레스테롤 저하"}],
    },
    {
        "name": "흑미",
        "slug": "food-black-rice",
        "category": "곡류",
        "description": "안토시아닌이 풍부하여 항산화 작용. 식이섬유로 약물 흡수 지연 가능",
        "common_names": ["흑미", "black rice"],
        "nutrients": [{"name": "안토시아닌", "note": "항산화"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "찹쌀",
        "slug": "food-glutinous-rice",
        "category": "곡류",
        "description": "아밀로펙틴 함량이 높아 소화·흡수가 빨라 혈당 급상승. 당뇨약 복용자 섭취량 주의",
        "common_names": ["찹쌀", "glutinous rice", "찰밥"],
        "nutrients": [{"name": "아밀로펙틴", "note": "혈당 급상승(고GI)"}],
    },
    {
        "name": "퀴노아",
        "slug": "food-quinoa",
        "category": "곡류",
        "description": "사포닌이 표면에 존재. 식이섬유와 미네랄이 풍부하여 약물 흡수에 영향 가능",
        "common_names": ["퀴노아", "quinoa"],
        "nutrients": [{"name": "사포닌", "note": "소화 자극"}, {"name": "마그네슘", "note": "미네랄"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "율무",
        "slug": "food-jobs-tears",
        "category": "곡류",
        "description": "코이시놀이 항종양·항염 작용. 이뇨 효과로 리튬 약물 농도에 영향. 임산부 주의 식품",
        "common_names": ["율무", "의이인", "Job's tears"],
        "nutrients": [{"name": "코이시놀", "note": "항종양·항염"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "아마씨",
        "slug": "food-flaxseed",
        "category": "곡류",
        "description": "리그난(식물성 에스트로겐)과 오메가3(ALA)가 풍부. 에스트로겐 약물·항응고제와 상호작용 가능. 약물 흡수 지연",
        "common_names": ["아마씨", "flaxseed", "린시드"],
        "nutrients": [{"name": "리그난", "note": "식물성 에스트로겐"}, {"name": "오메가3(ALA)", "note": "항혈소판"}, {"name": "식이섬유", "note": "약물 흡수 지연(30분 간격 권장)"}],
    },
    {
        "name": "치아씨",
        "slug": "food-chia-seed",
        "category": "곡류",
        "description": "오메가3(ALA)와 식이섬유 극히 풍부. 항응고제 병용 시 출혈 위험. 약물 흡수를 지연시킬 수 있음",
        "common_names": ["치아씨", "치아시드", "chia seed"],
        "nutrients": [{"name": "오메가3(ALA)", "note": "항혈소판 작용"}, {"name": "식이섬유", "note": "수분 흡수하여 약물 흡수 지연"}, {"name": "칼슘", "note": "항생제 킬레이트"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 유제품/대체유 (+8) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "모짜렐라치즈",
        "slug": "food-mozzarella",
        "category": "유제품",
        "description": "칼슘이 풍부하여 퀴놀론·테트라사이클린 항생제 흡수 저해. 숙성 치즈보다 티라민 함량은 낮음",
        "common_names": ["모짜렐라", "모짜렐라치즈", "mozzarella"],
        "nutrients": [{"name": "칼슘", "note": "항생제 킬레이트"}, {"name": "카제인", "note": "약물 결합 가능"}],
    },
    {
        "name": "크림치즈",
        "slug": "food-cream-cheese",
        "category": "유제품",
        "description": "고지방 유제품. 지용성 약물(그리세오풀빈 등)의 흡수를 증가시킬 수 있음",
        "common_names": ["크림치즈", "cream cheese"],
        "nutrients": [{"name": "포화지방", "note": "지용성 약물 흡수 증가"}, {"name": "칼슘", "note": "항생제 킬레이트"}],
    },
    {
        "name": "아이스크림",
        "slug": "food-ice-cream",
        "category": "유제품",
        "description": "칼슘과 지방이 풍부하여 항생제 흡수 저해 및 지용성 약물 흡수 증가. 당분이 높아 당뇨약 주의",
        "common_names": ["아이스크림", "ice cream"],
        "nutrients": [{"name": "칼슘", "note": "항생제 킬레이트"}, {"name": "포화지방", "note": "지용성 약물 흡수"}, {"name": "당분", "note": "혈당 영향"}],
    },
    {
        "name": "연유",
        "slug": "food-condensed-milk",
        "category": "유제품",
        "description": "고농축 당분과 칼슘. 당뇨약 복용자 혈당 급상승 주의. 항생제 흡수 저해",
        "common_names": ["연유", "condensed milk"],
        "nutrients": [{"name": "당분", "note": "혈당 급상승"}, {"name": "칼슘", "note": "항생제 킬레이트"}],
    },
    {
        "name": "아몬드밀크",
        "slug": "food-almond-milk",
        "category": "유제품",
        "description": "칼슘 강화 제품이 많아 퀴놀론·테트라사이클린 흡수 저해 가능. 유당 불내증 대체 음료",
        "common_names": ["아몬드밀크", "아몬드우유", "almond milk"],
        "nutrients": [{"name": "칼슘(강화)", "note": "항생제 킬레이트"}, {"name": "비타민E", "note": "항산화"}],
    },
    {
        "name": "오트밀크",
        "slug": "food-oat-milk",
        "category": "유제품",
        "description": "베타글루칸 함유로 약물 흡수 지연 가능. 칼슘 강화 제품은 항생제 흡수에 영향",
        "common_names": ["오트밀크", "귀리우유", "oat milk"],
        "nutrients": [{"name": "베타글루칸", "note": "약물 흡수 지연"}, {"name": "칼슘(강화)", "note": "항생제 킬레이트"}],
    },
    {
        "name": "코코넛밀크",
        "slug": "food-coconut-milk",
        "category": "유제품",
        "description": "포화지방(라우르산)이 풍부하여 지용성 약물 흡수를 증가시킬 수 있음",
        "common_names": ["코코넛밀크", "coconut milk"],
        "nutrients": [{"name": "라우르산", "note": "중쇄지방산"}, {"name": "포화지방", "note": "지용성 약물 흡수 증가"}],
    },
    {
        "name": "한국식 두유 (가당)",
        "slug": "food-korean-soy-milk",
        "category": "유제품",
        "description": "이소플라본 함유에 당분이 추가된 가공 두유. 갑상선약 흡수 저해. 당뇨약 복용자 혈당 주의",
        "common_names": ["한국식 두유", "가당두유", "베지밀"],
        "nutrients": [{"name": "이소플라본", "note": "갑상선약 흡수 저해"}, {"name": "당분", "note": "혈당 영향"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 음료 (+15) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "홍차",
        "slug": "food-black-tea",
        "category": "음료",
        "description": "카페인과 탄닌이 풍부. 철분제 흡수를 50~70% 저해. CYP1A2 기질로 약물 대사에 영향",
        "common_names": ["홍차", "black tea", "잉글리시 브렉퍼스트"],
        "nutrients": [{"name": "카페인", "note": "CYP1A2 기질"}, {"name": "탄닌", "note": "철분 흡수 50~70% 저해"}, {"name": "테아플라빈", "note": "항산화"}],
    },
    {
        "name": "우롱차",
        "slug": "food-oolong-tea",
        "category": "음료",
        "description": "카페인과 카테킨 함유. 철분 흡수 저해. CYP1A2를 통한 약물 대사에 영향 가능",
        "common_names": ["우롱차", "oolong tea"],
        "nutrients": [{"name": "카페인", "note": "CYP1A2 기질"}, {"name": "카테킨", "note": "철분 흡수 저해"}, {"name": "폴리페놀", "note": "항산화"}],
    },
    {
        "name": "보이차",
        "slug": "food-puer-tea",
        "category": "음료",
        "description": "발효차로 카페인 함유. 갈산과 탄닌이 철분 흡수를 저해. 스타틴 약효에 영향 가능",
        "common_names": ["보이차", "푸얼차", "pu-erh tea"],
        "nutrients": [{"name": "카페인", "note": "CYP1A2 기질"}, {"name": "갈산", "note": "철분 흡수 저해"}, {"name": "로바스타틴(미량)", "note": "발효 과정 생성"}],
    },
    {
        "name": "매실차 (매실액)",
        "slug": "food-plum-tea",
        "category": "음료",
        "description": "유기산(구연산·사과산)이 풍부하여 위산도 변화. 일부 약물 용해·흡수에 영향. 당분 함량 높음",
        "common_names": ["매실차", "매실액", "매실청", "plum tea"],
        "nutrients": [{"name": "구연산", "note": "위산도 변화"}, {"name": "사과산", "note": "유기산"}, {"name": "당분", "note": "혈당 영향"}],
    },
    {
        "name": "유자차",
        "slug": "food-yuzu-tea",
        "category": "음료",
        "description": "비타민C가 풍부한 감귤류 차. 플라보노이드 함유로 CYP 효소에 경미한 영향 가능",
        "common_names": ["유자차", "yuzu tea"],
        "nutrients": [{"name": "비타민C", "note": "항산화"}, {"name": "리모넨", "note": "감귤류 테르펜"}, {"name": "당분", "note": "설탕 절임"}],
    },
    {
        "name": "대추차",
        "slug": "food-jujube-tea",
        "category": "음료",
        "description": "사포닌과 플라보노이드 함유. 진정 작용으로 수면제·항불안제와 상가 작용 가능. 당분 주의",
        "common_names": ["대추차", "jujube tea"],
        "nutrients": [{"name": "사포닌", "note": "진정 작용"}, {"name": "당분", "note": "혈당 영향"}],
    },
    {
        "name": "생강차",
        "slug": "food-ginger-tea",
        "category": "음료",
        "description": "진저롤이 항혈소판 작용. 항응고제(와파린, 아스피린)와 병용 시 출혈 위험 증가",
        "common_names": ["생강차", "ginger tea"],
        "nutrients": [{"name": "진저롤", "note": "항혈소판 작용"}, {"name": "쇼가올", "note": "항구역"}],
    },
    {
        "name": "쌍화차",
        "slug": "food-ssanghwa-tea",
        "category": "음료",
        "description": "작약·당귀·숙지황 등 다수 한약재 배합. 항응고제와 상호작용. 다약 복용자 주의",
        "common_names": ["쌍화차", "쌍화탕", "ssanghwa tea"],
        "nutrients": [{"name": "작약 성분", "note": "항혈소판"}, {"name": "당귀 성분", "note": "쿠마린 함유"}, {"name": "카페인", "note": "일부 제품에 함유"}],
    },
    {
        "name": "식혜",
        "slug": "food-sikhye",
        "category": "음료",
        "description": "엿기름(맥아) 유래 전통 음료. 당분이 높아 당뇨약 복용자 혈당 주의. 소화 효소 함유",
        "common_names": ["식혜", "sikhye", "감주"],
        "nutrients": [{"name": "맥아당", "note": "혈당 상승"}, {"name": "아밀라아제", "note": "소화 효소"}],
    },
    {
        "name": "수정과",
        "slug": "food-sujeonggwa",
        "category": "음료",
        "description": "계피와 생강이 주재료. 쿠마린(계피)과 진저롤(생강)로 항응고제 병용 시 출혈 위험",
        "common_names": ["수정과", "sujeonggwa"],
        "nutrients": [{"name": "쿠마린", "note": "계피 유래, 항응고"}, {"name": "진저롤", "note": "생강 유래, 항혈소판"}, {"name": "당분", "note": "혈당 영향"}],
    },
    {
        "name": "미숫가루",
        "slug": "food-misutgaru",
        "category": "음료",
        "description": "여러 곡물 혼합 분말. 식이섬유가 풍부하여 약물 흡수를 지연. 피트산으로 미네랄 약물 킬레이트",
        "common_names": ["미숫가루", "misutgaru"],
        "nutrients": [{"name": "식이섬유", "note": "약물 흡수 지연"}, {"name": "피트산", "note": "미네랄 킬레이트"}],
    },
    {
        "name": "코코아",
        "slug": "food-cocoa",
        "category": "음료",
        "description": "테오브로민과 카페인 함유. MAO 억제제 복용자 티라민 주의. 플라바놀이 CYP 효소에 영향",
        "common_names": ["코코아", "핫초코", "cocoa", "hot chocolate"],
        "nutrients": [{"name": "테오브로민", "note": "카페인 유사체"}, {"name": "플라바놀", "note": "CYP 효소 영향"}, {"name": "카페인", "note": "미량"}],
    },
    {
        "name": "석류주스",
        "slug": "food-pomegranate-juice",
        "category": "음료",
        "description": "CYP3A4 및 CYP2C9 억제 작용이 보고됨. 스타틴, 와파린 등 다수 약물과 상호작용 가능",
        "common_names": ["석류주스", "pomegranate juice"],
        "nutrients": [{"name": "엘라그산", "note": "CYP2C9 억제"}, {"name": "푸니칼라긴", "note": "CYP3A4 억제"}],
    },
    {
        "name": "토마토주스",
        "slug": "food-tomato-juice",
        "category": "음료",
        "description": "칼륨이 농축된 형태로 ACE 억제제·칼륨보존이뇨제와 고칼륨혈증 위험. 리코펜 풍부",
        "common_names": ["토마토주스", "tomato juice"],
        "nutrients": [{"name": "칼륨", "note": "농축, 고칼륨혈증 위험"}, {"name": "리코펜", "note": "항산화"}],
    },
    {
        "name": "당근주스",
        "slug": "food-carrot-juice",
        "category": "음료",
        "description": "베타카로틴이 농축되어 비타민A 보충제와 과잉 위험. 칼륨도 농축",
        "common_names": ["당근주스", "carrot juice"],
        "nutrients": [{"name": "베타카로틴", "note": "농축, 비타민A 과잉 위험"}, {"name": "칼륨", "note": "농축"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 발효식품 (+10) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "고추장",
        "slug": "food-gochujang",
        "category": "발효식품",
        "description": "발효 과정에서 티라민 생성 가능. 나트륨과 당분이 높아 혈압약·당뇨약 복용자 주의",
        "common_names": ["고추장", "gochujang"],
        "nutrients": [{"name": "티라민", "note": "발효 생성, MAO 억제제 주의"}, {"name": "나트륨", "note": "고함량"}, {"name": "캡사이신", "note": "위장관 자극"}],
    },
    {
        "name": "쌈장",
        "slug": "food-ssamjang",
        "category": "발효식품",
        "description": "된장+고추장 혼합 발효 양념. 티라민과 나트륨 함유. MAO 억제제·혈압약 주의",
        "common_names": ["쌈장", "ssamjang"],
        "nutrients": [{"name": "티라민", "note": "발효 과정"}, {"name": "나트륨", "note": "고함량"}, {"name": "이소플라본", "note": "된장 유래"}],
    },
    {
        "name": "어간장 (액젓)",
        "slug": "food-fish-sauce",
        "category": "발효식품",
        "description": "히스타민과 티라민이 높은 발효 액젓. MAO 억제제·항히스타민제 복용자 주의",
        "common_names": ["어간장", "액젓", "까나리액젓", "멸치액젓", "fish sauce"],
        "nutrients": [{"name": "히스타민", "note": "발효 어류"}, {"name": "티라민", "note": "MAO 상호작용"}, {"name": "나트륨", "note": "극히 고함량"}],
    },
    {
        "name": "젓갈",
        "slug": "food-jeotgal",
        "category": "발효식품",
        "description": "히스타민과 티라민이 풍부한 발효 해산물. MAO 억제제와 고혈압 위기 위험. 나트륨 극고",
        "common_names": ["젓갈", "새우젓", "명란젓", "어리굴젓", "jeotgal"],
        "nutrients": [{"name": "히스타민", "note": "고농도"}, {"name": "티라민", "note": "MAO 상호작용"}, {"name": "나트륨", "note": "극고함량"}],
    },
    {
        "name": "막걸리",
        "slug": "food-makgeolli",
        "category": "발효식품",
        "description": "알코올+유산균 발효 음료. 에탄올의 약물 상호작용 + 티라민 함유로 MAO 억제제 주의",
        "common_names": ["막걸리", "makgeolli", "탁주"],
        "nutrients": [{"name": "에탄올", "note": "알코올 약물 상호작용"}, {"name": "유산균", "note": "프로바이오틱스"}, {"name": "티라민", "note": "발효 생성"}],
    },
    {
        "name": "드링크 요구르트",
        "slug": "food-drinking-yogurt",
        "category": "발효식품",
        "description": "칼슘이 풍부하여 항생제(퀴놀론, 테트라사이클린) 흡수 저해. 당분이 높은 가공 유제품",
        "common_names": ["드링크요구르트", "야쿠르트", "요구르트음료", "drinking yogurt"],
        "nutrients": [{"name": "칼슘", "note": "항생제 킬레이트"}, {"name": "유산균", "note": "장건강"}, {"name": "당분", "note": "혈당 영향"}],
    },
    {
        "name": "콤부차",
        "slug": "food-kombucha",
        "category": "발효식품",
        "description": "발효차 음료로 카페인·유기산·알코올(미량) 함유. 면역 자극 효과로 면역억제제와 상호작용 가능",
        "common_names": ["콤부차", "kombucha"],
        "nutrients": [{"name": "유기산", "note": "위산도 변화"}, {"name": "카페인", "note": "차 유래"}, {"name": "에탄올", "note": "미량, 발효 생성"}],
    },
    {
        "name": "사과식초 (유기농)",
        "slug": "food-apple-cider-vinegar",
        "category": "발효식품",
        "description": "아세트산이 혈당 강하 작용. 당뇨약과 저혈당 상가 위험. 이뇨제 병용 시 저칼륨혈증 가능",
        "common_names": ["사과식초", "애플사이다비네거", "apple cider vinegar", "ACV"],
        "nutrients": [{"name": "아세트산", "note": "혈당 강하"}, {"name": "칼륨", "note": "장기 대량 섭취 시 저칼륨"}],
    },
    {
        "name": "미소",
        "slug": "food-miso",
        "category": "발효식품",
        "description": "일본식 된장. 티라민과 이소플라본 함유. MAO 억제제 주의. 나트륨 고함량",
        "common_names": ["미소", "미소된장", "miso"],
        "nutrients": [{"name": "티라민", "note": "MAO 상호작용"}, {"name": "이소플라본", "note": "식물성 에스트로겐"}, {"name": "나트륨", "note": "고함량"}],
    },
    {
        "name": "템페",
        "slug": "food-tempeh",
        "category": "발효식품",
        "description": "발효 대두로 티라민 함유. MAO 억제제 복용자 고혈압 위기 위험. 이소플라본 풍부",
        "common_names": ["템페", "tempeh"],
        "nutrients": [{"name": "티라민", "note": "MAO 상호작용"}, {"name": "이소플라본", "note": "식물성 에스트로겐"}, {"name": "비타민K2", "note": "발효 생성"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 조미료/향신료 (+15) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "고춧가루",
        "slug": "food-red-pepper-powder",
        "category": "조미료/향신료",
        "description": "캡사이신이 위장관을 자극하여 일부 약물 흡수 변화. P-glycoprotein 억제 보고",
        "common_names": ["고춧가루", "red pepper powder", "고추가루"],
        "nutrients": [{"name": "캡사이신", "note": "P-gp 억제, 위장관 자극"}, {"name": "비타민A", "note": "베타카로틴"}],
    },
    {
        "name": "참기름",
        "slug": "food-sesame-oil",
        "category": "조미료/향신료",
        "description": "세사민이 CYP3A4를 억제하여 다수 약물의 혈중 농도를 높일 수 있음. 지용성 약물 흡수 촉진",
        "common_names": ["참기름", "sesame oil"],
        "nutrients": [{"name": "세사민", "note": "CYP3A4 억제"}, {"name": "세사몰린", "note": "항산화"}, {"name": "리놀레산", "note": "오메가6"}],
    },
    {
        "name": "들기름",
        "slug": "food-perilla-oil",
        "category": "조미료/향신료",
        "description": "오메가3(ALA)가 풍부하여 항응고제 병용 시 출혈 위험 증가. 로즈마린산 함유",
        "common_names": ["들기름", "perilla oil"],
        "nutrients": [{"name": "오메가3(ALA)", "note": "항혈소판 작용"}, {"name": "로즈마린산", "note": "항산화·항염"}],
    },
    {
        "name": "올리브오일",
        "slug": "food-olive-oil",
        "category": "조미료/향신료",
        "description": "올레유로핀이 혈압 강하 작용. 항고혈압제와 저혈압 상가 가능. 지용성 약물 흡수 촉진",
        "common_names": ["올리브오일", "올리브유", "olive oil"],
        "nutrients": [{"name": "올레유로핀", "note": "혈압 강하"}, {"name": "올레산", "note": "불포화지방산"}, {"name": "폴리페놀", "note": "항산화"}],
    },
    {
        "name": "코코넛오일",
        "slug": "food-coconut-oil",
        "category": "조미료/향신료",
        "description": "중쇄지방산(MCT)이 풍부. 지용성 약물의 생체이용률을 변화시킬 수 있음",
        "common_names": ["코코넛오일", "코코넛유", "coconut oil"],
        "nutrients": [{"name": "라우르산", "note": "중쇄지방산"}, {"name": "MCT", "note": "지용성 약물 흡수 영향"}],
    },
    {
        "name": "바질",
        "slug": "food-basil",
        "category": "조미료/향신료",
        "description": "유제놀 함유로 항혈소판 작용. 항응고제 병용 시 출혈 위험 증가 가능. 에스트라골 함유",
        "common_names": ["바질", "basil", "바질잎"],
        "nutrients": [{"name": "유제놀", "note": "항혈소판"}, {"name": "에스트라골", "note": "CYP 영향"}, {"name": "비타민K", "note": "신선 바질에 고함량"}],
    },
    {
        "name": "로즈마리",
        "slug": "food-rosemary",
        "category": "조미료/향신료",
        "description": "카르노솔이 CYP3A4를 억제하고 P-glycoprotein에 영향. 다수 약물 혈중 농도 변화 가능",
        "common_names": ["로즈마리", "rosemary"],
        "nutrients": [{"name": "카르노솔", "note": "CYP3A4 억제"}, {"name": "로즈마린산", "note": "항산화"}, {"name": "캠퍼", "note": "정유 성분"}],
    },
    {
        "name": "타임",
        "slug": "food-thyme",
        "category": "조미료/향신료",
        "description": "티몰이 항균·항산화 작용. 비타민K가 풍부하여 와파린 복용자 주의",
        "common_names": ["타임", "백리향", "thyme"],
        "nutrients": [{"name": "티몰", "note": "항균 성분"}, {"name": "비타민K", "note": "와파린 길항"}],
    },
    {
        "name": "오레가노",
        "slug": "food-oregano",
        "category": "조미료/향신료",
        "description": "카르바크롤이 CYP 효소에 영향. 항혈소판 작용 보고. 비타민K 함유",
        "common_names": ["오레가노", "oregano"],
        "nutrients": [{"name": "카르바크롤", "note": "CYP 영향·항혈소판"}, {"name": "비타민K", "note": "와파린 길항"}],
    },
    {
        "name": "딜",
        "slug": "food-dill",
        "category": "조미료/향신료",
        "description": "이뇨 작용이 있어 리튬 약물 농도에 영향 가능. 에스트로겐 유사 작용 보고",
        "common_names": ["딜", "dill"],
        "nutrients": [{"name": "카르본", "note": "이뇨 작용"}, {"name": "리모넨", "note": "정유 성분"}, {"name": "아피제닌", "note": "에스트로겐 유사"}],
    },
    {
        "name": "월계수잎",
        "slug": "food-bay-leaf",
        "category": "조미료/향신료",
        "description": "혈당 강하 작용이 보고되어 당뇨약과 저혈당 상가 위험. 유제놀 함유",
        "common_names": ["월계수잎", "bay leaf", "로렐"],
        "nutrients": [{"name": "유제놀", "note": "항혈소판"}, {"name": "시네올", "note": "정유 성분"}, {"name": "혈당 강하 성분", "note": "인슐린 민감도 개선"}],
    },
    {
        "name": "팔각 (스타아니스)",
        "slug": "food-star-anise",
        "category": "조미료/향신료",
        "description": "시키믹산 함유(타미플루 원료). 에스트로겐 유사 작용으로 호르몬 약물 상호작용 가능",
        "common_names": ["팔각", "스타아니스", "대회향", "star anise"],
        "nutrients": [{"name": "아네톨", "note": "에스트로겐 유사 작용"}, {"name": "시키믹산", "note": "항바이러스 전구체"}],
    },
    {
        "name": "정향",
        "slug": "food-clove",
        "category": "조미료/향신료",
        "description": "유제놀이 매우 풍부하여 항혈소판·항응고 작용. CYP 효소 억제. 항응고제 병용 시 출혈 위험",
        "common_names": ["정향", "clove"],
        "nutrients": [{"name": "유제놀", "note": "강력한 항혈소판, CYP 억제"}, {"name": "갈산", "note": "항산화"}],
    },
    {
        "name": "육두구 (넛맥)",
        "slug": "food-nutmeg",
        "category": "조미료/향신료",
        "description": "미리스티신이 MAO 억제 작용. 대량 섭취 시 환각·독성. MAO 억제제와 심각한 상호작용",
        "common_names": ["육두구", "넛맥", "nutmeg"],
        "nutrients": [{"name": "미리스티신", "note": "MAO 억제, 대량 시 독성"}, {"name": "사프롤", "note": "정유 성분"}],
    },
    {
        "name": "사프란",
        "slug": "food-saffron",
        "category": "조미료/향신료",
        "description": "크로세틴이 항우울 작용. SSRI 항우울제와 세로토닌 증후군 위험. 항혈소판 작용",
        "common_names": ["사프란", "saffron"],
        "nutrients": [{"name": "크로세틴", "note": "항우울·세로토닌 조절"}, {"name": "사프라날", "note": "항산화"}, {"name": "피크로크로신", "note": "항혈소판"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 견과/씨앗 (+12) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "잣",
        "slug": "food-pine-nut",
        "category": "견과류",
        "description": "피놀렌산이 식욕 억제 호르몬(CCK) 분비를 촉진. 마그네슘 풍부. 약물 흡수 지연 가능",
        "common_names": ["잣", "pine nut"],
        "nutrients": [{"name": "피놀렌산", "note": "식욕 억제"}, {"name": "마그네슘", "note": "미네랄"}, {"name": "아연", "note": "면역"}],
    },
    {
        "name": "해바라기씨",
        "slug": "food-sunflower-seed",
        "category": "견과류",
        "description": "비타민E가 극히 풍부하여 항응고제와 출혈 위험 증가. 셀레늄 함유",
        "common_names": ["해바라기씨", "sunflower seed"],
        "nutrients": [{"name": "비타민E", "note": "항산화, 항응고제 출혈 위험"}, {"name": "셀레늄", "note": "항산화 미네랄"}, {"name": "마그네슘", "note": "미네랄"}],
    },
    {
        "name": "호박씨",
        "slug": "food-pumpkin-seed",
        "category": "견과류",
        "description": "아연과 마그네슘이 풍부. 피토스테롤 함유로 콜레스테롤 약물과 상가 작용 가능",
        "common_names": ["호박씨", "pumpkin seed", "pepitas"],
        "nutrients": [{"name": "아연", "note": "고함량"}, {"name": "마그네슘", "note": "미네랄"}, {"name": "피토스테롤", "note": "콜레스테롤 저하"}],
    },
    {
        "name": "피스타치오",
        "slug": "food-pistachio",
        "category": "견과류",
        "description": "칼륨과 비타민B6가 풍부. 칼륨보존이뇨제 병용 시 고칼륨혈증 주의",
        "common_names": ["피스타치오", "pistachio"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 1,025mg"}, {"name": "비타민B6", "note": "레보도파 대사 촉진"}, {"name": "피토스테롤", "note": "콜레스테롤 저하"}],
    },
    {
        "name": "마카다미아",
        "slug": "food-macadamia",
        "category": "견과류",
        "description": "불포화지방산(팔미톨레산)이 풍부. 고지방으로 지용성 약물 흡수 증가. 칼로리 높음",
        "common_names": ["마카다미아", "macadamia"],
        "nutrients": [{"name": "팔미톨레산", "note": "불포화지방산"}, {"name": "마그네슘", "note": "미네랄"}],
    },
    {
        "name": "브라질너트",
        "slug": "food-brazil-nut",
        "category": "견과류",
        "description": "셀레늄이 극히 풍부(1개에 약 70μg). 셀레늄 보충제와 과잉 독성 위험. 갑상선 기능에 영향",
        "common_names": ["브라질너트", "brazil nut"],
        "nutrients": [{"name": "셀레늄", "note": "1개 약 70μg, 과잉 독성 주의"}, {"name": "마그네슘", "note": "미네랄"}],
    },
    {
        "name": "피칸",
        "slug": "food-pecan",
        "category": "견과류",
        "description": "엘라그산과 감마토코페롤(비타민E)이 풍부. 항산화 작용. 식이섬유가 약물 흡수 지연",
        "common_names": ["피칸", "pecan"],
        "nutrients": [{"name": "감마토코페롤", "note": "비타민E 형태"}, {"name": "엘라그산", "note": "항산화"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "밤",
        "slug": "food-chestnut",
        "category": "견과류",
        "description": "탄수화물이 풍부한 견과류. 당뇨약 복용자 혈당 주의. 비타민C 함유",
        "common_names": ["밤", "chestnut"],
        "nutrients": [{"name": "탄수화물", "note": "혈당 상승"}, {"name": "비타민C", "note": "견과류 중 고함량"}],
    },
    {
        "name": "은행",
        "slug": "food-ginkgo-nut",
        "category": "견과류",
        "description": "4'-O-메틸피리독신(MPN)이 비타민B6 길항제로 작용하여 경련 유발 가능. 과량 섭취 위험",
        "common_names": ["은행", "ginkgo nut", "백과"],
        "nutrients": [{"name": "4'-O-메틸피리독신", "note": "비타민B6 길항, 경련 위험"}, {"name": "징콜산", "note": "알레르기 유발"}],
    },
    {
        "name": "대마씨 (헴프씨드)",
        "slug": "food-hemp-seed",
        "category": "견과류",
        "description": "오메가3·6 균형 비율. 항응고제 병용 시 출혈 위험. 식이섬유가 약물 흡수 지연",
        "common_names": ["대마씨", "헴프씨드", "hemp seed"],
        "nutrients": [{"name": "오메가3(ALA)", "note": "항혈소판"}, {"name": "오메가6(GLA)", "note": "항염"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "들깨",
        "slug": "food-perilla-seed",
        "category": "견과류",
        "description": "오메가3(ALA)가 극히 풍부. 항응고제 병용 시 출혈 위험 증가. 로즈마린산 함유",
        "common_names": ["들깨", "perilla seed"],
        "nutrients": [{"name": "오메가3(ALA)", "note": "항혈소판 작용"}, {"name": "로즈마린산", "note": "항산화·항알레르기"}],
    },
    {
        "name": "참깨",
        "slug": "food-sesame-seed",
        "category": "견과류",
        "description": "세사민이 CYP3A4를 억제하여 다수 약물 혈중 농도 상승 가능. 칼슘·마그네슘 풍부",
        "common_names": ["참깨", "sesame seed", "깨"],
        "nutrients": [{"name": "세사민", "note": "CYP3A4 억제"}, {"name": "칼슘", "note": "항생제 킬레이트"}, {"name": "마그네슘", "note": "미네랄"}],
    },

    # ══════════════════════════════════════════════════════════
    # ── 기타/가공 (+15) ──
    # ══════════════════════════════════════════════════════════
    {
        "name": "초콜릿 (밀크)",
        "slug": "food-milk-chocolate",
        "category": "기타",
        "description": "테오브로민과 카페인 함유. 칼슘(유제품)이 항생제 흡수 저해. MAO 억제제 복용자 주의",
        "common_names": ["밀크초콜릿", "초콜릿", "milk chocolate"],
        "nutrients": [{"name": "테오브로민", "note": "카페인 유사체"}, {"name": "칼슘", "note": "유제품 유래"}, {"name": "당분", "note": "혈당 영향"}],
    },
    {
        "name": "젤리 (젤라틴)",
        "slug": "food-gelatin",
        "category": "기타",
        "description": "젤라틴이 일부 약물과 결합하여 흡수 저해 가능. 고당분으로 당뇨약 복용자 주의",
        "common_names": ["젤리", "젤라틴", "gelatin", "jelly"],
        "nutrients": [{"name": "젤라틴", "note": "약물 결합 가능"}, {"name": "당분", "note": "혈당 영향"}],
    },
    {
        "name": "소금",
        "slug": "food-salt",
        "category": "기타",
        "description": "나트륨이 리튬 배설에 직접 영향. 리튬 복용자 나트륨 섭취 급변 시 독성 위험. 혈압약 효과 감소",
        "common_names": ["소금", "식염", "salt", "천일염"],
        "nutrients": [{"name": "나트륨", "note": "리튬 배설 경쟁, 혈압 상승"}],
    },
    {
        "name": "설탕",
        "slug": "food-sugar",
        "category": "기타",
        "description": "혈당을 급격히 상승시켜 당뇨약(메트포르민, 인슐린 등) 효과를 감소시킬 수 있음",
        "common_names": ["설탕", "백설탕", "sugar", "흑설탕"],
        "nutrients": [{"name": "자당", "note": "혈당 급상승"}, {"name": "과당", "note": "간 대사"}],
    },
    {
        "name": "아스파탐 (인공감미료)",
        "slug": "food-aspartame",
        "category": "기타",
        "description": "페닐알라닌을 함유하여 페닐케톤뇨증(PKU) 환자 금기. 레보도파 흡수 경쟁 가능",
        "common_names": ["아스파탐", "aspartame", "인공감미료"],
        "nutrients": [{"name": "페닐알라닌", "note": "PKU 금기, 레보도파 흡수 경쟁"}, {"name": "아스파르트산", "note": "아미노산"}],
    },
    {
        "name": "MSG (글루탐산나트륨)",
        "slug": "food-msg",
        "category": "기타",
        "description": "글루탐산이 흥분성 신경전달물질. 나트륨 함유로 리튬 약물에 영향. 대량 섭취 시 두통 보고",
        "common_names": ["MSG", "글루탐산나트륨", "미원", "monosodium glutamate"],
        "nutrients": [{"name": "글루탐산", "note": "흥분성 신경전달"}, {"name": "나트륨", "note": "리튬 배설 영향"}],
    },
    {
        "name": "탄산수",
        "slug": "food-sparkling-water",
        "category": "기타",
        "description": "이산화탄소로 위산도를 일시적으로 변화시켜 일부 약물 용해·흡수에 영향 가능",
        "common_names": ["탄산수", "sparkling water", "소다수"],
        "nutrients": [{"name": "이산화탄소", "note": "위산도 일시 변화"}, {"name": "미네랄", "note": "제품별 상이"}],
    },
    {
        "name": "베이킹소다 (중조)",
        "slug": "food-baking-soda",
        "category": "기타",
        "description": "탄산수소나트륨이 위산을 중화하여 산성 환경 필요 약물(케토코나졸 등)의 흡수를 저해",
        "common_names": ["베이킹소다", "중조", "탄산수소나트륨", "baking soda"],
        "nutrients": [{"name": "탄산수소나트륨", "note": "위산 중화, 약물 흡수 저해"}, {"name": "나트륨", "note": "고함량"}],
    },
    {
        "name": "식용유 (대두유)",
        "slug": "food-soybean-oil",
        "category": "기타",
        "description": "오메가6(리놀레산)가 풍부. 지용성 약물 흡수를 촉진. 비타민E 함유",
        "common_names": ["식용유", "대두유", "콩기름", "soybean oil"],
        "nutrients": [{"name": "리놀레산", "note": "오메가6"}, {"name": "비타민E", "note": "항산화"}, {"name": "지방", "note": "지용성 약물 흡수 촉진"}],
    },
    {
        "name": "포도씨유",
        "slug": "food-grapeseed-oil",
        "category": "기타",
        "description": "프로안토시아니딘이 CYP 효소에 영향 가능. 비타민E 풍부. 지용성 약물 흡수 촉진",
        "common_names": ["포도씨유", "grapeseed oil"],
        "nutrients": [{"name": "프로안토시아니딘", "note": "CYP 영향"}, {"name": "비타민E", "note": "항산화"}, {"name": "리놀레산", "note": "오메가6"}],
    },
    {
        "name": "코코넛워터",
        "slug": "food-coconut-water",
        "category": "기타",
        "description": "칼륨이 매우 풍부하여 ACE 억제제, 칼륨보존이뇨제와 고칼륨혈증 위험",
        "common_names": ["코코넛워터", "coconut water"],
        "nutrients": [{"name": "칼륨", "note": "100ml당 약 250mg"}, {"name": "마그네슘", "note": "전해질"}, {"name": "나트륨", "note": "미량"}],
    },
    {
        "name": "알로에",
        "slug": "food-aloe-vera",
        "category": "기타",
        "description": "알로인이 강한 완하 작용으로 약물 흡수 감소. 디곡신 독성 증가(저칼륨). 혈당 강하 효과",
        "common_names": ["알로에", "알로에베라", "aloe vera"],
        "nutrients": [{"name": "알로인", "note": "완하 작용, 디곡신 독성 위험"}, {"name": "아세만난", "note": "면역 자극"}, {"name": "바르발로인", "note": "혈당 강하"}],
    },
    {
        "name": "노니",
        "slug": "food-noni",
        "category": "기타",
        "description": "칼륨이 풍부하여 칼륨 관련 약물 주의. 간독성 보고 사례. CYP 효소 억제 가능",
        "common_names": ["노니", "noni", "노니주스"],
        "nutrients": [{"name": "칼륨", "note": "고함량"}, {"name": "스코폴레틴", "note": "혈압 강하"}, {"name": "다구스테롤", "note": "CYP 영향 가능"}],
    },
    {
        "name": "아사이베리",
        "slug": "food-acai-berry",
        "category": "기타",
        "description": "안토시아닌이 극히 풍부. CYP 효소에 영향 가능. 항응고제 병용 시 출혈 위험 보고",
        "common_names": ["아사이베리", "아사이", "acai berry"],
        "nutrients": [{"name": "안토시아닌", "note": "CYP 효소 영향"}, {"name": "올레산", "note": "불포화지방산"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "카페인파우더",
        "slug": "food-caffeine-powder",
        "category": "기타",
        "description": "순수 카페인으로 과량 시 치명적. CYP1A2 기질로 테오필린, 클로자핀 등과 경쟁적 대사",
        "common_names": ["카페인파우더", "카페인분말", "caffeine powder"],
        "nutrients": [{"name": "카페인", "note": "CYP1A2 기질, 과량 시 심부정맥·사망 위험"}],
    },
]


async def seed_foods_expanded(dry_run: bool = False) -> dict[str, int]:
    """확장 식품 ~170종을 DB에 삽입한다."""
    stats = {"inserted": 0, "skipped": 0}

    async with async_session_factory() as session:
        for food in FOODS_EXPANDED:
            if not dry_run:
                result = await session.execute(
                    text("""
                        INSERT INTO foods (
                            name, slug, category, description,
                            common_names, nutrients
                        ) VALUES (
                            :name, :slug, :category, :description,
                            CAST(:common_names AS jsonb),
                            CAST(:nutrients AS jsonb)
                        )
                        ON CONFLICT (slug) DO NOTHING
                        RETURNING id
                    """),
                    {
                        "name": food["name"],
                        "slug": food["slug"],
                        "category": food["category"],
                        "description": food["description"],
                        "common_names": json.dumps(food["common_names"], ensure_ascii=False),
                        "nutrients": json.dumps(food["nutrients"], ensure_ascii=False),
                    },
                )
                row = result.first()
                if row:
                    stats["inserted"] += 1
                else:
                    stats["skipped"] += 1
            else:
                stats["inserted"] += 1

        if not dry_run:
            await session.commit()

    return stats


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="식품 확장 시드 데이터 적재 (~170종)")
    parser.add_argument("--dry-run", action="store_true", help="실제 DB 수정 없이 시뮬레이션")
    args = parser.parse_args()

    logger.info("식품 확장 시드 데이터 적재 시작 (dry_run=%s)", args.dry_run)
    start = time.time()
    stats = asyncio.run(seed_foods_expanded(dry_run=args.dry_run))
    elapsed = time.time() - start

    logger.info("=" * 60)
    logger.info("완료 (%.1f초) — 삽입: %d건, 건너뜀(중복): %d건",
                elapsed, stats["inserted"], stats["skipped"])
    logger.info("총 확장 식품 데이터: %d종", len(FOODS_EXPANDED))
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
