"""영양제 시드 데이터 + 상호작용 룰 적재 스크립트.

인기 영양제 50종 + 약물-영양제 상호작용 + 영양제-영양제 상호작용을
DB에 적재한다. 의학적 근거가 확립된 상호작용만 포함.

사용법:
    python -m scripts.data-import.seed_supplements
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
logger = logging.getLogger("seed_supplements")

# ─────────────────────────────────────────────────────────
# 1. 영양제 시드 데이터 (50종)
# ─────────────────────────────────────────────────────────

SUPPLEMENTS: list[dict[str, Any]] = [
    # ── 비타민 ──
    {
        "product_name": "비타민D (콜레칼시페롤)",
        "main_ingredient": "콜레칼시페롤",
        "category": "비타민",
        "ingredients": [{"name": "콜레칼시페롤(비타민D3)", "amount": "1000", "unit": "IU"}],
        "functionality": "칼슘과 인이 흡수되고 이용되는데 필요. 뼈의 형성과 유지에 필요. 골다공증 발생 위험 감소에 도움.",
        "precautions": "고칼슘혈증 환자는 섭취 주의. 과량 섭취 시 고칼슘혈증, 고칼슘뇨증 유발 가능.",
        "intake_method": "1일 1회, 1회 1정, 식후 복용 권장.",
    },
    {
        "product_name": "비타민C (아스코르브산)",
        "main_ingredient": "아스코르브산",
        "category": "비타민",
        "ingredients": [{"name": "아스코르브산(비타민C)", "amount": "500", "unit": "mg"}],
        "functionality": "결합조직 형성과 기능 유지에 필요. 철의 흡수에 필요. 항산화 작용을 하여 유해산소로부터 세포를 보호.",
        "precautions": "과량 섭취 시 소화장애, 설사 유발 가능. 신장결석 병력자는 주의.",
        "intake_method": "1일 1~2회, 1회 1정.",
    },
    {
        "product_name": "비타민B군 복합 (B-Complex)",
        "main_ingredient": "비타민B1, B2, B6, B12, 나이아신, 판토텐산",
        "category": "비타민",
        "ingredients": [
            {"name": "티아민(B1)", "amount": "50", "unit": "mg"},
            {"name": "리보플라빈(B2)", "amount": "50", "unit": "mg"},
            {"name": "피리독신(B6)", "amount": "50", "unit": "mg"},
            {"name": "시아노코발라민(B12)", "amount": "100", "unit": "μg"},
            {"name": "나이아신아마이드", "amount": "50", "unit": "mg"},
            {"name": "판토텐산칼슘", "amount": "50", "unit": "mg"},
        ],
        "functionality": "체내 에너지 생성에 필요. 신경계의 정상적인 기능 유지.",
        "precautions": "고용량 B6(100mg 이상) 장기 복용 시 말초신경병증 주의.",
        "intake_method": "1일 1회, 1회 1정, 식후 복용.",
    },
    {
        "product_name": "비타민B12 (코발라민)",
        "main_ingredient": "시아노코발라민",
        "category": "비타민",
        "ingredients": [{"name": "시아노코발라민(비타민B12)", "amount": "1000", "unit": "μg"}],
        "functionality": "정상적인 엽산 대사에 필요. 적혈구 형성에 필요.",
        "precautions": "특별한 부작용 보고 적음.",
        "intake_method": "1일 1회, 1회 1정.",
    },
    {
        "product_name": "엽산 (폴산)",
        "main_ingredient": "엽산",
        "category": "비타민",
        "ingredients": [{"name": "엽산(비타민B9)", "amount": "400", "unit": "μg"}],
        "functionality": "세포와 혈액 생성에 필요. 태아 신경관의 정상 발달에 필요. 호모시스테인 수준을 정상으로 유지.",
        "precautions": "고용량 엽산은 B12 결핍 증상을 은폐할 수 있으므로 B12 수치 확인 권장.",
        "intake_method": "1일 1회, 1회 1정. 임산부는 임신 전부터 복용 권장.",
    },
    {
        "product_name": "비타민E (토코페롤)",
        "main_ingredient": "d-알파-토코페롤",
        "category": "비타민",
        "ingredients": [{"name": "d-알파-토코페롤(비타민E)", "amount": "200", "unit": "IU"}],
        "functionality": "항산화 작용을 하여 유해산소로부터 세포를 보호.",
        "precautions": "고용량(400IU 이상) 복용 시 출혈 위험 증가. 항응고제 복용자 주의.",
        "intake_method": "1일 1회, 1회 1캡슐, 식후 복용.",
    },
    {
        "product_name": "비타민A (베타카로틴)",
        "main_ingredient": "베타카로틴",
        "category": "비타민",
        "ingredients": [{"name": "베타카로틴(프로비타민A)", "amount": "6", "unit": "mg"}],
        "functionality": "어두운 곳에서 시각 적응을 위해 필요. 피부와 점막의 건강 유지에 필요.",
        "precautions": "임산부는 과량 섭취 주의(기형 유발 가능). 흡연자의 베타카로틴 고용량 섭취 주의.",
        "intake_method": "1일 1회, 1회 1캡슐.",
    },
    {
        "product_name": "비타민K2 (메나퀴논-7)",
        "main_ingredient": "메나퀴논-7",
        "category": "비타민",
        "ingredients": [{"name": "메나퀴논-7(비타민K2)", "amount": "100", "unit": "μg"}],
        "functionality": "정상적인 혈액응고에 필요. 뼈의 구성에 필요.",
        "precautions": "항응고제(와파린) 복용자는 반드시 의사와 상담 후 복용.",
        "intake_method": "1일 1회, 1회 1캡슐, 식후 복용.",
    },
    {
        "product_name": "비오틴 (비타민B7)",
        "main_ingredient": "비오틴",
        "category": "비타민",
        "ingredients": [{"name": "비오틴(비타민B7)", "amount": "5000", "unit": "μg"}],
        "functionality": "지방, 탄수화물, 단백질 대사와 에너지 생성에 필요.",
        "precautions": "고용량 복용 시 갑상선 기능 검사 결과 왜곡 가능. 검사 1주일 전 중단 권장.",
        "intake_method": "1일 1회, 1회 1정.",
    },
    {
        "product_name": "종합비타민 (멀티비타민)",
        "main_ingredient": "비타민A, B군, C, D, E, K, 미네랄",
        "category": "비타민",
        "ingredients": [
            {"name": "비타민A", "amount": "700", "unit": "μg"},
            {"name": "비타민C", "amount": "100", "unit": "mg"},
            {"name": "비타민D", "amount": "400", "unit": "IU"},
            {"name": "비타민E", "amount": "11", "unit": "mg"},
            {"name": "비타민B1", "amount": "1.2", "unit": "mg"},
            {"name": "비타민B2", "amount": "1.4", "unit": "mg"},
            {"name": "비타민B6", "amount": "1.5", "unit": "mg"},
            {"name": "비타민B12", "amount": "2.4", "unit": "μg"},
            {"name": "엽산", "amount": "400", "unit": "μg"},
            {"name": "아연", "amount": "8.5", "unit": "mg"},
        ],
        "functionality": "체내 다양한 대사과정에 필요한 비타민과 미네랄을 종합적으로 보충.",
        "precautions": "다른 비타민/미네랄 보충제와 중복 섭취 주의.",
        "intake_method": "1일 1회, 1회 1정, 식후 복용.",
    },
    # ── 미네랄 ──
    {
        "product_name": "칼슘 (탄산칼슘)",
        "main_ingredient": "탄산칼슘",
        "category": "미네랄",
        "ingredients": [{"name": "탄산칼슘", "amount": "500", "unit": "mg"}],
        "functionality": "뼈와 치아 형성에 필요. 신경과 근육 기능 유지에 필요. 정상적인 혈액응고에 필요.",
        "precautions": "과량 섭취 시 변비, 소화불량 가능. 신장결석 병력자 주의.",
        "intake_method": "1일 1~2회, 1회 1정. 비타민D와 함께 복용 시 흡수율 증가.",
    },
    {
        "product_name": "마그네슘 (산화마그네슘)",
        "main_ingredient": "산화마그네슘",
        "category": "미네랄",
        "ingredients": [{"name": "산화마그네슘", "amount": "400", "unit": "mg"}],
        "functionality": "에너지 이용에 필요. 신경과 근육 기능 유지에 필요.",
        "precautions": "과량 섭취 시 설사 유발. 신장 기능 저하자 주의.",
        "intake_method": "1일 1회, 1회 1정, 취침 전 복용 권장.",
    },
    {
        "product_name": "철분 (황산제일철)",
        "main_ingredient": "황산제일철",
        "category": "미네랄",
        "ingredients": [{"name": "황산제일철", "amount": "65", "unit": "mg"}],
        "functionality": "체내 산소운반과 혈액생성에 필요. 에너지 생성에 필요.",
        "precautions": "과량 섭취 시 변비, 위장장애. 비타민C와 함께 복용 시 흡수율 증가.",
        "intake_method": "1일 1회, 1회 1정, 공복 복용 권장.",
    },
    {
        "product_name": "아연 (황산아연)",
        "main_ingredient": "황산아연",
        "category": "미네랄",
        "ingredients": [{"name": "황산아연", "amount": "15", "unit": "mg"}],
        "functionality": "정상적인 면역기능에 필요. 정상적인 세포분열에 필요.",
        "precautions": "고용량(50mg 이상) 장기 복용 시 구리 결핍 유발 가능.",
        "intake_method": "1일 1회, 1회 1정, 식후 복용.",
    },
    {
        "product_name": "셀레늄",
        "main_ingredient": "셀레늄",
        "category": "미네랄",
        "ingredients": [{"name": "셀렌산나트륨", "amount": "50", "unit": "μg"}],
        "functionality": "유해산소로부터 세포를 보호하는데 필요.",
        "precautions": "과량 섭취 시 셀레늄 중독 주의(탈모, 손톱 변형).",
        "intake_method": "1일 1회, 1회 1정.",
    },
    {
        "product_name": "구리",
        "main_ingredient": "황산구리",
        "category": "미네랄",
        "ingredients": [{"name": "황산구리", "amount": "0.8", "unit": "mg"}],
        "functionality": "철의 운반과 이용에 필요. 유해산소로부터 세포를 보호하는데 필요.",
        "precautions": "아연 고용량 보충 시 구리 결핍 방지를 위해 복용 권장.",
        "intake_method": "1일 1회, 1회 1정.",
    },
    {
        "product_name": "칼륨",
        "main_ingredient": "염화칼륨",
        "category": "미네랄",
        "ingredients": [{"name": "염화칼륨", "amount": "99", "unit": "mg"}],
        "functionality": "체내 수분 균형 및 정상적인 근육 수축에 필요.",
        "precautions": "ACE억제제/ARB 혈압약 복용자는 반드시 의사와 상담. 고칼륨혈증 위험.",
        "intake_method": "1일 1회, 1회 1정, 식후 복용.",
    },
    {
        "product_name": "크롬",
        "main_ingredient": "피콜린산크롬",
        "category": "미네랄",
        "ingredients": [{"name": "피콜린산크롬", "amount": "200", "unit": "μg"}],
        "functionality": "체내 탄수화물, 지방, 단백질 대사에 필요.",
        "precautions": "당뇨약 복용자는 저혈당 위험으로 의사 상담 필요.",
        "intake_method": "1일 1회, 1회 1정.",
    },
    {
        "product_name": "요오드",
        "main_ingredient": "요오드화칼륨",
        "category": "미네랄",
        "ingredients": [{"name": "요오드화칼륨", "amount": "150", "unit": "μg"}],
        "functionality": "갑상선 호르몬의 합성에 필요. 에너지 생성에 필요.",
        "precautions": "갑상선 질환자는 의사와 상담 후 섭취.",
        "intake_method": "1일 1회, 1회 1정.",
    },
    # ── 오메가 / 지방산 ──
    {
        "product_name": "오메가3 (EPA/DHA)",
        "main_ingredient": "EPA, DHA",
        "category": "오메가지방산",
        "ingredients": [
            {"name": "EPA", "amount": "600", "unit": "mg"},
            {"name": "DHA", "amount": "400", "unit": "mg"},
        ],
        "functionality": "혈중 중성지질 개선, 혈행 개선에 도움. 건조한 눈을 개선하여 눈 건강에 도움.",
        "precautions": "고용량 복용 시 출혈 경향 증가. 수술 전 중단 권장. 항응고제 복용자 주의.",
        "intake_method": "1일 1~2회, 1회 1캡슐, 식후 복용.",
    },
    {
        "product_name": "크릴오일",
        "main_ingredient": "크릴오일(인지질 결합 오메가3)",
        "category": "오메가지방산",
        "ingredients": [
            {"name": "크릴오일", "amount": "1000", "unit": "mg"},
            {"name": "EPA", "amount": "120", "unit": "mg"},
            {"name": "DHA", "amount": "55", "unit": "mg"},
            {"name": "아스타잔틴", "amount": "100", "unit": "μg"},
        ],
        "functionality": "혈중 중성지질 개선에 도움. 인지질 형태로 흡수율 우수.",
        "precautions": "갑각류 알레르기 주의. 항응고제 복용자 주의.",
        "intake_method": "1일 1~2회, 1회 1캡슐, 식후.",
    },
    {
        "product_name": "감마리놀렌산 (GLA)",
        "main_ingredient": "달맞이꽃종자유",
        "category": "오메가지방산",
        "ingredients": [{"name": "감마리놀렌산(GLA)", "amount": "300", "unit": "mg"}],
        "functionality": "피부 건강에 도움. 월경 전 불편함 개선에 도움.",
        "precautions": "간질 병력자 주의. 항응고제 병용 시 출혈 위험.",
        "intake_method": "1일 2~3회, 1회 1캡슐, 식후.",
    },
    # ── 장 건강 ──
    {
        "product_name": "프로바이오틱스 (유산균)",
        "main_ingredient": "락토바실러스, 비피도박테리움",
        "category": "프로바이오틱스",
        "ingredients": [
            {"name": "락토바실러스 애시도필루스", "amount": "50", "unit": "억CFU"},
            {"name": "비피도박테리움 롱검", "amount": "50", "unit": "억CFU"},
        ],
        "functionality": "유익균 증식 및 유해균 억제. 배변활동 원활에 도움.",
        "precautions": "면역억제제 복용자, 중환자 주의. 항생제와 동시 복용 시 효과 감소.",
        "intake_method": "1일 1회, 1회 1캡슐. 항생제 복용 시 2시간 간격 유지.",
    },
    # ── 간 건강 ──
    {
        "product_name": "밀크씨슬 (실리마린)",
        "main_ingredient": "밀크씨슬추출물(실리마린)",
        "category": "간건강",
        "ingredients": [{"name": "밀크씨슬추출물(실리마린)", "amount": "130", "unit": "mg"}],
        "functionality": "간 건강에 도움을 줄 수 있음.",
        "precautions": "두통, 소화장애 가능. 에스트로겐 유사 작용 가능성 보고.",
        "intake_method": "1일 1~3회, 1회 1정, 식전 또는 식후.",
    },
    # ── 눈 건강 ──
    {
        "product_name": "루테인/지아잔틴",
        "main_ingredient": "루테인, 지아잔틴",
        "category": "눈건강",
        "ingredients": [
            {"name": "루테인", "amount": "20", "unit": "mg"},
            {"name": "지아잔틴", "amount": "4", "unit": "mg"},
        ],
        "functionality": "노화로 인해 감소될 수 있는 황반 색소 밀도를 유지하여 눈 건강에 도움.",
        "precautions": "흡연자의 베타카로틴 고용량 동시 섭취 주의.",
        "intake_method": "1일 1회, 1회 1캡슐, 식후 복용.",
    },
    # ── 관절 건강 ──
    {
        "product_name": "글루코사민",
        "main_ingredient": "글루코사민황산염",
        "category": "관절건강",
        "ingredients": [{"name": "글루코사민황산염", "amount": "1500", "unit": "mg"}],
        "functionality": "관절 및 연골 건강에 도움.",
        "precautions": "갑각류 유래 원료 알레르기 주의. 항응고제(와파린) 병용 시 INR 상승 보고.",
        "intake_method": "1일 1~3회, 1회 1정, 식후.",
    },
    {
        "product_name": "MSM (메틸설포닐메탄)",
        "main_ingredient": "MSM",
        "category": "관절건강",
        "ingredients": [{"name": "메틸설포닐메탄(MSM)", "amount": "1500", "unit": "mg"}],
        "functionality": "관절 및 연골 건강에 도움.",
        "precautions": "위장 장애, 두통 가능. 혈액희석제 복용 시 주의.",
        "intake_method": "1일 2~3회, 1회 1정.",
    },
    {
        "product_name": "콘드로이틴",
        "main_ingredient": "콘드로이틴황산나트륨",
        "category": "관절건강",
        "ingredients": [{"name": "콘드로이틴황산나트륨", "amount": "400", "unit": "mg"}],
        "functionality": "관절 연골의 구성 성분으로 관절 건강에 도움.",
        "precautions": "항응고제 복용자 주의(출혈 경향 증가 가능).",
        "intake_method": "1일 2~3회, 1회 1캡슐.",
    },
    # ── 항산화 ──
    {
        "product_name": "코엔자임Q10 (CoQ10)",
        "main_ingredient": "코엔자임Q10",
        "category": "항산화",
        "ingredients": [{"name": "코엔자임Q10(유비퀴논)", "amount": "100", "unit": "mg"}],
        "functionality": "항산화에 도움을 줄 수 있음. 높은 혈압 감소에 도움.",
        "precautions": "혈압약, 항응고제 병용 시 효과 변동 가능. 의사 상담 권장.",
        "intake_method": "1일 1~2회, 1회 1캡슐, 식후.",
    },
    {
        "product_name": "아스타잔틴",
        "main_ingredient": "헤마토코쿠스추출물",
        "category": "항산화",
        "ingredients": [{"name": "아스타잔틴", "amount": "4", "unit": "mg"}],
        "functionality": "눈의 피로도 개선에 도움. 항산화 작용.",
        "precautions": "특별한 부작용 보고 적음.",
        "intake_method": "1일 1회, 1회 1캡슐, 식후.",
    },
    {
        "product_name": "알파리포산",
        "main_ingredient": "알파리포산",
        "category": "항산화",
        "ingredients": [{"name": "알파리포산", "amount": "200", "unit": "mg"}],
        "functionality": "항산화에 도움. 체내 에너지 대사에 관여.",
        "precautions": "당뇨약 복용자는 저혈당 위험으로 의사 상담 필요.",
        "intake_method": "1일 1회, 1회 1정, 공복 복용.",
    },
    # ── 전통 한방 / 허브 ──
    {
        "product_name": "홍삼 (Korean Red Ginseng)",
        "main_ingredient": "홍삼농축액(진세노사이드)",
        "category": "면역력",
        "ingredients": [{"name": "홍삼농축액(Rg1+Rb1+Rg3)", "amount": "3", "unit": "mg"}],
        "functionality": "면역력 증진. 피로 개선. 혈소판 응집 억제를 통한 혈액흐름에 도움.",
        "precautions": "항응고제, 혈압약, 당뇨약 복용자 주의. 자가면역질환자 주의.",
        "intake_method": "1일 1~3회, 1회 1포.",
    },
    {
        "product_name": "프로폴리스",
        "main_ingredient": "프로폴리스추출물",
        "category": "면역력",
        "ingredients": [{"name": "프로폴리스추출물(플라보노이드)", "amount": "17", "unit": "mg"}],
        "functionality": "항산화에 도움. 구강 내 항균 작용에 도움.",
        "precautions": "꿀벌 알레르기 주의. 천식 환자 주의.",
        "intake_method": "1일 1~2회, 1회 1캡슐.",
    },
    {
        "product_name": "에키네시아",
        "main_ingredient": "에키네시아추출물",
        "category": "면역력",
        "ingredients": [{"name": "에키네시아 퍼퓨리아 추출물", "amount": "400", "unit": "mg"}],
        "functionality": "면역 기능 지원에 도움.",
        "precautions": "자가면역질환자, 면역억제제 복용자 금기. 국화과 알레르기 주의.",
        "intake_method": "1일 2~3회, 1회 1캡슐. 연속 8주 이상 복용 비권장.",
    },
    {
        "product_name": "은행잎 추출물 (징코)",
        "main_ingredient": "은행잎추출물(징코빌로바)",
        "category": "뇌건강",
        "ingredients": [{"name": "은행잎추출물(플라보노이드 배당체)", "amount": "120", "unit": "mg"}],
        "functionality": "기억력 개선에 도움. 혈행 개선에 도움.",
        "precautions": "항응고제, 항혈소판제 복용자 금기(출혈 위험). 수술 2주 전 중단.",
        "intake_method": "1일 2~3회, 1회 1정.",
    },
    {
        "product_name": "세인트존스워트 (관엽연교)",
        "main_ingredient": "세인트존스워트추출물(히페리신)",
        "category": "기분개선",
        "ingredients": [{"name": "세인트존스워트추출물(히페리신 0.3%)", "amount": "300", "unit": "mg"}],
        "functionality": "기분 개선 및 정서적 안정에 도움.",
        "precautions": "SSRI 항우울제, 면역억제제, 경구피임약 등 다수 약물과 심각한 상호작용. CYP3A4 유도.",
        "intake_method": "1일 3회, 1회 1정.",
    },
    {
        "product_name": "마늘추출물",
        "main_ingredient": "마늘추출물(알리인)",
        "category": "혈행개선",
        "ingredients": [{"name": "마늘추출물(알리인)", "amount": "600", "unit": "mg"}],
        "functionality": "혈중 콜레스테롤 개선에 도움. 혈행 개선에 도움.",
        "precautions": "항응고제 복용자 출혈 위험 증가. 수술 전 중단 권장.",
        "intake_method": "1일 1~2회, 1회 1캡슐.",
    },
    {
        "product_name": "녹차추출물 (EGCG)",
        "main_ingredient": "녹차추출물(카테킨)",
        "category": "항산화",
        "ingredients": [{"name": "녹차추출물(EGCG)", "amount": "300", "unit": "mg"}],
        "functionality": "체지방 감소에 도움. 항산화에 도움.",
        "precautions": "공복 복용 시 간 손상 보고. 철분 흡수 저해. 카페인 민감자 주의.",
        "intake_method": "1일 1~2회, 1회 1캡슐, 식후 복용.",
    },
    {
        "product_name": "당귀추출물",
        "main_ingredient": "당귀추출물(데커신)",
        "category": "여성건강",
        "ingredients": [{"name": "당귀추출물(데커신+데커시놀안젤레이트)", "amount": "500", "unit": "mg"}],
        "functionality": "여성 건강에 도움. 혈행 개선에 도움.",
        "precautions": "항응고제 복용자 출혈 위험. 임산부 복용 주의.",
        "intake_method": "1일 2~3회, 1회 1캡슐.",
    },
    {
        "product_name": "쏘팔메토",
        "main_ingredient": "쏘팔메토열매추출물",
        "category": "남성건강",
        "ingredients": [{"name": "쏘팔메토열매추출물", "amount": "320", "unit": "mg"}],
        "functionality": "전립선 건강에 도움. 배뇨 기능 개선에 도움.",
        "precautions": "호르몬 관련 약물 복용자 주의. 위장장애 가능.",
        "intake_method": "1일 1회, 1회 1캡슐, 식후.",
    },
    # ── 피부/미용 ──
    {
        "product_name": "콜라겐 (피쉬콜라겐)",
        "main_ingredient": "저분자 피쉬콜라겐 펩타이드",
        "category": "피부건강",
        "ingredients": [{"name": "저분자 피쉬콜라겐 펩타이드", "amount": "1000", "unit": "mg"}],
        "functionality": "피부 보습 및 탄력에 도움.",
        "precautions": "어류 알레르기 주의. 약물 상호작용 보고 적음.",
        "intake_method": "1일 1회, 1회 1포.",
    },
    # ── 수면 ──
    {
        "product_name": "멜라토닌",
        "main_ingredient": "멜라토닌",
        "category": "수면",
        "ingredients": [{"name": "멜라토닌", "amount": "3", "unit": "mg"}],
        "functionality": "수면의 질 개선에 도움. 시차 적응에 도움.",
        "precautions": "진정제, 수면제, 항우울제 복용자 주의(과도한 진정). 혈압약 효과 간섭 가능.",
        "intake_method": "취침 30분~1시간 전 1정 복용.",
    },
    # ── 기타 ──
    {
        "product_name": "레시틴",
        "main_ingredient": "대두레시틴",
        "category": "뇌건강",
        "ingredients": [{"name": "대두레시틴(포스파티딜콜린)", "amount": "1200", "unit": "mg"}],
        "functionality": "간 건강에 도움. 혈중 콜레스테롤 개선에 도움.",
        "precautions": "대두 알레르기 주의.",
        "intake_method": "1일 1~2회, 1회 1캡슐, 식후.",
    },
    {
        "product_name": "스피루리나",
        "main_ingredient": "스피루리나",
        "category": "종합영양",
        "ingredients": [{"name": "스피루리나", "amount": "3000", "unit": "mg"}],
        "functionality": "다양한 영양소 보충. 피부 건강에 도움.",
        "precautions": "자가면역질환자 주의. 페닐케톤뇨증 환자 금기.",
        "intake_method": "1일 3회, 1회 4정.",
    },
    {
        "product_name": "포스파티딜세린",
        "main_ingredient": "포스파티딜세린",
        "category": "뇌건강",
        "ingredients": [{"name": "포스파티딜세린", "amount": "100", "unit": "mg"}],
        "functionality": "인지력 개선에 도움.",
        "precautions": "항응고제 복용자 주의(혈액 응고 시간 연장 가능).",
        "intake_method": "1일 1~3회, 1회 1캡슐.",
    },
    {
        "product_name": "단백질보충제 (유청단백)",
        "main_ingredient": "유청단백",
        "category": "근육건강",
        "ingredients": [{"name": "유청단백질 분리물", "amount": "25", "unit": "g"}],
        "functionality": "근력 유지 및 증가에 도움.",
        "precautions": "유당불내증 주의. 신장 질환자 고단백 섭취 주의.",
        "intake_method": "1일 1~2회, 1회 1스쿱(30g), 물 또는 우유에 타서 섭취.",
    },
    {
        "product_name": "알로에 베라",
        "main_ingredient": "알로에 전잎 추출물",
        "category": "장건강",
        "ingredients": [{"name": "알로에 전잎 추출물", "amount": "100", "unit": "mg"}],
        "functionality": "배변활동 원활에 도움. 피부 건강에 도움.",
        "precautions": "장기 복용 시 전해질 불균형 주의. 임산부 복용 금기.",
        "intake_method": "1일 1회, 1회 1캡슐.",
    },
    {
        "product_name": "L-아르기닌",
        "main_ingredient": "L-아르기닌",
        "category": "혈행개선",
        "ingredients": [{"name": "L-아르기닌", "amount": "1000", "unit": "mg"}],
        "functionality": "혈관 건강에 도움. 운동 수행 능력 향상에 도움.",
        "precautions": "혈압약 복용자 저혈압 주의. 질산염 제제(니트로글리세린) 병용 금기.",
        "intake_method": "1일 1~2회, 1회 1정.",
    },
    {
        "product_name": "HMB",
        "main_ingredient": "HMB칼슘",
        "category": "근육건강",
        "ingredients": [{"name": "HMB칼슘(β-히드록시-β-메틸부티레이트)", "amount": "1500", "unit": "mg"}],
        "functionality": "근력 운동 시 근육량 유지에 도움.",
        "precautions": "특별한 약물 상호작용 보고 적음.",
        "intake_method": "1일 3회, 1회 1정, 식후.",
    },
]


# ─────────────────────────────────────────────────────────
# 2. 약물-영양제 상호작용 룰
# ─────────────────────────────────────────────────────────

# drug_keyword: drugs 테이블에서 ILIKE 검색할 키워드
# supplement_name: SUPPLEMENTS 리스트의 product_name과 매칭
DRUG_SUPPLEMENT_INTERACTIONS: list[dict[str, Any]] = [
    # ── SSRI + 세인트존스워트 (danger) ──
    {
        "drug_keywords": ["플루옥세틴", "파록세틴", "세르트랄린", "에스시탈로프람"],
        "supplement_name": "세인트존스워트 (관엽연교)",
        "severity": "danger",
        "description": "세로토닌 증후군 위험. SSRI와 세인트존스워트 모두 세로토닌 재흡수를 억제하여 세로토닌이 과도하게 축적될 수 있습니다.",
        "mechanism": "세로토닌 재흡수 억제 효과 중첩 → 세로토닌 과잉 → 정신상태 변화, 진전, 자율신경 불안정",
        "recommendation": "절대 병용하지 마세요. 반드시 의사/약사와 상담하세요.",
    },
    # ── 면역억제제 + 세인트존스워트 (danger) ──
    {
        "drug_keywords": ["사이클로스포린", "타크로리무스"],
        "supplement_name": "세인트존스워트 (관엽연교)",
        "severity": "danger",
        "description": "면역억제제 혈중 농도가 급격히 감소하여 장기이식 거부반응 위험이 있습니다.",
        "mechanism": "CYP3A4 효소 유도 → 면역억제제 대사 가속화 → 혈중 농도 급감",
        "recommendation": "절대 병용하지 마세요. 장기이식 환자는 특히 주의.",
    },
    # ── 면역억제제 + 에키네시아 (danger) ──
    {
        "drug_keywords": ["사이클로스포린", "타크로리무스"],
        "supplement_name": "에키네시아",
        "severity": "danger",
        "description": "에키네시아의 면역 자극 작용이 면역억제제의 효과를 상쇄할 수 있습니다.",
        "mechanism": "면역 세포 활성화 촉진 → 면역억제 효과 감소",
        "recommendation": "면역억제제 복용자는 에키네시아를 피하세요.",
    },
    # ── 아스피린 + 은행잎추출물 (danger) ──
    {
        "drug_keywords": ["아스피린"],
        "supplement_name": "은행잎 추출물 (징코)",
        "severity": "danger",
        "description": "출혈 위험이 크게 증가합니다. 은행잎 추출물은 혈소판 활성화 인자(PAF)를 억제하여 아스피린의 항혈소판 효과를 증폭시킵니다.",
        "mechanism": "항혈소판 작용 중첩 → 출혈 시간 연장",
        "recommendation": "병용을 피하세요. 수술 2주 전 은행잎 추출물 중단.",
    },
    # ── 아스피린 + 비타민E 고용량 (warning) ──
    {
        "drug_keywords": ["아스피린"],
        "supplement_name": "비타민E (토코페롤)",
        "severity": "warning",
        "description": "고용량 비타민E(400IU 이상) 복용 시 출혈 위험이 증가할 수 있습니다.",
        "mechanism": "비타민E가 비타민K 의존성 응고인자 활성 억제 + 혈소판 응집 억제",
        "recommendation": "비타민E 400IU 이하로 용량 조절. 출혈 징후 모니터링.",
    },
    # ── 아스피린 + 오메가3 고용량 (caution) ──
    {
        "drug_keywords": ["아스피린"],
        "supplement_name": "오메가3 (EPA/DHA)",
        "severity": "caution",
        "description": "이론적으로 출혈 위험이 증가할 수 있습니다. 다만 4g/일 이하에서는 실제 출혈 증가가 유의하지 않다는 연구 결과도 있습니다.",
        "mechanism": "항혈소판 효과 가능성",
        "recommendation": "일반적 용량에서는 안전하나, 고용량 복용 시 의사와 상담.",
    },
    # ── 아스피린 + 홍삼 (caution) ──
    {
        "drug_keywords": ["아스피린"],
        "supplement_name": "홍삼 (Korean Red Ginseng)",
        "severity": "caution",
        "description": "홍삼의 항혈소판 작용으로 출혈 위험이 증가할 수 있습니다.",
        "mechanism": "혈소판 응집 억제 작용 + INR 변동 가능",
        "recommendation": "병용 시 출혈 징후 모니터링. 수술 전 2주 중단 권장.",
    },
    # ── 아스피린 + 마늘추출물 (caution) ──
    {
        "drug_keywords": ["아스피린"],
        "supplement_name": "마늘추출물",
        "severity": "caution",
        "description": "마늘의 항혈소판 활성으로 출혈 경향이 증가할 수 있습니다.",
        "mechanism": "항혈소판 작용 + CYP2C9 억제 가능",
        "recommendation": "병용 시 주의. 수술 전 중단 권장.",
    },
    # ── 퀴놀론 항생제 + 미네랄 (caution) ──
    {
        "drug_keywords": ["플록사신"],
        "supplement_name": "칼슘 (탄산칼슘)",
        "severity": "caution",
        "description": "퀴놀론 항생제의 흡수가 최대 85%까지 감소할 수 있습니다. 다가 양이온(칼슘)과 킬레이트 복합체를 형성합니다.",
        "mechanism": "Ca²⁺와 킬레이트 형성 → 불용성 복합체 → 흡수 저해",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 칼슘을 복용하세요.",
    },
    {
        "drug_keywords": ["플록사신"],
        "supplement_name": "마그네슘 (산화마그네슘)",
        "severity": "caution",
        "description": "퀴놀론 항생제의 흡수가 감소합니다. 마그네슘과 킬레이트 복합체를 형성합니다.",
        "mechanism": "Mg²⁺와 킬레이트 형성 → 흡수 저해",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 마그네슘을 복용하세요.",
    },
    {
        "drug_keywords": ["플록사신"],
        "supplement_name": "철분 (황산제일철)",
        "severity": "caution",
        "description": "퀴놀론 항생제의 흡수가 감소합니다. 철분과 킬레이트 복합체를 형성합니다.",
        "mechanism": "Fe²⁺/Fe³⁺와 킬레이트 형성 → 흡수 저해",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 철분을 복용하세요.",
    },
    {
        "drug_keywords": ["플록사신"],
        "supplement_name": "아연 (황산아연)",
        "severity": "caution",
        "description": "퀴놀론 항생제의 흡수가 감소합니다.",
        "mechanism": "Zn²⁺와 킬레이트 형성 → 흡수 저해",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 아연을 복용하세요.",
    },
    # ── 테트라사이클린 + 미네랄 (caution) ──
    {
        "drug_keywords": ["사이클린"],
        "supplement_name": "칼슘 (탄산칼슘)",
        "severity": "caution",
        "description": "테트라사이클린계 항생제의 흡수가 크게 감소합니다.",
        "mechanism": "Ca²⁺와 킬레이트 형성 → 불용성 복합체",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 칼슘을 복용하세요.",
    },
    {
        "drug_keywords": ["사이클린"],
        "supplement_name": "철분 (황산제일철)",
        "severity": "caution",
        "description": "테트라사이클린계 항생제의 흡수가 크게 감소합니다.",
        "mechanism": "Fe²⁺/Fe³⁺와 킬레이트 형성",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 철분을 복용하세요.",
    },
    {
        "drug_keywords": ["사이클린"],
        "supplement_name": "마그네슘 (산화마그네슘)",
        "severity": "caution",
        "description": "테트라사이클린계 항생제의 흡수가 감소합니다.",
        "mechanism": "Mg²⁺와 킬레이트 형성",
        "recommendation": "항생제 복용 2시간 전 또는 6시간 후에 마그네슘을 복용하세요.",
    },
    # ── 스타틴 + CoQ10 (info) ──
    {
        "drug_keywords": ["스타틴", "아토르바스타틴", "로수바스타틴", "심바스타틴"],
        "supplement_name": "코엔자임Q10 (CoQ10)",
        "severity": "info",
        "description": "스타틴 복용 시 체내 CoQ10 합성이 저하됩니다. CoQ10 보충이 스타틴 부작용(근육통) 완화에 도움이 될 수 있습니다.",
        "mechanism": "HMG-CoA 환원효소 억제 → 콜레스테롤과 함께 CoQ10 합성도 감소",
        "recommendation": "스타틴 복용자는 CoQ10 보충을 고려하세요 (100~200mg/일).",
    },
    # ── 메트포르민 + 비타민B12 (info) ──
    {
        "drug_keywords": ["메트포르민"],
        "supplement_name": "비타민B12 (코발라민)",
        "severity": "info",
        "description": "메트포르민 장기 복용(2년 이상) 시 비타민B12 결핍이 발생할 수 있습니다(환자의 7~30%). B12 보충이 권장됩니다.",
        "mechanism": "B12-내인자(intrinsic factor) 복합체의 장 흡수 방해",
        "recommendation": "메트포르민 복용자는 B12 수치를 2~3년마다 모니터링하고, 보충을 고려하세요.",
    },
]


# ─────────────────────────────────────────────────────────
# 3. 영양제-영양제 상호작용 룰
# ─────────────────────────────────────────────────────────

SUPP_SUPP_INTERACTIONS: list[dict[str, Any]] = [
    # ── 흡수 경쟁 (caution) ──
    {
        "supp_a": "칼슘 (탄산칼슘)",
        "supp_b": "철분 (황산제일철)",
        "severity": "caution",
        "description": "칼슘이 철분(헴철, 비헴철 모두)의 흡수를 억제합니다. DMT1 수송체 경쟁으로 흡수율이 감소합니다.",
        "mechanism": "Ca²⁺와 Fe²⁺/Fe³⁺가 장관 내 동일 수송체(DMT1)에서 경쟁",
        "recommendation": "2~4시간 간격을 두고 복용하세요. 칼슘은 식후, 철분은 공복에 복용 권장.",
    },
    {
        "supp_a": "아연 (황산아연)",
        "supp_b": "철분 (황산제일철)",
        "severity": "caution",
        "description": "고용량 철분이 아연의 흡수를 현저히 억제합니다. 특히 공복 복용 시 영향이 큽니다.",
        "mechanism": "Fe²⁺와 Zn²⁺의 장관 내 흡수 경쟁",
        "recommendation": "다른 식사 시간에 분리하여 복용하세요.",
    },
    {
        "supp_a": "아연 (황산아연)",
        "supp_b": "구리",
        "severity": "caution",
        "description": "고용량 아연(50mg 이상)을 10주 이상 복용하면 구리 결핍을 유발할 수 있습니다(빈혈, 신경 손상).",
        "mechanism": "아연이 장세포 내 메탈로티오네인을 유도 → 구리가 메탈로티오네인에 포획 → 구리 흡수 차단",
        "recommendation": "아연:구리 비율을 10:1 이하로 유지. 아연 고용량 복용 시 구리 보충 권장.",
    },
    {
        "supp_a": "칼슘 (탄산칼슘)",
        "supp_b": "마그네슘 (산화마그네슘)",
        "severity": "caution",
        "description": "고용량 칼슘이 마그네슘 흡수를 방해하고 요중 마그네슘 배설을 증가시킬 수 있습니다.",
        "mechanism": "Ca²⁺와 Mg²⁺의 장관 내 흡수 경쟁 + 신장 배설 경쟁",
        "recommendation": "Ca:Mg 비율을 2:1로 유지. 동시 복용도 가능하나, 분리 복용이 더 효과적.",
    },
    {
        "supp_a": "칼슘 (탄산칼슘)",
        "supp_b": "아연 (황산아연)",
        "severity": "caution",
        "description": "칼슘이 아연의 흡수를 저해할 수 있습니다.",
        "mechanism": "장관 내 흡수 경쟁",
        "recommendation": "분리하여 복용 권장.",
    },
    {
        "supp_a": "녹차추출물 (EGCG)",
        "supp_b": "철분 (황산제일철)",
        "severity": "caution",
        "description": "녹차의 EGCG가 비헴철과 결합하여 철분 흡수를 저해합니다.",
        "mechanism": "폴리페놀이 비헴철과 불용성 복합체 형성",
        "recommendation": "2시간 이상 간격을 두고 복용하세요.",
    },
    {
        "supp_a": "비타민E (토코페롤)",
        "supp_b": "비타민K2 (메나퀴논-7)",
        "severity": "caution",
        "description": "고용량 비타민E(400IU 이상)가 비타민K 의존성 응고인자의 활성을 억제할 수 있습니다.",
        "mechanism": "비타민E가 비타민K 의존성 카르복실화 효소 활성 억제",
        "recommendation": "비타민E를 400IU 이하로 용량 조절.",
    },
    {
        "supp_a": "엽산 (폴산)",
        "supp_b": "비타민B12 (코발라민)",
        "severity": "caution",
        "description": "고용량 엽산이 B12 결핍의 주요 증상(거대적아구성 빈혈)을 은폐할 수 있어 신경 손상이 진행될 위험이 있습니다.",
        "mechanism": "엽산이 B12 결핍에 의한 빈혈 증상만 개선 → B12 결핍에 의한 신경계 손상은 계속 진행",
        "recommendation": "엽산 고용량 복용 전 B12 수치 확인. 가능하면 함께 보충.",
    },
    # ── 시너지 (info — 함께 복용 추천) ──
    {
        "supp_a": "비타민D (콜레칼시페롤)",
        "supp_b": "칼슘 (탄산칼슘)",
        "severity": "info",
        "description": "비타민D가 장에서 칼슘 흡수를 촉진합니다. 함께 복용 시 뼈 건강에 시너지 효과가 있습니다.",
        "mechanism": "비타민D → 활성형 칼시트리올 → 장 칼슘 수송 단백질(CaBP) 합성 유도 → 칼슘 흡수 증가",
        "recommendation": "함께 복용을 권장합니다. 식후 복용 시 흡수율이 높아집니다.",
    },
    {
        "supp_a": "비타민D (콜레칼시페롤)",
        "supp_b": "마그네슘 (산화마그네슘)",
        "severity": "info",
        "description": "마그네슘은 비타민D의 생합성, 수송, 활성화에 필수적인 보조인자입니다.",
        "mechanism": "마그네슘이 비타민D 대사 효소(25-hydroxylase, 1α-hydroxylase)의 보조인자로 작용",
        "recommendation": "함께 복용을 권장합니다. 비타민D 효과를 극대화합니다.",
    },
    {
        "supp_a": "비타민D (콜레칼시페롤)",
        "supp_b": "비타민K2 (메나퀴논-7)",
        "severity": "info",
        "description": "비타민D가 혈중 칼슘을 증가시키고, 비타민K2가 칼슘을 뼈로 이동시켜 동맥 석회화를 방지합니다.",
        "mechanism": "비타민D → 칼슘 흡수 증가 / 비타민K2 → 오스테오칼신 활성화 → 칼슘을 뼈로 유도",
        "recommendation": "함께 복용을 권장합니다. 뼈 건강 + 심혈관 보호 시너지.",
    },
    {
        "supp_a": "비타민C (아스코르브산)",
        "supp_b": "철분 (황산제일철)",
        "severity": "info",
        "description": "비타민C가 비헴철(Fe³⁺)을 흡수 가능한 형태(Fe²⁺)로 환원하여 철분 흡수율을 크게 높입니다.",
        "mechanism": "아스코르브산의 환원 작용: Fe³⁺ → Fe²⁺ (흡수 가능 형태)",
        "recommendation": "함께 복용을 권장합니다. 철분 보충 시 비타민C 동시 섭취가 효과적.",
    },
    {
        "supp_a": "오메가3 (EPA/DHA)",
        "supp_b": "비타민D (콜레칼시페롤)",
        "severity": "info",
        "description": "오메가3의 지방이 지용성 비타민D의 흡수를 촉진합니다.",
        "mechanism": "지용성 비타민은 지방과 함께 섭취 시 미셀 형성 → 흡수율 증가",
        "recommendation": "함께 식후 복용하면 비타민D 흡수가 향상됩니다.",
    },
    {
        "supp_a": "오메가3 (EPA/DHA)",
        "supp_b": "루테인/지아잔틴",
        "severity": "info",
        "description": "지용성인 루테인의 흡수를 오메가3의 지방산이 도와줍니다.",
        "mechanism": "지용성 카로테노이드의 지방 미셀 형성 흡수 촉진",
        "recommendation": "함께 식후 복용을 권장합니다.",
    },
]


# ─────────────────────────────────────────────────────────
# 적재 로직
# ─────────────────────────────────────────────────────────

async def seed_supplements(session) -> dict[str, int]:
    """영양제 50종을 DB에 삽입한다."""
    stats = {"inserted": 0, "skipped": 0}

    for supp in SUPPLEMENTS:
        slug = "supp-" + supp["product_name"].split("(")[0].strip().replace(" ", "-")

        # 중복 체크
        exists = await session.execute(
            text("SELECT id FROM supplements WHERE product_name = :name"),
            {"name": supp["product_name"]},
        )
        if exists.first():
            stats["skipped"] += 1
            continue

        await session.execute(
            text("""
                INSERT INTO supplements (
                    product_name, slug, main_ingredient, category,
                    ingredients, functionality, precautions, intake_method,
                    source
                ) VALUES (
                    :product_name, :slug, :main_ingredient, :category,
                    CAST(:ingredients AS jsonb), :functionality, :precautions,
                    :intake_method, :source
                )
            """),
            {
                "product_name": supp["product_name"],
                "slug": slug,
                "main_ingredient": supp.get("main_ingredient"),
                "category": supp.get("category"),
                "ingredients": json.dumps(supp.get("ingredients", []), ensure_ascii=False),
                "functionality": supp.get("functionality"),
                "precautions": supp.get("precautions"),
                "intake_method": supp.get("intake_method"),
                "source": "seed_evidence_based",
            },
        )
        stats["inserted"] += 1

    return stats


async def seed_drug_supplement_interactions(session) -> dict[str, int]:
    """약물-영양제 상호작용을 DB에 삽입한다."""
    stats = {"inserted": 0, "skipped": 0, "no_match": 0}

    # 영양제 name → id 매핑
    result = await session.execute(text("SELECT id, product_name FROM supplements"))
    supp_map = {row[1]: row[0] for row in result.fetchall()}

    for rule in DRUG_SUPPLEMENT_INTERACTIONS:
        supp_name = rule["supplement_name"]
        supp_id = supp_map.get(supp_name)
        if not supp_id:
            logger.warning("영양제 없음: %s", supp_name)
            stats["no_match"] += 1
            continue

        for kw in rule["drug_keywords"]:
            # 해당 키워드의 대표 약물 1개만 사용 (모든 약물에 대해 만들면 너무 많음)
            # → 대표 약물 최대 5개로 제한
            drug_rows = await session.execute(
                text("SELECT id, item_name FROM drugs WHERE item_name ILIKE :kw LIMIT 5"),
                {"kw": f"%{kw}%"},
            )
            drugs = drug_rows.fetchall()

            if not drugs:
                continue

            for drug_id, drug_name in drugs:
                source_id = f"SEED_DS_{drug_id}_{supp_id}"

                # 중복 체크
                exists = await session.execute(
                    text("SELECT id FROM interactions WHERE source_id = :sid"),
                    {"sid": source_id},
                )
                if exists.first():
                    stats["skipped"] += 1
                    continue

                # item_a = 작은 id, item_b = 큰 id (정렬 통일)
                if drug_id < supp_id:
                    a_type, a_id, a_name = "drug", drug_id, drug_name
                    b_type, b_id, b_name = "supplement", supp_id, supp_name
                else:
                    a_type, a_id, a_name = "supplement", supp_id, supp_name
                    b_type, b_id, b_name = "drug", drug_id, drug_name

                await session.execute(
                    text("""
                        INSERT INTO interactions (
                            item_a_type, item_a_id, item_a_name,
                            item_b_type, item_b_id, item_b_name,
                            severity, description, mechanism, recommendation,
                            source, source_id, evidence_level
                        ) VALUES (
                            :a_type, :a_id, :a_name,
                            :b_type, :b_id, :b_name,
                            :severity, :description, :mechanism, :recommendation,
                            :source, :source_id, :evidence_level
                        )
                    """),
                    {
                        "a_type": a_type, "a_id": a_id, "a_name": a_name,
                        "b_type": b_type, "b_id": b_id, "b_name": b_name,
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "mechanism": rule["mechanism"],
                        "recommendation": rule["recommendation"],
                        "source": "evidence_based",
                        "source_id": source_id,
                        "evidence_level": "clinical",
                    },
                )
                stats["inserted"] += 1

    return stats


async def seed_supp_supp_interactions(session) -> dict[str, int]:
    """영양제-영양제 상호작용을 DB에 삽입한다."""
    stats = {"inserted": 0, "skipped": 0, "no_match": 0}

    result = await session.execute(text("SELECT id, product_name FROM supplements"))
    supp_map = {row[1]: row[0] for row in result.fetchall()}

    for rule in SUPP_SUPP_INTERACTIONS:
        id_a = supp_map.get(rule["supp_a"])
        id_b = supp_map.get(rule["supp_b"])

        if not id_a or not id_b:
            logger.warning("영양제 없음: %s / %s", rule["supp_a"], rule["supp_b"])
            stats["no_match"] += 1
            continue

        # 정렬
        if id_a > id_b:
            id_a, id_b = id_b, id_a
            rule["supp_a"], rule["supp_b"] = rule["supp_b"], rule["supp_a"]

        source_id = f"SEED_SS_{id_a}_{id_b}"

        exists = await session.execute(
            text("SELECT id FROM interactions WHERE source_id = :sid"),
            {"sid": source_id},
        )
        if exists.first():
            stats["skipped"] += 1
            continue

        await session.execute(
            text("""
                INSERT INTO interactions (
                    item_a_type, item_a_id, item_a_name,
                    item_b_type, item_b_id, item_b_name,
                    severity, description, mechanism, recommendation,
                    source, source_id, evidence_level
                ) VALUES (
                    'supplement', :a_id, :a_name,
                    'supplement', :b_id, :b_name,
                    :severity, :description, :mechanism, :recommendation,
                    'evidence_based', :source_id, 'clinical'
                )
            """),
            {
                "a_id": id_a, "a_name": rule["supp_a"],
                "b_id": id_b, "b_name": rule["supp_b"],
                "severity": rule["severity"],
                "description": rule["description"],
                "mechanism": rule["mechanism"],
                "recommendation": rule["recommendation"],
                "source_id": source_id,
            },
        )
        stats["inserted"] += 1

    return stats


async def main() -> None:
    start = time.time()
    logger.info("영양제 시드 데이터 적재 시작")

    async with async_session_factory() as session:
        # 1. 영양제
        logger.info("=" * 50)
        logger.info("[1/3] 영양제 50종 적재")
        s1 = await seed_supplements(session)
        logger.info("  삽입: %d, 건너뜀: %d", s1["inserted"], s1["skipped"])

        # 2. 약물-영양제 상호작용
        logger.info("[2/3] 약물-영양제 상호작용 적재")
        s2 = await seed_drug_supplement_interactions(session)
        logger.info(
            "  삽입: %d, 건너뜀: %d, 매칭실패: %d",
            s2["inserted"], s2["skipped"], s2["no_match"],
        )

        # 3. 영양제-영양제 상호작용
        logger.info("[3/3] 영양제-영양제 상호작용 적재")
        s3 = await seed_supp_supp_interactions(session)
        logger.info(
            "  삽입: %d, 건너뜀: %d, 매칭실패: %d",
            s3["inserted"], s3["skipped"], s3["no_match"],
        )

        await session.commit()

    elapsed = time.time() - start
    logger.info("=" * 50)
    logger.info("적재 완료 (%.1f초)", elapsed)
    logger.info(
        "영양제: %d | 약-영양제 상호작용: %d | 영양제-영양제 상호작용: %d",
        s1["inserted"], s2["inserted"], s3["inserted"],
    )


if __name__ == "__main__":
    asyncio.run(main())
