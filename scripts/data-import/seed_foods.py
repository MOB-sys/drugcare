"""식품 시드 데이터 적재 스크립트.

약물/영양제와 상호작용이 알려진 주요 식품 ~80종을 DB에 적재한다.
카테고리: 과일, 채소, 유제품, 음료, 곡류, 견과류, 해산물, 육류, 조미료/향신료, 발효식품

사용법:
    python -m scripts.data-import.seed_foods
    python -m scripts.data-import.seed_foods --dry-run
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
logger = logging.getLogger("seed_foods")


# ============================================================
# 식품 시드 데이터 (~80종)
# ============================================================

FOODS: list[dict[str, Any]] = [
    # ── 과일 ──
    {
        "name": "자몽",
        "slug": "food-grapefruit",
        "category": "과일",
        "description": "CYP3A4 효소를 억제하여 많은 약물의 혈중 농도를 높일 수 있는 대표적 식품",
        "common_names": ["자몽", "그레이프프루트", "grapefruit"],
        "nutrients": [{"name": "푸라노쿠마린", "note": "CYP3A4 억제 성분"}, {"name": "나린진", "note": "CYP3A4 억제"}],
    },
    {
        "name": "바나나",
        "slug": "food-banana",
        "category": "과일",
        "description": "칼륨이 풍부하여 ACE 억제제, 칼륨보존이뇨제와 병용 시 고칼륨혈증 위험이 있는 식품",
        "common_names": ["바나나", "banana"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 358mg"}],
    },
    {
        "name": "오렌지",
        "slug": "food-orange",
        "category": "과일",
        "description": "칼륨 함량이 높고, 오렌지주스는 일부 약물 흡수에 영향을 줄 수 있음",
        "common_names": ["오렌지", "orange", "오렌지주스"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 181mg"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "크랜베리",
        "slug": "food-cranberry",
        "category": "과일",
        "description": "와파린의 항응고 효과를 증강시킬 수 있는 식품. 크랜베리주스 포함",
        "common_names": ["크랜베리", "cranberry", "크랜베리주스"],
        "nutrients": [{"name": "플라보노이드", "note": "CYP2C9 억제 가능성"}, {"name": "살리실산", "note": "항혈소판 작용"}],
    },
    {
        "name": "아보카도",
        "slug": "food-avocado",
        "category": "과일",
        "description": "비타민K와 칼륨이 풍부하여 와파린 및 ACE 억제제와 상호작용 가능",
        "common_names": ["아보카도", "avocado"],
        "nutrients": [{"name": "비타민K", "note": "응고인자 합성"}, {"name": "칼륨", "note": "100g당 약 485mg"}],
    },
    {
        "name": "석류",
        "slug": "food-pomegranate",
        "category": "과일",
        "description": "CYP3A4 및 CYP2C9 억제 작용이 있어 일부 약물과 상호작용 가능",
        "common_names": ["석류", "pomegranate", "석류주스"],
        "nutrients": [{"name": "엘라그산", "note": "CYP 억제"}, {"name": "안토시아닌", "note": "항산화"}],
    },
    {
        "name": "망고",
        "slug": "food-mango",
        "category": "과일",
        "description": "비타민A와 섬유질이 풍부. 대량 섭취 시 와파린 효과에 영향 가능",
        "common_names": ["망고", "mango"],
        "nutrients": [{"name": "비타민A", "note": "베타카로틴"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "포도",
        "slug": "food-grape",
        "category": "과일",
        "description": "레스베라트롤 등 폴리페놀이 CYP 효소에 영향을 줄 수 있음",
        "common_names": ["포도", "grape", "포도주스"],
        "nutrients": [{"name": "레스베라트롤", "note": "CYP 억제 가능"}, {"name": "폴리페놀", "note": "항산화"}],
    },
    # ── 채소 ──
    {
        "name": "시금치",
        "slug": "food-spinach",
        "category": "채소",
        "description": "비타민K 함량이 매우 높아 와파린의 항응고 효과를 직접 길항하는 대표적 식품",
        "common_names": ["시금치", "spinach"],
        "nutrients": [{"name": "비타민K", "note": "100g당 약 483μg"}, {"name": "엽산", "note": "조혈 작용"}, {"name": "철분", "note": "비헴철"}],
    },
    {
        "name": "케일",
        "slug": "food-kale",
        "category": "채소",
        "description": "비타민K 함량이 극히 높아 와파린 복용자는 섭취량 일정하게 유지 필요",
        "common_names": ["케일", "kale"],
        "nutrients": [{"name": "비타민K", "note": "100g당 약 817μg"}, {"name": "칼슘", "note": "식물성 칼슘"}],
    },
    {
        "name": "브로콜리",
        "slug": "food-broccoli",
        "category": "채소",
        "description": "비타민K가 풍부하여 와파린과 상호작용. 갑상선 기능에도 영향 가능(고이트로겐)",
        "common_names": ["브로콜리", "broccoli"],
        "nutrients": [{"name": "비타민K", "note": "100g당 약 102μg"}, {"name": "설포라판", "note": "항산화"}, {"name": "고이트로겐", "note": "갑상선 영향"}],
    },
    {
        "name": "양배추",
        "slug": "food-cabbage",
        "category": "채소",
        "description": "비타민K가 풍부한 십자화과 채소. 와파린 복용자 주의",
        "common_names": ["양배추", "cabbage"],
        "nutrients": [{"name": "비타민K", "note": "100g당 약 76μg"}],
    },
    {
        "name": "고구마",
        "slug": "food-sweet-potato",
        "category": "채소",
        "description": "칼륨이 풍부하여 ACE 억제제, 칼륨보존이뇨제와 병용 시 고칼륨혈증 주의",
        "common_names": ["고구마", "sweet potato"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 337mg"}, {"name": "베타카로틴", "note": "비타민A 전구체"}],
    },
    {
        "name": "감자",
        "slug": "food-potato",
        "category": "채소",
        "description": "칼륨이 풍부하여 칼륨 관련 약물과 상호작용 가능",
        "common_names": ["감자", "potato"],
        "nutrients": [{"name": "칼륨", "note": "100g당 약 421mg"}],
    },
    {
        "name": "당근",
        "slug": "food-carrot",
        "category": "채소",
        "description": "베타카로틴이 풍부. 고용량 비타민A 보충제와 중복 주의",
        "common_names": ["당근", "carrot"],
        "nutrients": [{"name": "베타카로틴", "note": "비타민A 전구체"}],
    },
    {
        "name": "토마토",
        "slug": "food-tomato",
        "category": "채소",
        "description": "칼륨이 풍부하고 산성 식품으로 일부 약물 흡수에 영향 가능",
        "common_names": ["토마토", "tomato", "토마토주스"],
        "nutrients": [{"name": "칼륨", "note": "칼륨 함유"}, {"name": "리코펜", "note": "항산화"}],
    },
    {
        "name": "셀러리",
        "slug": "food-celery",
        "category": "채소",
        "description": "쿠마린 유도체를 함유하여 항응고제와 상호작용 가능",
        "common_names": ["셀러리", "celery"],
        "nutrients": [{"name": "쿠마린", "note": "항응고 작용 가능"}, {"name": "칼륨", "note": "전해질"}],
    },
    {
        "name": "파슬리",
        "slug": "food-parsley",
        "category": "채소",
        "description": "비타민K 함량이 극히 높아 와파린 복용자 주의 필요",
        "common_names": ["파슬리", "parsley"],
        "nutrients": [{"name": "비타민K", "note": "100g당 약 1,640μg"}],
    },
    # ── 유제품 ──
    {
        "name": "우유",
        "slug": "food-milk",
        "category": "유제품",
        "description": "칼슘이 풍부하여 테트라사이클린, 퀴놀론계 항생제의 흡수를 저해하는 대표적 식품",
        "common_names": ["우유", "milk", "밀크"],
        "nutrients": [{"name": "칼슘", "note": "100ml당 약 120mg"}, {"name": "카제인", "note": "약물 결합 가능"}],
    },
    {
        "name": "치즈",
        "slug": "food-cheese",
        "category": "유제품",
        "description": "티라민 함량이 높아 MAO 억제제와 병용 시 고혈압 위기(hypertensive crisis) 위험",
        "common_names": ["치즈", "cheese", "체다치즈", "브리치즈"],
        "nutrients": [{"name": "티라민", "note": "숙성치즈에 고농도"}, {"name": "칼슘", "note": "고함량"}],
    },
    {
        "name": "요거트",
        "slug": "food-yogurt",
        "category": "유제품",
        "description": "칼슘이 풍부하여 일부 항생제 흡수 저해. 프로바이오틱스 효과",
        "common_names": ["요거트", "요구르트", "yogurt"],
        "nutrients": [{"name": "칼슘", "note": "약물 킬레이트"}, {"name": "유산균", "note": "장건강"}],
    },
    {
        "name": "버터",
        "slug": "food-butter",
        "category": "유제품",
        "description": "지방 함량이 높아 지용성 약물의 흡수를 증가시킬 수 있음",
        "common_names": ["버터", "butter"],
        "nutrients": [{"name": "포화지방", "note": "지용성 약물 흡수 증가"}],
    },
    # ── 음료 ──
    {
        "name": "커피",
        "slug": "food-coffee",
        "category": "음료",
        "description": "카페인이 기관지확장제(테오필린)와 경쟁적 상호작용. 일부 약물 대사에 영향",
        "common_names": ["커피", "coffee", "카페인"],
        "nutrients": [{"name": "카페인", "note": "CYP1A2 기질"}, {"name": "클로로겐산", "note": "철분 흡수 저해"}],
    },
    {
        "name": "녹차",
        "slug": "food-green-tea",
        "category": "음료",
        "description": "카페인과 카테킨을 함유. 비타민K 포함으로 와파린과 상호작용. 철분 흡수 저해",
        "common_names": ["녹차", "green tea", "말차"],
        "nutrients": [{"name": "카페인", "note": "중추신경 자극"}, {"name": "EGCG", "note": "카테킨"}, {"name": "비타민K", "note": "미량 함유"}],
    },
    {
        "name": "알코올 (술)",
        "slug": "food-alcohol",
        "category": "음료",
        "description": "간 대사에 광범위하게 영향. 아세트아미노펜 간독성 증폭, 메트포르민 젖산증 위험 등",
        "common_names": ["술", "알코올", "맥주", "소주", "와인", "alcohol", "beer", "wine"],
        "nutrients": [{"name": "에탄올", "note": "간 CYP2E1 유도, 중추신경 억제"}],
    },
    {
        "name": "와인 (적포도주)",
        "slug": "food-wine",
        "category": "음료",
        "description": "티라민과 히스타민 함유. MAO 억제제와 상호작용. 알코올 효과 포함",
        "common_names": ["와인", "적포도주", "레드와인", "wine", "red wine"],
        "nutrients": [{"name": "에탄올", "note": "알코올"}, {"name": "티라민", "note": "MAO 억제제 상호작용"}, {"name": "레스베라트롤", "note": "항산화"}],
    },
    {
        "name": "맥주",
        "slug": "food-beer",
        "category": "음료",
        "description": "티라민 함유 발효 음료. MAO 억제제 복용자 주의. 알코올 상호작용",
        "common_names": ["맥주", "beer"],
        "nutrients": [{"name": "에탄올", "note": "알코올"}, {"name": "티라민", "note": "발효 과정 생성"}],
    },
    {
        "name": "오렌지주스",
        "slug": "food-orange-juice",
        "category": "음료",
        "description": "OATP 수송체를 억제하여 일부 약물(펙소페나딘 등)의 흡수를 감소시킬 수 있음",
        "common_names": ["오렌지주스", "orange juice", "OJ"],
        "nutrients": [{"name": "나린진", "note": "OATP 억제"}, {"name": "칼륨", "note": "고칼륨"}, {"name": "비타민C", "note": "항산화"}],
    },
    {
        "name": "자몽주스",
        "slug": "food-grapefruit-juice",
        "category": "음료",
        "description": "자몽과 동일한 CYP3A4 억제 효과. 주스 한 잔으로도 72시간까지 효소 억제",
        "common_names": ["자몽주스", "그레이프프루트주스", "grapefruit juice"],
        "nutrients": [{"name": "푸라노쿠마린", "note": "CYP3A4 비가역적 억제"}, {"name": "나린진", "note": "OATP 억제"}],
    },
    {
        "name": "에너지드링크",
        "slug": "food-energy-drink",
        "category": "음료",
        "description": "고카페인 음료. 교감신경흥분제, 심장약과 상호작용 위험",
        "common_names": ["에너지드링크", "energy drink", "레드불", "몬스터"],
        "nutrients": [{"name": "카페인", "note": "고함량 80~300mg"}, {"name": "타우린", "note": "신경 작용"}],
    },
    {
        "name": "탄산음료 (콜라)",
        "slug": "food-cola",
        "category": "음료",
        "description": "인산 함유로 칼슘 흡수 방해. 카페인 함유 제품은 카페인 상호작용",
        "common_names": ["콜라", "탄산음료", "cola", "사이다"],
        "nutrients": [{"name": "인산", "note": "칼슘 흡수 방해"}, {"name": "카페인", "note": "콜라에 함유"}],
    },
    # ── 곡류 ──
    {
        "name": "귀리 (오트밀)",
        "slug": "food-oatmeal",
        "category": "곡류",
        "description": "식이섬유가 풍부하여 일부 약물의 흡수를 지연시킬 수 있음",
        "common_names": ["귀리", "오트밀", "oatmeal", "oat"],
        "nutrients": [{"name": "베타글루칸", "note": "식이섬유, 약물 흡수 지연 가능"}],
    },
    {
        "name": "현미",
        "slug": "food-brown-rice",
        "category": "곡류",
        "description": "피트산이 미네랄 약물의 흡수를 저해할 수 있음",
        "common_names": ["현미", "brown rice"],
        "nutrients": [{"name": "피트산", "note": "미네랄 킬레이트"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "밀기울",
        "slug": "food-wheat-bran",
        "category": "곡류",
        "description": "고섬유질로 레보티록신 등 갑상선약 흡수를 감소시킬 수 있음",
        "common_names": ["밀기울", "wheat bran", "통밀"],
        "nutrients": [{"name": "식이섬유", "note": "약물 흡수 저해"}, {"name": "피트산", "note": "미네랄 킬레이트"}],
    },
    # ── 견과류 ──
    {
        "name": "호두",
        "slug": "food-walnut",
        "category": "견과류",
        "description": "오메가3(ALA)와 식이섬유 함유. 갑상선약 흡수 방해 가능",
        "common_names": ["호두", "walnut"],
        "nutrients": [{"name": "오메가3(ALA)", "note": "항염"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    {
        "name": "아몬드",
        "slug": "food-almond",
        "category": "견과류",
        "description": "비타민E와 마그네슘이 풍부. 일부 항생제 흡수에 영향 가능",
        "common_names": ["아몬드", "almond"],
        "nutrients": [{"name": "비타민E", "note": "항산화"}, {"name": "마그네슘", "note": "미네랄"}],
    },
    {
        "name": "땅콩",
        "slug": "food-peanut",
        "category": "견과류",
        "description": "MAO 억제제 복용 시 주의 필요. 레스베라트롤 미량 함유",
        "common_names": ["땅콩", "peanut", "땅콩버터"],
        "nutrients": [{"name": "나이아신", "note": "비타민B3"}, {"name": "레스베라트롤", "note": "미량"}],
    },
    {
        "name": "캐슈넛",
        "slug": "food-cashew",
        "category": "견과류",
        "description": "마그네슘과 아연이 풍부. 미네랄 관련 약물 상호작용 가능",
        "common_names": ["캐슈넛", "cashew"],
        "nutrients": [{"name": "마그네슘", "note": "미네랄"}, {"name": "아연", "note": "미네랄"}],
    },
    # ── 해산물 ──
    {
        "name": "고등어",
        "slug": "food-mackerel",
        "category": "해산물",
        "description": "히스타민 생성 가능 식품. 항히스타민제 효과 감소. 오메가3 풍부",
        "common_names": ["고등어", "mackerel"],
        "nutrients": [{"name": "히스타민", "note": "신선도 저하 시 생성"}, {"name": "오메가3", "note": "EPA/DHA"}],
    },
    {
        "name": "참치",
        "slug": "food-tuna",
        "category": "해산물",
        "description": "히스타민 생성 가능. 수은 함량 주의. 오메가3 풍부",
        "common_names": ["참치", "tuna", "참치캔"],
        "nutrients": [{"name": "히스타민", "note": "신선도 저하 시"}, {"name": "오메가3", "note": "EPA/DHA"}, {"name": "수은", "note": "중금속"}],
    },
    {
        "name": "미역/다시마",
        "slug": "food-seaweed",
        "category": "해산물",
        "description": "요오드가 매우 풍부하여 갑상선약(레보티록신)과 상호작용. 칼륨도 풍부",
        "common_names": ["미역", "다시마", "해조류", "김", "seaweed", "kelp"],
        "nutrients": [{"name": "요오드", "note": "갑상선 호르몬 합성"}, {"name": "칼륨", "note": "전해질"}, {"name": "알긴산", "note": "약물 결합 가능"}],
    },
    {
        "name": "새우",
        "slug": "food-shrimp",
        "category": "해산물",
        "description": "키틴질과 칼슘 함유. 일부 약물 흡수에 영향 가능",
        "common_names": ["새우", "shrimp"],
        "nutrients": [{"name": "칼슘", "note": "껍질 칼슘"}, {"name": "아스타잔틴", "note": "항산화"}],
    },
    # ── 육류 ──
    {
        "name": "소간 (간)",
        "slug": "food-liver",
        "category": "육류",
        "description": "비타민A가 극히 풍부하여 비타민A 과잉 위험. 철분 고함량",
        "common_names": ["소간", "간", "돼지간", "liver"],
        "nutrients": [{"name": "비타민A(레티놀)", "note": "과잉 섭취 주의"}, {"name": "헴철", "note": "고흡수율 철분"}, {"name": "비타민B12", "note": "고함량"}],
    },
    {
        "name": "숯불구이/훈제육",
        "slug": "food-chargrilled-meat",
        "category": "육류",
        "description": "다환방향족탄화수소(PAH)가 CYP1A2를 유도하여 일부 약물 대사 촉진",
        "common_names": ["숯불구이", "훈제", "바베큐", "chargrilled", "BBQ"],
        "nutrients": [{"name": "PAH", "note": "CYP1A2 유도 물질"}],
    },
    {
        "name": "가공육 (소시지/햄)",
        "slug": "food-processed-meat",
        "category": "육류",
        "description": "티라민 함유 가능. 아질산나트륨으로 인한 MAO 억제제 상호작용 주의",
        "common_names": ["소시지", "햄", "베이컨", "살라미", "processed meat"],
        "nutrients": [{"name": "티라민", "note": "MAO 상호작용"}, {"name": "아질산나트륨", "note": "식품첨가물"}],
    },
    # ── 조미료/향신료 ──
    {
        "name": "마늘",
        "slug": "food-garlic",
        "category": "조미료/향신료",
        "description": "항혈소판 작용으로 항응고제와 병용 시 출혈 위험 증가. CYP3A4 유도 가능",
        "common_names": ["마늘", "garlic", "다진마늘"],
        "nutrients": [{"name": "알리신", "note": "항혈소판 작용"}, {"name": "아조엔", "note": "항혈소판"}, {"name": "디알릴디설파이드", "note": "CYP2E1 억제"}],
    },
    {
        "name": "생강",
        "slug": "food-ginger",
        "category": "조미료/향신료",
        "description": "항혈소판 및 항응고 작용으로 항응고제, 항혈소판제와 병용 시 출혈 위험",
        "common_names": ["생강", "ginger", "건강"],
        "nutrients": [{"name": "진저롤", "note": "항혈소판 작용"}, {"name": "쇼가올", "note": "항염 작용"}],
    },
    {
        "name": "강황/울금 (커큐민)",
        "slug": "food-turmeric",
        "category": "조미료/향신료",
        "description": "CYP 효소 억제 및 항혈소판 작용. 항응고제와 상호작용 가능",
        "common_names": ["강황", "울금", "커큐민", "turmeric", "curcumin"],
        "nutrients": [{"name": "커큐민", "note": "CYP3A4/CYP1A2 억제"}, {"name": "항혈소판 성분", "note": "출혈 위험"}],
    },
    {
        "name": "후추 (흑후추)",
        "slug": "food-black-pepper",
        "category": "조미료/향신료",
        "description": "피페린이 CYP3A4를 억제하여 많은 약물의 생체이용률을 높일 수 있음",
        "common_names": ["후추", "흑후추", "black pepper", "피페린"],
        "nutrients": [{"name": "피페린", "note": "CYP3A4 억제, 약물 생체이용률 증가"}],
    },
    {
        "name": "계피",
        "slug": "food-cinnamon",
        "category": "조미료/향신료",
        "description": "쿠마린 함유로 항응고제와 상호작용 가능. 혈당 강하 작용",
        "common_names": ["계피", "시나몬", "cinnamon"],
        "nutrients": [{"name": "쿠마린", "note": "간독성/항응고"}, {"name": "시나몬알데히드", "note": "혈당 강하"}],
    },
    {
        "name": "감초",
        "slug": "food-licorice",
        "category": "조미료/향신료",
        "description": "위알도스테론증을 유발하여 이뇨제, 항고혈압제와 심각한 상호작용. 저칼륨혈증 유발",
        "common_names": ["감초", "licorice", "감초뿌리"],
        "nutrients": [{"name": "글리시리진", "note": "11β-HSD2 억제 → 위알도스테론증"}, {"name": "글라브리딘", "note": "CYP 억제"}],
    },
    {
        "name": "고추/캡사이신",
        "slug": "food-chili-pepper",
        "category": "조미료/향신료",
        "description": "위장관 자극으로 일부 약물 흡수 변화. ACE 억제제와 기침 상호작용",
        "common_names": ["고추", "캡사이신", "chili", "capsaicin", "청양고추"],
        "nutrients": [{"name": "캡사이신", "note": "위장관 자극, TRPV1 수용체 작용"}],
    },
    {
        "name": "고수 (코리안더)",
        "slug": "food-coriander",
        "category": "조미료/향신료",
        "description": "혈당 강하 작용으로 당뇨약과 상호작용 가능",
        "common_names": ["고수", "코리안더", "실란트로", "coriander", "cilantro"],
        "nutrients": [{"name": "리날로올", "note": "혈당 강하"}, {"name": "항산화 성분", "note": "폴리페놀"}],
    },
    {
        "name": "겨자",
        "slug": "food-mustard",
        "category": "조미료/향신료",
        "description": "이소티오시아네이트가 CYP 효소에 영향. 갑상선 기능 관련 고이트로겐 함유",
        "common_names": ["겨자", "머스타드", "mustard"],
        "nutrients": [{"name": "이소티오시아네이트", "note": "CYP 영향"}, {"name": "고이트로겐", "note": "갑상선 영향"}],
    },
    # ── 두류/콩류 ──
    {
        "name": "두부",
        "slug": "food-tofu",
        "category": "곡류",
        "description": "이소플라본(식물성 에스트로겐) 함유. 갑상선약, 에스트로겐 관련 약물과 상호작용",
        "common_names": ["두부", "tofu"],
        "nutrients": [{"name": "이소플라본", "note": "식물성 에스트로겐"}, {"name": "칼슘", "note": "응고제 유래"}],
    },
    {
        "name": "두유",
        "slug": "food-soy-milk",
        "category": "음료",
        "description": "이소플라본 함유. 레보티록신 흡수 저해. 에스트로겐 관련 약물 상호작용",
        "common_names": ["두유", "soy milk", "콩우유"],
        "nutrients": [{"name": "이소플라본", "note": "갑상선약 흡수 저해"}, {"name": "식물성 단백질", "note": "콩 유래"}],
    },
    {
        "name": "콩 (대두)",
        "slug": "food-soybean",
        "category": "곡류",
        "description": "이소플라본이 갑상선약, 타목시펜, 와파린과 상호작용 가능",
        "common_names": ["콩", "대두", "soybean", "soy"],
        "nutrients": [{"name": "이소플라본(제니스테인)", "note": "식물성 에스트로겐"}, {"name": "피트산", "note": "미네랄 흡수 저해"}],
    },
    {
        "name": "팥",
        "slug": "food-red-bean",
        "category": "곡류",
        "description": "칼륨이 풍부하여 칼륨 관련 약물 복용자 주의",
        "common_names": ["팥", "red bean", "소두"],
        "nutrients": [{"name": "칼륨", "note": "고함량"}, {"name": "식이섬유", "note": "약물 흡수 지연"}],
    },
    # ── 발효식품 ──
    {
        "name": "간장",
        "slug": "food-soy-sauce",
        "category": "발효식품",
        "description": "티라민 함유 발효식품. MAO 억제제 복용자 고혈압 위기 위험",
        "common_names": ["간장", "soy sauce", "진간장", "국간장"],
        "nutrients": [{"name": "티라민", "note": "발효 과정 생성"}, {"name": "나트륨", "note": "고함량"}],
    },
    {
        "name": "된장",
        "slug": "food-doenjang",
        "category": "발효식품",
        "description": "티라민 함유 발효식품. MAO 억제제와 상호작용. 나트륨 고함량",
        "common_names": ["된장", "doenjang", "대두장"],
        "nutrients": [{"name": "티라민", "note": "MAO 상호작용"}, {"name": "이소플라본", "note": "식물성 에스트로겐"}, {"name": "나트륨", "note": "고함량"}],
    },
    {
        "name": "청국장",
        "slug": "food-cheonggukjang",
        "category": "발효식품",
        "description": "비타민K2 함유 발효식품. 와파린 복용자 주의. 티라민도 함유",
        "common_names": ["청국장", "cheonggukjang"],
        "nutrients": [{"name": "비타민K2", "note": "와파린 길항"}, {"name": "티라민", "note": "MAO 상호작용"}, {"name": "나토키나아제", "note": "항혈전"}],
    },
    {
        "name": "김치",
        "slug": "food-kimchi",
        "category": "발효식품",
        "description": "비타민K와 티라민 함유 가능. 유산균 풍부. MAO 억제제 주의",
        "common_names": ["김치", "kimchi"],
        "nutrients": [{"name": "유산균", "note": "프로바이오틱스"}, {"name": "비타민K", "note": "미량"}, {"name": "티라민", "note": "숙성 시 생성"}],
    },
    {
        "name": "낫토",
        "slug": "food-natto",
        "category": "발효식품",
        "description": "비타민K2가 매우 풍부하여 와파린 효과를 강력히 길항. 나토키나아제 함유",
        "common_names": ["낫토", "natto", "낫또"],
        "nutrients": [{"name": "비타민K2(MK-7)", "note": "100g당 약 1,000μg"}, {"name": "나토키나아제", "note": "혈전 용해"}],
    },
    {
        "name": "식초",
        "slug": "food-vinegar",
        "category": "발효식품",
        "description": "위산도를 높여 일부 약물 흡수에 영향. 혈당 강하 작용",
        "common_names": ["식초", "사과식초", "vinegar"],
        "nutrients": [{"name": "초산", "note": "위산도 변화"}, {"name": "아세트산", "note": "혈당 강하 효과"}],
    },
    {
        "name": "맥주효모",
        "slug": "food-brewers-yeast",
        "category": "발효식품",
        "description": "티라민 함유 가능. MAO 억제제 복용자 주의. B군 비타민 풍부",
        "common_names": ["맥주효모", "brewer's yeast"],
        "nutrients": [{"name": "티라민", "note": "MAO 상호작용"}, {"name": "비타민B군", "note": "B1, B2, B6"}, {"name": "크롬", "note": "미량원소"}],
    },
    # ── 기타 식품 ──
    {
        "name": "꿀",
        "slug": "food-honey",
        "category": "조미료/향신료",
        "description": "MAO 억제제 복용자 일부 꿀에서 티라민 유사 물질 주의. 혈당 영향",
        "common_names": ["꿀", "honey", "벌꿀"],
        "nutrients": [{"name": "과당", "note": "혈당 영향"}, {"name": "폴리페놀", "note": "항산화"}],
    },
    {
        "name": "다크초콜릿",
        "slug": "food-dark-chocolate",
        "category": "조미료/향신료",
        "description": "카페인과 테오브로민 함유. 티라민 함유. MAO 억제제 복용자 주의",
        "common_names": ["다크초콜릿", "초콜릿", "dark chocolate", "chocolate", "카카오"],
        "nutrients": [{"name": "테오브로민", "note": "카페인 유사체"}, {"name": "카페인", "note": "미량"}, {"name": "티라민", "note": "발효 카카오"}],
    },
    {
        "name": "세인트존스워트 (허브차)",
        "slug": "food-st-johns-wort",
        "category": "음료",
        "description": "CYP3A4, CYP1A2, CYP2C9 등 다수 효소를 유도하여 매우 많은 약물과 심각한 상호작용",
        "common_names": ["세인트존스워트", "St. John's Wort", "관엽연교", "성요한초"],
        "nutrients": [{"name": "히페리신", "note": "항우울 성분"}, {"name": "하이퍼포린", "note": "강력한 CYP 유도제, PXR 활성화"}],
    },
    {
        "name": "감귤류 (레몬/라임)",
        "slug": "food-citrus",
        "category": "과일",
        "description": "비타민C 풍부. 일부 감귤류는 CYP 효소에 영향 가능",
        "common_names": ["레몬", "라임", "감귤", "귤", "lemon", "lime", "citrus"],
        "nutrients": [{"name": "비타민C", "note": "항산화"}, {"name": "구연산", "note": "위산도 변화"}],
    },
    {
        "name": "키위",
        "slug": "food-kiwi",
        "category": "과일",
        "description": "칼륨과 비타민C가 풍부. 항혈소판 작용 보고",
        "common_names": ["키위", "kiwi", "참다래"],
        "nutrients": [{"name": "칼륨", "note": "전해질"}, {"name": "비타민C", "note": "항산화"}, {"name": "액티니딘", "note": "단백질 분해 효소"}],
    },
    {
        "name": "수박",
        "slug": "food-watermelon",
        "category": "과일",
        "description": "칼륨이 풍부하여 칼륨 관련 약물 복용자 대량 섭취 시 주의",
        "common_names": ["수박", "watermelon"],
        "nutrients": [{"name": "칼륨", "note": "전해질"}, {"name": "시트룰린", "note": "혈관 확장"}],
    },
    {
        "name": "양파",
        "slug": "food-onion",
        "category": "채소",
        "description": "항혈소판 작용이 있어 항응고제와 병용 시 출혈 위험 약간 증가",
        "common_names": ["양파", "onion"],
        "nutrients": [{"name": "퀘르세틴", "note": "항혈소판"}, {"name": "알리신", "note": "황화합물"}],
    },
    {
        "name": "부추",
        "slug": "food-chives",
        "category": "채소",
        "description": "비타민K와 황화합물 함유. 항응고제 복용자 주의",
        "common_names": ["부추", "chives", "정구지"],
        "nutrients": [{"name": "비타민K", "note": "응고인자"}, {"name": "황화합물", "note": "마늘류 성분"}],
    },
    {
        "name": "깻잎",
        "slug": "food-perilla-leaf",
        "category": "채소",
        "description": "비타민K가 풍부한 한국 고유 엽채소. 와파린 복용자 주의",
        "common_names": ["깻잎", "perilla leaf", "들깻잎"],
        "nutrients": [{"name": "비타민K", "note": "고함량"}, {"name": "로즈마린산", "note": "항산화"}],
    },
    {
        "name": "아스파라거스",
        "slug": "food-asparagus",
        "category": "채소",
        "description": "비타민K 함유. 이뇨 작용이 있어 리튬 약물 농도에 영향 가능",
        "common_names": ["아스파라거스", "asparagus"],
        "nutrients": [{"name": "비타민K", "note": "응고인자"}, {"name": "아스파라긴", "note": "이뇨 작용"}],
    },
    {
        "name": "쑥",
        "slug": "food-mugwort",
        "category": "채소",
        "description": "비타민K 함유. 항응고제 복용자 과량 섭취 주의. 한약재로도 사용",
        "common_names": ["쑥", "mugwort", "애엽"],
        "nutrients": [{"name": "비타민K", "note": "응고인자"}, {"name": "치네올", "note": "정유 성분"}],
    },
    {
        "name": "인삼차/인삼",
        "slug": "food-ginseng",
        "category": "음료",
        "description": "항응고제 효과 변동, 혈당강하제와 저혈당 위험. 면역 조절 작용",
        "common_names": ["인삼", "인삼차", "ginseng", "수삼"],
        "nutrients": [{"name": "진세노사이드", "note": "항혈소판, 혈당 강하"}, {"name": "폴리아세틸렌", "note": "항염"}],
    },
    {
        "name": "페퍼민트",
        "slug": "food-peppermint",
        "category": "음료",
        "description": "CYP3A4 억제 가능. 위식도역류약(PPI) 효과 감소 가능",
        "common_names": ["페퍼민트", "박하", "peppermint", "민트"],
        "nutrients": [{"name": "멘톨", "note": "CYP3A4 억제 가능"}, {"name": "로즈마린산", "note": "항산화"}],
    },
    {
        "name": "카모마일",
        "slug": "food-chamomile",
        "category": "음료",
        "description": "쿠마린 유도체 함유로 항응고제와 상호작용 가능. 진정 작용",
        "common_names": ["카모마일", "캐모마일", "chamomile"],
        "nutrients": [{"name": "아피제닌", "note": "진정 작용"}, {"name": "쿠마린", "note": "항응고 작용"}],
    },
]


async def seed_foods(dry_run: bool = False) -> dict[str, int]:
    """식품 ~80종을 DB에 삽입한다."""
    stats = {"inserted": 0, "skipped": 0}

    async with async_session_factory() as session:
        for food in FOODS:
            if not dry_run:
                result = await session.execute(
                    text("""
                        INSERT INTO foods (
                            name, slug, category, description,
                            common_names, nutrients, source
                        ) VALUES (
                            :name, :slug, :category, :description,
                            CAST(:common_names AS jsonb),
                            CAST(:nutrients AS jsonb),
                            :source
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
                        "source": "seed_evidence_based",
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

    parser = argparse.ArgumentParser(description="식품 시드 데이터 적재")
    parser.add_argument("--dry-run", action="store_true", help="실제 DB 수정 없이 시뮬레이션")
    args = parser.parse_args()

    logger.info("식품 시드 데이터 적재 시작 (dry_run=%s)", args.dry_run)
    start = time.time()
    stats = asyncio.run(seed_foods(dry_run=args.dry_run))
    elapsed = time.time() - start

    logger.info("=" * 60)
    logger.info("완료 (%.1f초) — 삽입: %d건, 건너뜀(중복): %d건",
                elapsed, stats["inserted"], stats["skipped"])
    logger.info("총 식품 데이터: %d종", len(FOODS))
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
