"""해외 인기 약물/영양제 데이터 수집 스크립트.

OpenFDA API + 큐레이션 데이터로 한국인이 많이 사용하는
해외 직구 약물·영양제를 DB에 추가한다.

사용법:
    python scripts/collect_international.py
"""

import asyncio
import hashlib
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
if not DATABASE_URL_SYNC:
    sys.exit("ERROR: DATABASE_URL_SYNC 필요")

import psycopg2

# ─── 한영 성분명 매핑 ───────────────────────────────────────────
INGREDIENT_MAP_EN_TO_KR = {
    # 진통/해열/소염
    "acetaminophen": "아세트아미노펜",
    "ibuprofen": "이부프로펜",
    "naproxen": "나프록센",
    "naproxen sodium": "나프록센나트륨",
    "aspirin": "아스피린",
    "diclofenac": "디클로페낙",
    "celecoxib": "셀레콕시브",
    # 항히스타민/알레르기
    "cetirizine": "세티리진",
    "cetirizine hydrochloride": "세티리진염산염",
    "loratadine": "로라타딘",
    "fexofenadine": "펙소페나딘",
    "diphenhydramine": "디펜히드라민",
    "diphenhydramine hydrochloride": "디펜히드라민염산염",
    "chlorpheniramine": "클로르페니라민",
    # 소화기
    "omeprazole": "오메프라졸",
    "omeprazole magnesium": "오메프라졸마그네슘",
    "famotidine": "파모티딘",
    "ranitidine": "라니티딘",
    "bismuth subsalicylate": "비스무트차살리실산염",
    "calcium carbonate": "탄산칼슘",
    "loperamide": "로페라미드",
    "simethicone": "시메티콘",
    # 비타민
    "vitamin a": "비타민A",
    "vitamin b1": "비타민B1(티아민)",
    "vitamin b2": "비타민B2(리보플라빈)",
    "vitamin b6": "비타민B6(피리독신)",
    "vitamin b12": "비타민B12(시아노코발라민)",
    "vitamin c": "비타민C(아스코르브산)",
    "ascorbic acid": "아스코르브산(비타민C)",
    "vitamin d": "비타민D",
    "vitamin d3": "비타민D3(콜레칼시페롤)",
    "cholecalciferol": "콜레칼시페롤(비타민D3)",
    "vitamin e": "비타민E(토코페롤)",
    "vitamin k": "비타민K",
    "folic acid": "엽산",
    "niacin": "니아신(비타민B3)",
    "biotin": "비오틴",
    "pantothenic acid": "판토텐산(비타민B5)",
    # 미네랄
    "calcium": "칼슘",
    "magnesium": "마그네슘",
    "magnesium oxide": "산화마그네슘",
    "magnesium citrate": "구연산마그네슘",
    "zinc": "아연",
    "zinc gluconate": "글루콘산아연",
    "iron": "철분",
    "ferrous sulfate": "황산제일철",
    "selenium": "셀레늄",
    "chromium": "크롬",
    "potassium": "칼륨",
    "copper": "구리",
    "manganese": "망간",
    "iodine": "요오드",
    # 오메가/지방산
    "omega-3": "오메가-3",
    "fish oil": "피쉬오일",
    "epa": "EPA",
    "dha": "DHA",
    "flaxseed oil": "아마씨오일",
    # 프로바이오틱스
    "lactobacillus": "락토바실러스",
    "bifidobacterium": "비피더스균",
    "probiotics": "프로바이오틱스",
    # 아미노산/단백질
    "l-arginine": "L-아르기닌",
    "l-carnitine": "L-카르니틴",
    "l-lysine": "L-라이신",
    "collagen": "콜라겐",
    "whey protein": "유청단백질",
    # 허브/추출물
    "turmeric": "강황(커큐민)",
    "curcumin": "커큐민",
    "ginkgo biloba": "은행잎추출물",
    "milk thistle": "밀크씨슬(실리마린)",
    "silymarin": "실리마린",
    "saw palmetto": "쏘팔메토",
    "echinacea": "에키네시아",
    "valerian": "발레리안",
    "st. john's wort": "세인트존스워트",
    "garlic": "마늘추출물",
    "ginger": "생강추출물",
    "cranberry": "크랜베리",
    "green tea extract": "녹차추출물",
    # 기타 인기 성분
    "melatonin": "멜라토닌",
    "coenzyme q10": "코엔자임Q10",
    "coq10": "코엔자임Q10",
    "ubiquinol": "유비퀴놀",
    "glucosamine": "글루코사민",
    "chondroitin": "콘드로이틴",
    "msm": "MSM(메틸설포닐메탄)",
    "hyaluronic acid": "히알루론산",
    "lutein": "루테인",
    "zeaxanthin": "지아잔틴",
    "alpha lipoic acid": "알파리포산",
    "resveratrol": "레스베라트롤",
    "quercetin": "케르세틴",
    "psyllium": "차전자피",
    "spirulina": "스피룰리나",
    "chlorella": "클로렐라",
    # 기침/감기
    "dextromethorphan": "덱스트로메토르판",
    "guaifenesin": "구아이페네신",
    "pseudoephedrine": "슈도에페드린",
    "phenylephrine": "페닐에프린",
    # 기타 OTC
    "minoxidil": "미녹시딜",
    "hydrocortisone": "히드로코르티손",
    "benzoyl peroxide": "벤조일퍼옥사이드",
    "salicylic acid": "살리실산",
    "miconazole": "미코나졸",
    "clotrimazole": "클로트리마졸",
}


def translate_ingredient(en_name: str) -> str:
    """영문 성분명을 한글로 번역한다."""
    lower = en_name.lower().strip()
    if lower in INGREDIENT_MAP_EN_TO_KR:
        return INGREDIENT_MAP_EN_TO_KR[lower]
    # 부분 매칭 시도
    for en, kr in INGREDIENT_MAP_EN_TO_KR.items():
        if en in lower or lower in en:
            return kr
    return en_name  # 매핑 없으면 영문 그대로


def make_slug(prefix: str, name: str) -> str:
    """URL-safe slug 생성."""
    h = hashlib.md5(name.encode()).hexdigest()[:12]
    return f"{prefix}-{h}"


# ─── 큐레이션: 한국인이 많이 직구하는 해외 영양제 ─────────────
CURATED_SUPPLEMENTS = [
    # 비타민D
    {"product_name": "Nature Made Vitamin D3 2000 IU", "product_name_kr": "네이처메이드 비타민D3 2000IU",
     "company": "Nature Made", "category": "비타민",
     "main_ingredient": "비타민D3(콜레칼시페롤)", "ingredients": [{"name": "Cholecalciferol (Vitamin D3)", "name_kr": "비타민D3(콜레칼시페롤)", "amount": "50", "unit": "mcg"}],
     "functionality": "뼈와 치아 건강 유지에 필요. 칼슘과 인의 흡수를 도움. 면역 기능 지원."},
    {"product_name": "Kirkland Signature Vitamin D3 2000 IU", "product_name_kr": "커클랜드 비타민D3 2000IU",
     "company": "Kirkland Signature", "category": "비타민",
     "main_ingredient": "비타민D3(콜레칼시페롤)", "ingredients": [{"name": "Cholecalciferol (Vitamin D3)", "name_kr": "비타민D3(콜레칼시페롤)", "amount": "50", "unit": "mcg"}],
     "functionality": "뼈와 치아 건강 유지에 필요. 칼슘과 인의 흡수를 도움."},
    {"product_name": "NOW Foods Vitamin D3 5000 IU", "product_name_kr": "나우푸드 비타민D3 5000IU",
     "company": "NOW Foods", "category": "비타민",
     "main_ingredient": "비타민D3(콜레칼시페롤)", "ingredients": [{"name": "Cholecalciferol (Vitamin D3)", "name_kr": "비타민D3(콜레칼시페롤)", "amount": "125", "unit": "mcg"}],
     "functionality": "뼈와 치아 건강 유지에 필요. 면역 기능 지원. 고함량 비타민D."},
    # 오메가-3
    {"product_name": "Nature Made Fish Oil 1200mg Omega-3", "product_name_kr": "네이처메이드 피쉬오일 1200mg 오메가3",
     "company": "Nature Made", "category": "오메가-3",
     "main_ingredient": "오메가-3(EPA+DHA)", "ingredients": [{"name": "EPA", "name_kr": "EPA", "amount": "360", "unit": "mg"}, {"name": "DHA", "name_kr": "DHA", "amount": "240", "unit": "mg"}],
     "functionality": "혈중 중성지방 감소에 도움. 혈행 개선. 기억력 개선에 도움."},
    {"product_name": "Kirkland Signature Fish Oil 1000mg", "product_name_kr": "커클랜드 피쉬오일 1000mg",
     "company": "Kirkland Signature", "category": "오메가-3",
     "main_ingredient": "오메가-3(EPA+DHA)", "ingredients": [{"name": "EPA", "name_kr": "EPA", "amount": "300", "unit": "mg"}, {"name": "DHA", "name_kr": "DHA", "amount": "200", "unit": "mg"}],
     "functionality": "혈중 중성지방 감소에 도움. 혈행 개선."},
    {"product_name": "NOW Foods Ultra Omega-3", "product_name_kr": "나우푸드 울트라 오메가-3",
     "company": "NOW Foods", "category": "오메가-3",
     "main_ingredient": "오메가-3(EPA+DHA)", "ingredients": [{"name": "EPA", "name_kr": "EPA", "amount": "500", "unit": "mg"}, {"name": "DHA", "name_kr": "DHA", "amount": "250", "unit": "mg"}],
     "functionality": "혈중 중성지방 감소에 도움. 혈행 개선. 고순도 오메가3."},
    {"product_name": "Nordic Naturals Ultimate Omega", "product_name_kr": "노르딕내추럴스 얼티밋 오메가",
     "company": "Nordic Naturals", "category": "오메가-3",
     "main_ingredient": "오메가-3(EPA+DHA)", "ingredients": [{"name": "EPA", "name_kr": "EPA", "amount": "650", "unit": "mg"}, {"name": "DHA", "name_kr": "DHA", "amount": "450", "unit": "mg"}],
     "functionality": "혈중 중성지방 감소에 도움. 고순도 고함량 오메가3."},
    # 종합비타민
    {"product_name": "Centrum Adults Multivitamin", "product_name_kr": "센트룸 어덜트 종합비타민",
     "company": "Centrum (GSK)", "category": "비타민",
     "main_ingredient": "종합비타민/미네랄", "ingredients": [
        {"name": "Vitamin A", "name_kr": "비타민A", "amount": "900", "unit": "mcg"},
        {"name": "Vitamin C", "name_kr": "비타민C", "amount": "90", "unit": "mg"},
        {"name": "Vitamin D3", "name_kr": "비타민D3", "amount": "25", "unit": "mcg"},
        {"name": "Vitamin E", "name_kr": "비타민E", "amount": "15", "unit": "mg"},
        {"name": "Vitamin B12", "name_kr": "비타민B12", "amount": "6", "unit": "mcg"},
        {"name": "Iron", "name_kr": "철분", "amount": "8", "unit": "mg"},
        {"name": "Zinc", "name_kr": "아연", "amount": "11", "unit": "mg"},
     ],
     "functionality": "종합비타민 및 미네랄 보충. 에너지 대사, 면역 기능, 뼈 건강 지원."},
    {"product_name": "Kirkland Signature Daily Multi Vitamins & Minerals", "product_name_kr": "커클랜드 데일리 종합비타민 미네랄",
     "company": "Kirkland Signature", "category": "비타민",
     "main_ingredient": "종합비타민/미네랄", "ingredients": [
        {"name": "Vitamin A", "name_kr": "비타민A", "amount": "900", "unit": "mcg"},
        {"name": "Vitamin C", "name_kr": "비타민C", "amount": "120", "unit": "mg"},
        {"name": "Vitamin D3", "name_kr": "비타민D3", "amount": "25", "unit": "mcg"},
        {"name": "Iron", "name_kr": "철분", "amount": "18", "unit": "mg"},
     ],
     "functionality": "일일 필요 비타민 및 미네랄 보충."},
    {"product_name": "Nature Made Multi Complete", "product_name_kr": "네이처메이드 멀티 컴플리트",
     "company": "Nature Made", "category": "비타민",
     "main_ingredient": "종합비타민/미네랄", "ingredients": [
        {"name": "Vitamin C", "name_kr": "비타민C", "amount": "60", "unit": "mg"},
        {"name": "Vitamin D3", "name_kr": "비타민D3", "amount": "25", "unit": "mcg"},
        {"name": "Vitamin B12", "name_kr": "비타민B12", "amount": "6", "unit": "mcg"},
     ],
     "functionality": "일일 필요 비타민 보충. 에너지 대사 지원."},
    # 프로바이오틱스
    {"product_name": "Culturelle Digestive Health Probiotic", "product_name_kr": "컬처렐 소화건강 프로바이오틱스",
     "company": "Culturelle", "category": "프로바이오틱스",
     "main_ingredient": "Lactobacillus rhamnosus GG", "ingredients": [{"name": "Lactobacillus rhamnosus GG", "name_kr": "락토바실러스 람노서스 GG", "amount": "10B", "unit": "CFU"}],
     "functionality": "장내 유익균 증식 및 유해균 억제. 배변 활동 원활. 소화 건강."},
    {"product_name": "Garden of Life Dr. Formulated Probiotics", "product_name_kr": "가든오브라이프 닥터포뮬레이트 프로바이오틱스",
     "company": "Garden of Life", "category": "프로바이오틱스",
     "main_ingredient": "프로바이오틱스 16종", "ingredients": [{"name": "Probiotic Blend (16 Strains)", "name_kr": "프로바이오틱스 복합 16종", "amount": "50B", "unit": "CFU"}],
     "functionality": "장내 유익균 증식. 면역 기능 지원. 소화 건강."},
    {"product_name": "NOW Foods Probiotic-10 25 Billion", "product_name_kr": "나우푸드 프로바이오틱-10 250억",
     "company": "NOW Foods", "category": "프로바이오틱스",
     "main_ingredient": "프로바이오틱스 10종", "ingredients": [{"name": "Probiotic Blend (10 Strains)", "name_kr": "프로바이오틱스 복합 10종", "amount": "25B", "unit": "CFU"}],
     "functionality": "장내 유익균 증식. 배변 활동 원활."},
    # 마그네슘
    {"product_name": "Nature Made Magnesium 250mg", "product_name_kr": "네이처메이드 마그네슘 250mg",
     "company": "Nature Made", "category": "미네랄",
     "main_ingredient": "마그네슘", "ingredients": [{"name": "Magnesium Oxide", "name_kr": "산화마그네슘", "amount": "250", "unit": "mg"}],
     "functionality": "신경과 근육 기능 유지에 필요. 에너지 이용에 필요."},
    {"product_name": "NOW Foods Magnesium Citrate 200mg", "product_name_kr": "나우푸드 구연산마그네슘 200mg",
     "company": "NOW Foods", "category": "미네랄",
     "main_ingredient": "구연산마그네슘", "ingredients": [{"name": "Magnesium Citrate", "name_kr": "구연산마그네슘", "amount": "200", "unit": "mg"}],
     "functionality": "신경과 근육 기능 유지에 필요. 에너지 이용에 필요. 높은 흡수율."},
    {"product_name": "Doctor's Best High Absorption Magnesium", "product_name_kr": "닥터스베스트 고흡수 마그네슘",
     "company": "Doctor's Best", "category": "미네랄",
     "main_ingredient": "킬레이트 마그네슘", "ingredients": [{"name": "Magnesium (as Magnesium Lysinate Glycinate Chelate)", "name_kr": "마그네슘 리시네이트 글리시네이트 킬레이트", "amount": "200", "unit": "mg"}],
     "functionality": "신경과 근육 기능 유지. 높은 흡수율의 킬레이트 마그네슘."},
    # 칼슘
    {"product_name": "Kirkland Signature Calcium 600mg + D3", "product_name_kr": "커클랜드 칼슘 600mg + 비타민D3",
     "company": "Kirkland Signature", "category": "미네랄",
     "main_ingredient": "칼슘+비타민D3", "ingredients": [{"name": "Calcium Carbonate", "name_kr": "탄산칼슘", "amount": "600", "unit": "mg"}, {"name": "Vitamin D3", "name_kr": "비타민D3", "amount": "500", "unit": "IU"}],
     "functionality": "뼈와 치아 건강 유지에 필요. 골다공증 예방."},
    {"product_name": "Nature Made Calcium 750mg + D + K", "product_name_kr": "네이처메이드 칼슘 750mg + D + K",
     "company": "Nature Made", "category": "미네랄",
     "main_ingredient": "칼슘+비타민D+비타민K", "ingredients": [
        {"name": "Calcium", "name_kr": "칼슘", "amount": "750", "unit": "mg"},
        {"name": "Vitamin D3", "name_kr": "비타민D3", "amount": "500", "unit": "IU"},
        {"name": "Vitamin K", "name_kr": "비타민K", "amount": "40", "unit": "mcg"},
     ],
     "functionality": "뼈와 치아 건강 유지에 필요. 칼슘 흡수 증진."},
    # 아연
    {"product_name": "Nature Made Zinc 30mg", "product_name_kr": "네이처메이드 아연 30mg",
     "company": "Nature Made", "category": "미네랄",
     "main_ingredient": "아연", "ingredients": [{"name": "Zinc Gluconate", "name_kr": "글루콘산아연", "amount": "30", "unit": "mg"}],
     "functionality": "면역 기능에 필요. 정상적인 세포 분열에 필요."},
    # 비타민C
    {"product_name": "Nature Made Vitamin C 1000mg", "product_name_kr": "네이처메이드 비타민C 1000mg",
     "company": "Nature Made", "category": "비타민",
     "main_ingredient": "비타민C(아스코르브산)", "ingredients": [{"name": "Ascorbic Acid (Vitamin C)", "name_kr": "아스코르브산(비타민C)", "amount": "1000", "unit": "mg"}],
     "functionality": "결합조직 형성과 기능유지에 필요. 항산화 작용. 면역 기능 지원."},
    {"product_name": "NOW Foods Vitamin C-1000", "product_name_kr": "나우푸드 비타민C 1000",
     "company": "NOW Foods", "category": "비타민",
     "main_ingredient": "비타민C(아스코르브산)", "ingredients": [{"name": "Ascorbic Acid", "name_kr": "아스코르브산(비타민C)", "amount": "1000", "unit": "mg"}, {"name": "Rose Hips", "name_kr": "로즈힙", "amount": "25", "unit": "mg"}],
     "functionality": "결합조직 형성과 기능유지에 필요. 항산화 작용. 로즈힙 함유."},
    # 비타민B 복합
    {"product_name": "Nature Made Super B-Complex", "product_name_kr": "네이처메이드 슈퍼 비타민B 콤플렉스",
     "company": "Nature Made", "category": "비타민",
     "main_ingredient": "비타민B군 복합", "ingredients": [
        {"name": "Vitamin B1", "name_kr": "비타민B1(티아민)", "amount": "100", "unit": "mg"},
        {"name": "Vitamin B2", "name_kr": "비타민B2(리보플라빈)", "amount": "20", "unit": "mg"},
        {"name": "Vitamin B6", "name_kr": "비타민B6(피리독신)", "amount": "10", "unit": "mg"},
        {"name": "Vitamin B12", "name_kr": "비타민B12", "amount": "15", "unit": "mcg"},
        {"name": "Folic Acid", "name_kr": "엽산", "amount": "400", "unit": "mcg"},
        {"name": "Biotin", "name_kr": "비오틴", "amount": "30", "unit": "mcg"},
     ],
     "functionality": "에너지 대사에 필요. 신경 기능 유지."},
    # 코엔자임 Q10
    {"product_name": "NOW Foods CoQ10 100mg", "product_name_kr": "나우푸드 코큐텐 100mg",
     "company": "NOW Foods", "category": "코엔자임Q10",
     "main_ingredient": "코엔자임Q10", "ingredients": [{"name": "Coenzyme Q10 (Ubiquinone)", "name_kr": "코엔자임Q10(유비퀴논)", "amount": "100", "unit": "mg"}],
     "functionality": "항산화 작용. 세포 에너지 생성에 관여. 심혈관 건강 지원."},
    {"product_name": "Kirkland Signature CoQ10 300mg", "product_name_kr": "커클랜드 코큐텐 300mg",
     "company": "Kirkland Signature", "category": "코엔자임Q10",
     "main_ingredient": "코엔자임Q10", "ingredients": [{"name": "Coenzyme Q10", "name_kr": "코엔자임Q10", "amount": "300", "unit": "mg"}],
     "functionality": "항산화 작용. 세포 에너지 생성에 관여. 고함량."},
    # 글루코사민
    {"product_name": "Kirkland Signature Glucosamine HCI 1500mg with MSM", "product_name_kr": "커클랜드 글루코사민 1500mg + MSM",
     "company": "Kirkland Signature", "category": "글루코사민",
     "main_ingredient": "글루코사민+MSM", "ingredients": [
        {"name": "Glucosamine HCl", "name_kr": "글루코사민염산염", "amount": "1500", "unit": "mg"},
        {"name": "MSM", "name_kr": "MSM(메틸설포닐메탄)", "amount": "1500", "unit": "mg"},
     ],
     "functionality": "관절 건강에 도움. 연골 구성 성분 보충."},
    {"product_name": "NOW Foods Glucosamine & Chondroitin with MSM", "product_name_kr": "나우푸드 글루코사민 콘드로이틴 MSM",
     "company": "NOW Foods", "category": "글루코사민",
     "main_ingredient": "글루코사민+콘드로이틴+MSM", "ingredients": [
        {"name": "Glucosamine HCl", "name_kr": "글루코사민염산염", "amount": "1100", "unit": "mg"},
        {"name": "Chondroitin Sulfate", "name_kr": "콘드로이틴황산염", "amount": "1200", "unit": "mg"},
        {"name": "MSM", "name_kr": "MSM", "amount": "300", "unit": "mg"},
     ],
     "functionality": "관절 건강에 도움. 연골 보호."},
    # 루테인
    {"product_name": "NOW Foods Lutein 20mg", "product_name_kr": "나우푸드 루테인 20mg",
     "company": "NOW Foods", "category": "루테인",
     "main_ingredient": "루테인", "ingredients": [{"name": "Lutein (from Marigold Extract)", "name_kr": "루테인(마리골드추출물)", "amount": "20", "unit": "mg"}, {"name": "Zeaxanthin", "name_kr": "지아잔틴", "amount": "1", "unit": "mg"}],
     "functionality": "눈 건강에 도움을 줄 수 있음. 황반색소 밀도 유지."},
    # 밀크씨슬
    {"product_name": "NOW Foods Silymarin Milk Thistle Extract 150mg", "product_name_kr": "나우푸드 실리마린 밀크씨슬 150mg",
     "company": "NOW Foods", "category": "밀크씨슬",
     "main_ingredient": "실리마린(밀크씨슬)", "ingredients": [{"name": "Milk Thistle Extract (Silymarin)", "name_kr": "밀크씨슬추출물(실리마린)", "amount": "150", "unit": "mg"}],
     "functionality": "간 건강에 도움을 줄 수 있음. 항산화 작용."},
    {"product_name": "Jarrow Formulas Milk Thistle 150mg", "product_name_kr": "재로우 밀크씨슬 150mg",
     "company": "Jarrow Formulas", "category": "밀크씨슬",
     "main_ingredient": "실리마린(밀크씨슬)", "ingredients": [{"name": "Milk Thistle Seed Extract (80% Silymarin)", "name_kr": "밀크씨슬종자추출물(실리마린 80%)", "amount": "150", "unit": "mg"}],
     "functionality": "간 건강에 도움을 줄 수 있음. 간세포 보호."},
    # 멜라토닌
    {"product_name": "Nature Made Melatonin 3mg", "product_name_kr": "네이처메이드 멜라토닌 3mg",
     "company": "Nature Made", "category": "기타",
     "main_ingredient": "멜라토닌", "ingredients": [{"name": "Melatonin", "name_kr": "멜라토닌", "amount": "3", "unit": "mg"}],
     "functionality": "수면 보조. 시차 적응에 도움. (국내에서는 전문의약품 성분)"},
    {"product_name": "NOW Foods Melatonin 5mg", "product_name_kr": "나우푸드 멜라토닌 5mg",
     "company": "NOW Foods", "category": "기타",
     "main_ingredient": "멜라토닌", "ingredients": [{"name": "Melatonin", "name_kr": "멜라토닌", "amount": "5", "unit": "mg"}],
     "functionality": "수면 보조. 시차 적응에 도움. (국내에서는 전문의약품 성분)"},
    # 콜라겐
    {"product_name": "Vital Proteins Collagen Peptides", "product_name_kr": "바이탈프로틴스 콜라겐 펩타이드",
     "company": "Vital Proteins", "category": "콜라겐",
     "main_ingredient": "콜라겐 펩타이드", "ingredients": [{"name": "Collagen Peptides (Bovine)", "name_kr": "콜라겐펩타이드(소)", "amount": "20", "unit": "g"}],
     "functionality": "피부 탄력 및 수분 유지에 도움. 관절 건강 지원."},
    {"product_name": "NOW Foods UC-II Type II Collagen", "product_name_kr": "나우푸드 UC-II 타입2 콜라겐",
     "company": "NOW Foods", "category": "콜라겐",
     "main_ingredient": "UC-II 콜라겐", "ingredients": [{"name": "UC-II Standardized Cartilage (Chicken)", "name_kr": "UC-II 표준화 연골(닭)", "amount": "40", "unit": "mg"}],
     "functionality": "관절 건강에 도움. 비변성 2형 콜라겐."},
    # 커큐민/강황
    {"product_name": "NOW Foods Curcumin 500mg", "product_name_kr": "나우푸드 커큐민 500mg",
     "company": "NOW Foods", "category": "기타",
     "main_ingredient": "커큐민", "ingredients": [{"name": "Turmeric Root Extract (95% Curcuminoids)", "name_kr": "강황근추출물(커큐미노이드 95%)", "amount": "500", "unit": "mg"}],
     "functionality": "항산화 작용. 관절 건강에 도움을 줄 수 있음."},
    # 비오틴
    {"product_name": "Nature's Bounty Biotin 10000mcg", "product_name_kr": "네이처스바운티 비오틴 10000mcg",
     "company": "Nature's Bounty", "category": "비타민",
     "main_ingredient": "비오틴", "ingredients": [{"name": "Biotin", "name_kr": "비오틴", "amount": "10000", "unit": "mcg"}],
     "functionality": "모발, 피부, 손톱 건강에 도움. 에너지 대사에 필요."},
    # 엽산
    {"product_name": "Nature Made Folic Acid 400mcg", "product_name_kr": "네이처메이드 엽산 400mcg",
     "company": "Nature Made", "category": "비타민",
     "main_ingredient": "엽산", "ingredients": [{"name": "Folic Acid", "name_kr": "엽산", "amount": "400", "unit": "mcg"}],
     "functionality": "태아 신경관의 정상 발달에 필요. 세포와 혈액 생성에 필요."},
    # 쏘팔메토
    {"product_name": "NOW Foods Saw Palmetto Extract 320mg", "product_name_kr": "나우푸드 쏘팔메토 추출물 320mg",
     "company": "NOW Foods", "category": "기타",
     "main_ingredient": "쏘팔메토", "ingredients": [{"name": "Saw Palmetto Berry Extract", "name_kr": "쏘팔메토 베리 추출물", "amount": "320", "unit": "mg"}],
     "functionality": "전립선 건강에 도움을 줄 수 있음."},
    # 알파리포산
    {"product_name": "NOW Foods Alpha Lipoic Acid 250mg", "product_name_kr": "나우푸드 알파리포산 250mg",
     "company": "NOW Foods", "category": "기타",
     "main_ingredient": "알파리포산", "ingredients": [{"name": "Alpha Lipoic Acid", "name_kr": "알파리포산", "amount": "250", "unit": "mg"}],
     "functionality": "항산화 작용. 에너지 대사 지원."},
    # 크릴 오일
    {"product_name": "Kirkland Signature Krill Oil 500mg", "product_name_kr": "커클랜드 크릴오일 500mg",
     "company": "Kirkland Signature", "category": "오메가-3",
     "main_ingredient": "크릴오일(오메가-3)", "ingredients": [{"name": "Krill Oil", "name_kr": "크릴오일", "amount": "500", "unit": "mg"}, {"name": "EPA", "name_kr": "EPA", "amount": "90", "unit": "mg"}, {"name": "DHA", "name_kr": "DHA", "amount": "50", "unit": "mg"}, {"name": "Astaxanthin", "name_kr": "아스타잔틴", "amount": "100", "unit": "mcg"}],
     "functionality": "혈중 중성지방 감소에 도움. 인지질 형태로 흡수율 우수."},
    # 철분
    {"product_name": "Nature Made Iron 65mg", "product_name_kr": "네이처메이드 철분 65mg",
     "company": "Nature Made", "category": "미네랄",
     "main_ingredient": "철분", "ingredients": [{"name": "Ferrous Sulfate", "name_kr": "황산제일철", "amount": "65", "unit": "mg"}],
     "functionality": "체내 산소 운반과 혈액 생성에 필요."},
]


# ─── 큐레이션: 한국인이 많이 직구하는 해외 OTC 약물 ────────────
CURATED_DRUGS = [
    {"item_name": "Tylenol Extra Strength (타이레놀 엑스트라 스트렝스)", "entp_name": "Kenvue (Johnson & Johnson)", "etc_otc_code": "일반의약품",
     "material_name": "Acetaminophen 500mg", "ingredients": [{"name": "아세트아미노펜", "amount": "500", "unit": "mg"}],
     "efcy_qesitm": "두통, 치통, 근육통, 관절통, 생리통, 감기로 인한 발열 및 통증 완화",
     "use_method_qesitm": "성인: 1회 1~2정, 4~6시간마다 복용. 1일 최대 6정 초과 금지.",
     "atpn_qesitm": "간 손상 위험: 1일 3,000mg 초과 금지. 음주 시 간 손상 위험 증가. 다른 아세트아미노펜 함유 제품과 함께 복용 금지.",
     "intrc_qesitm": "와파린(항응고제)과 병용 시 출혈 위험 증가. 간독성 약물과 병용 주의."},
    {"item_name": "Advil (애드빌 이부프로펜)", "entp_name": "Haleon (GSK)", "etc_otc_code": "일반의약품",
     "material_name": "Ibuprofen 200mg", "ingredients": [{"name": "이부프로펜", "amount": "200", "unit": "mg"}],
     "efcy_qesitm": "두통, 치통, 근육통, 관절통, 생리통, 감기로 인한 발열 및 통증 완화, 소염",
     "use_method_qesitm": "성인: 1회 1정, 4~6시간마다 복용. 1일 최대 3정.",
     "atpn_qesitm": "위장 출혈 위험. 심혈관 질환 위험 증가 가능. 아스피린과 병용 시 아스피린의 심장보호 효과 감소.",
     "intrc_qesitm": "아스피린, 항응고제, SSRI 항우울제, ACE억제제, 이뇨제와 병용 주의."},
    {"item_name": "Aleve (얼리브 나프록센)", "entp_name": "Bayer", "etc_otc_code": "일반의약품",
     "material_name": "Naproxen Sodium 220mg", "ingredients": [{"name": "나프록센나트륨", "amount": "220", "unit": "mg"}],
     "efcy_qesitm": "두통, 근육통, 치통, 생리통, 관절통, 감기로 인한 발열 및 통증 완화",
     "use_method_qesitm": "성인: 1회 1정, 8~12시간마다 복용. 1일 최대 3정.",
     "atpn_qesitm": "위장 출혈 위험. 12시간 지속형이므로 과량 복용 주의.",
     "intrc_qesitm": "항응고제, 아스피린, 다른 NSAID, ACE억제제, 리튬과 병용 주의."},
    {"item_name": "Zyrtec (지르텍 세티리진)", "entp_name": "Johnson & Johnson", "etc_otc_code": "일반의약품",
     "material_name": "Cetirizine Hydrochloride 10mg", "ingredients": [{"name": "세티리진염산염", "amount": "10", "unit": "mg"}],
     "efcy_qesitm": "알레르기성 비염 (재채기, 콧물, 코막힘), 두드러기, 가려움증 완화",
     "use_method_qesitm": "성인: 1일 1회 1정 복용.",
     "atpn_qesitm": "졸음 유발 가능. 운전 및 기계 조작 시 주의.",
     "intrc_qesitm": "알코올, 중추신경억제제와 병용 시 졸음 증가."},
    {"item_name": "Claritin (클라리틴 로라타딘)", "entp_name": "Bayer", "etc_otc_code": "일반의약품",
     "material_name": "Loratadine 10mg", "ingredients": [{"name": "로라타딘", "amount": "10", "unit": "mg"}],
     "efcy_qesitm": "알레르기성 비염 (재채기, 콧물, 코막힘), 두드러기 완화",
     "use_method_qesitm": "성인: 1일 1회 1정 복용.",
     "atpn_qesitm": "비졸음성 항히스타민제. 간 질환 시 용량 조절 필요.",
     "intrc_qesitm": "에리스로마이신, 시메티딘과 병용 시 혈중 농도 증가 가능."},
    {"item_name": "Benadryl (베나드릴 디펜히드라민)", "entp_name": "Johnson & Johnson", "etc_otc_code": "일반의약품",
     "material_name": "Diphenhydramine Hydrochloride 25mg", "ingredients": [{"name": "디펜히드라민염산염", "amount": "25", "unit": "mg"}],
     "efcy_qesitm": "알레르기 반응 (두드러기, 재채기, 콧물, 가려움), 불면증 보조, 멀미 예방",
     "use_method_qesitm": "성인: 1회 1~2정, 4~6시간마다 복용. 1일 최대 6정.",
     "atpn_qesitm": "강한 졸음 유발. 운전/기계 조작 금지. 고령자 주의.",
     "intrc_qesitm": "MAO억제제, 알코올, 진정제, 수면제와 병용 금지."},
    {"item_name": "Pepto-Bismol (펩토비스몰)", "entp_name": "Procter & Gamble", "etc_otc_code": "일반의약품",
     "material_name": "Bismuth Subsalicylate 262mg", "ingredients": [{"name": "비스무트차살리실산염", "amount": "262", "unit": "mg"}],
     "efcy_qesitm": "설사, 속쓰림, 소화불량, 메스꺼움, 위 불편감 완화",
     "use_method_qesitm": "성인: 1회 2정, 30분~1시간마다 복용. 1일 최대 16정.",
     "atpn_qesitm": "혀와 대변이 검게 변할 수 있음 (정상). 살리실산 성분 함유.",
     "intrc_qesitm": "아스피린 및 NSAID와 병용 시 살리실산 과다 위험. 항응고제, 당뇨약과 병용 주의. 테트라사이클린 항생제 흡수 방해."},
    {"item_name": "Prilosec OTC (프릴로섹 오메프라졸)", "entp_name": "Procter & Gamble", "etc_otc_code": "일반의약품",
     "material_name": "Omeprazole Magnesium 20mg", "ingredients": [{"name": "오메프라졸마그네슘", "amount": "20", "unit": "mg"}],
     "efcy_qesitm": "위산 과다에 의한 속쓰림 치료. 위식도역류질환(GERD) 치료.",
     "use_method_qesitm": "1일 1회, 아침 식사 전 복용. 14일간 복용 후 4개월 이상 간격을 두고 재복용.",
     "atpn_qesitm": "14일 이상 연속 복용 금지(의사 상담 필요). 장기 복용 시 마그네슘 결핍, 골절 위험.",
     "intrc_qesitm": "클로피도그렐(항혈전제) 효과 감소. 메토트렉세이트, 디곡신과 병용 주의."},
    {"item_name": "Tums (텀스 탄산칼슘)", "entp_name": "Haleon (GSK)", "etc_otc_code": "일반의약품",
     "material_name": "Calcium Carbonate 750mg", "ingredients": [{"name": "탄산칼슘", "amount": "750", "unit": "mg"}],
     "efcy_qesitm": "속쓰림, 위산과다, 신물 올라옴 완화",
     "use_method_qesitm": "증상 발생 시 1~2정 씹어 복용. 1일 최대 15정.",
     "atpn_qesitm": "2주 이상 사용 시 의사 상담. 신장 질환 시 주의.",
     "intrc_qesitm": "테트라사이클린, 플루오로퀴놀론 항생제 흡수 방해. 철분제 흡수 감소. 비타민D와 병용 시 고칼슘혈증 위험."},
    {"item_name": "Motrin (모트린 이부프로펜)", "entp_name": "Johnson & Johnson", "etc_otc_code": "일반의약품",
     "material_name": "Ibuprofen 200mg", "ingredients": [{"name": "이부프로펜", "amount": "200", "unit": "mg"}],
     "efcy_qesitm": "두통, 근육통, 치통, 생리통, 관절통, 감기 발열 및 통증 완화",
     "use_method_qesitm": "성인: 1회 1정, 4~6시간마다 복용. 1일 최대 3정.",
     "atpn_qesitm": "위장 출혈 위험. 심혈관 위험.",
     "intrc_qesitm": "아스피린, 항응고제, SSRI, ACE억제제, 이뇨제와 병용 주의."},
    {"item_name": "Excedrin (엑세드린 두통약)", "entp_name": "Haleon (GSK)", "etc_otc_code": "일반의약품",
     "material_name": "Acetaminophen 250mg, Aspirin 250mg, Caffeine 65mg",
     "ingredients": [{"name": "아세트아미노펜", "amount": "250", "unit": "mg"}, {"name": "아스피린", "amount": "250", "unit": "mg"}, {"name": "카페인", "amount": "65", "unit": "mg"}],
     "efcy_qesitm": "두통(긴장성 두통, 편두통 포함) 완화",
     "use_method_qesitm": "성인: 1회 2정 복용. 6시간마다 반복 가능. 1일 최대 8정.",
     "atpn_qesitm": "아스피린+아세트아미노펜 복합제. 위장 출혈 및 간 손상 위험. 카페인 함유.",
     "intrc_qesitm": "항응고제, 다른 NSAID, 아세트아미노펜 제제와 병용 금지."},
    {"item_name": "NyQuil Cold & Flu (나이퀼 감기약)", "entp_name": "Procter & Gamble", "etc_otc_code": "일반의약품",
     "material_name": "Acetaminophen 325mg, Dextromethorphan HBr 15mg, Doxylamine Succinate 6.25mg",
     "ingredients": [{"name": "아세트아미노펜", "amount": "325", "unit": "mg"}, {"name": "덱스트로메토르판", "amount": "15", "unit": "mg"}, {"name": "독시라민", "amount": "6.25", "unit": "mg"}],
     "efcy_qesitm": "감기 및 독감 증상 완화: 두통, 발열, 기침, 콧물, 재채기. 야간용(수면 보조 성분 포함).",
     "use_method_qesitm": "성인: 1회 2정 (또는 30mL), 6시간마다 복용. 1일 최대 4회.",
     "atpn_qesitm": "강한 졸음 유발. 알코올과 절대 병용 금지. 다른 아세트아미노펜 제품 병용 금지.",
     "intrc_qesitm": "MAO억제제와 병용 금지. 알코올, 진정제, 수면제, 항우울제와 병용 주의."},
    {"item_name": "DayQuil Cold & Flu (데이퀼 감기약)", "entp_name": "Procter & Gamble", "etc_otc_code": "일반의약품",
     "material_name": "Acetaminophen 325mg, Dextromethorphan HBr 10mg, Phenylephrine HCl 5mg",
     "ingredients": [{"name": "아세트아미노펜", "amount": "325", "unit": "mg"}, {"name": "덱스트로메토르판", "amount": "10", "unit": "mg"}, {"name": "페닐에프린", "amount": "5", "unit": "mg"}],
     "efcy_qesitm": "감기 및 독감 증상 완화: 두통, 발열, 기침, 코막힘. 주간용(졸음 없음).",
     "use_method_qesitm": "성인: 1회 2정, 4시간마다 복용. 1일 최대 5회.",
     "atpn_qesitm": "다른 아세트아미노펜 제품 병용 금지. 고혈압 환자 주의(페닐에프린).",
     "intrc_qesitm": "MAO억제제와 병용 금지. 고혈압약과 병용 주의."},
    {"item_name": "Allegra (알레그라 펙소페나딘)", "entp_name": "Sanofi", "etc_otc_code": "일반의약품",
     "material_name": "Fexofenadine Hydrochloride 180mg", "ingredients": [{"name": "펙소페나딘염산염", "amount": "180", "unit": "mg"}],
     "efcy_qesitm": "알레르기성 비염 (재채기, 콧물, 코/목/눈 가려움), 두드러기 완화",
     "use_method_qesitm": "성인: 1일 1회 1정 복용.",
     "atpn_qesitm": "비졸음성 항히스타민제. 과일 주스(자몽, 오렌지, 사과)와 함께 복용 시 흡수 감소.",
     "intrc_qesitm": "에리스로마이신, 케토코나졸과 병용 시 혈중 농도 증가."},
    {"item_name": "Nexium 24HR (넥시움 에소메프라졸)", "entp_name": "Haleon (GSK)", "etc_otc_code": "일반의약품",
     "material_name": "Esomeprazole Magnesium 20mg", "ingredients": [{"name": "에소메프라졸마그네슘", "amount": "20", "unit": "mg"}],
     "efcy_qesitm": "빈번한 속쓰림(주 2회 이상) 치료. 위산 분비 억제.",
     "use_method_qesitm": "1일 1회, 아침 식사 전 최소 1시간 전에 복용. 14일 코스.",
     "atpn_qesitm": "14일 이상 연속 복용 금지. 장기 복용 시 뼈 골절, 마그네슘 결핍 위험.",
     "intrc_qesitm": "클로피도그렐 효과 감소. 메토트렉세이트 혈중 농도 증가. 철분·비타민B12 흡수 감소."},
    {"item_name": "Imodium (이모디움 로페라미드)", "entp_name": "Johnson & Johnson", "etc_otc_code": "일반의약품",
     "material_name": "Loperamide Hydrochloride 2mg", "ingredients": [{"name": "로페라미드염산염", "amount": "2", "unit": "mg"}],
     "efcy_qesitm": "급성 설사 증상 완화. 여행자 설사 치료.",
     "use_method_qesitm": "성인: 첫 설사 후 2정, 이후 설사마다 1정 추가. 1일 최대 4정.",
     "atpn_qesitm": "2일 이상 증상 지속 시 의사 상담. 혈변 시 사용 금지. 과량 복용 시 심장 독성.",
     "intrc_qesitm": "P-당단백 억제제(퀴니딘, 리토나비르 등)와 병용 시 심장 독성 증가."},
]


def main():
    db_url = DATABASE_URL_SYNC.replace("postgresql+asyncpg://", "postgresql://")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # ─── 1. 해외 영양제 삽입 ─────────────────────────────
    logger.info("═══ 해외 인기 영양제 삽입 시작 ═══")
    supp_inserted = 0
    supp_skipped = 0

    for supp in CURATED_SUPPLEMENTS:
        name_kr = supp["product_name_kr"]
        full_name = f"{name_kr} ({supp['product_name']})"
        slug = make_slug("intl-supp", supp["product_name"])

        # 중복 체크 (slug 기반)
        cur.execute("SELECT id FROM supplements WHERE slug = %s", (slug,))
        if cur.fetchone():
            supp_skipped += 1
            continue

        # ingredients 한글화
        ingredients_kr = []
        for ing in supp["ingredients"]:
            ingredients_kr.append({
                "name": ing.get("name_kr", ing["name"]),
                "amount": ing.get("amount"),
                "unit": ing.get("unit"),
            })

        try:
            cur.execute(
                """INSERT INTO supplements (
                    product_name, slug, company, main_ingredient,
                    ingredients, functionality, precautions,
                    intake_method, category, source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    full_name, slug, supp["company"],
                    supp["main_ingredient"],
                    json.dumps(ingredients_kr, ensure_ascii=False),
                    supp.get("functionality"),
                    "이 제품은 해외 직구 제품으로, 국내 식약처 인증 제품이 아닙니다. 복용 전 전문가와 상담하세요.",
                    None,
                    supp["category"],
                    "OpenFDA/큐레이션",
                ),
            )
            supp_inserted += 1
        except Exception as e:
            conn.rollback()
            logger.warning("영양제 삽입 실패 (%s): %s", full_name, e)

    conn.commit()
    logger.info("영양제 삽입 완료: %d건 삽입, %d건 건너뜀", supp_inserted, supp_skipped)

    # ─── 2. 해외 OTC 약물 삽입 ──────────────────────────
    logger.info("═══ 해외 인기 OTC 약물 삽입 시작 ═══")
    drug_inserted = 0
    drug_skipped = 0

    for drug in CURATED_DRUGS:
        item_name = drug["item_name"]
        # item_seq: 해외 약물은 INTL- 접두사
        item_seq = f"INTL-{hashlib.md5(item_name.encode()).hexdigest()[:12]}"
        slug = make_slug("intl-drug", item_name)

        # 중복 체크
        cur.execute("SELECT id FROM drugs WHERE item_seq = %s", (item_seq,))
        if cur.fetchone():
            drug_skipped += 1
            continue

        try:
            cur.execute(
                """INSERT INTO drugs (
                    item_seq, item_name, slug, entp_name, etc_otc_code,
                    material_name, ingredients,
                    efcy_qesitm, use_method_qesitm,
                    atpn_qesitm, intrc_qesitm, se_qesitm
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    item_seq, item_name, slug,
                    drug["entp_name"], drug["etc_otc_code"],
                    drug["material_name"],
                    json.dumps(drug["ingredients"], ensure_ascii=False),
                    drug["efcy_qesitm"], drug["use_method_qesitm"],
                    drug["atpn_qesitm"], drug["intrc_qesitm"],
                    None,  # 부작용은 별도 수집 필요
                ),
            )
            drug_inserted += 1
        except Exception as e:
            conn.rollback()
            logger.warning("약물 삽입 실패 (%s): %s", item_name, e)

    conn.commit()
    logger.info("약물 삽입 완료: %d건 삽입, %d건 건너뜀", drug_inserted, drug_skipped)

    # ─── 3. 해외 약물-약물 상호작용 삽입 ──────────────────
    logger.info("═══ 해외 약물 상호작용 삽입 시작 ═══")

    # 주요 상호작용 데이터 (성분 기반)
    INTL_INTERACTIONS = [
        # 아세트아미노펜 상호작용
        ("아세트아미노펜", "이부프로펜", "caution",
         "아세트아미노펜과 이부프로펜을 동시에 복용하면 위장관 부담이 증가할 수 있습니다. 시간 간격을 두고 복용하세요.",
         "아세트아미노펜 + 이부프로펜"),
        ("아세트아미노펜", "나프록센나트륨", "caution",
         "아세트아미노펜과 나프록센을 동시에 복용하면 위장관 및 간 부담이 증가할 수 있습니다.",
         "아세트아미노펜 + 나프록센"),
        ("아세트아미노펜", "아스피린", "caution",
         "아세트아미노펜과 아스피린을 함께 복용하면 위장 출혈 및 간 손상 위험이 증가합니다.",
         "아세트아미노펜 + 아스피린"),
        # NSAID 상호작용
        ("이부프로펜", "나프록센나트륨", "danger",
         "이부프로펜과 나프록센을 함께 복용하면 위장 출혈 및 신장 손상 위험이 크게 증가합니다. 동시 복용 금지.",
         "NSAID 중복 (이부프로펜 + 나프록센)"),
        ("이부프로펜", "아스피린", "warning",
         "이부프로펜이 아스피린의 항혈소판(심장보호) 효과를 감소시킬 수 있습니다. 아스피린을 먼저 복용하고 최소 30분 후에 이부프로펜을 복용하세요.",
         "이부프로펜 + 아스피린"),
        # 항히스타민 상호작용
        ("디펜히드라민염산염", "독시라민", "danger",
         "디펜히드라민과 독시라민을 함께 복용하면 과도한 졸음, 어지러움, 인지장애가 발생할 수 있습니다. 동시 복용 금지.",
         "항히스타민 중복 (디펜히드라민 + 독시라민)"),
        ("세티리진염산염", "디펜히드라민염산염", "warning",
         "세티리진과 디펜히드라민을 함께 복용하면 졸음 효과가 증가합니다.",
         "항히스타민 중복 (세티리진 + 디펜히드라민)"),
        # 소화기 상호작용
        ("오메프라졸마그네슘", "탄산칼슘", "caution",
         "오메프라졸이 위산을 억제하여 칼슘 흡수를 방해할 수 있습니다. 장기 병용 시 골밀도 감소 위험.",
         "PPI + 칼슘"),
        ("오메프라졸마그네슘", "에소메프라졸마그네슘", "danger",
         "같은 계열의 PPI(양성자 펌프 억제제)를 중복 복용하면 과도한 위산 억제로 부작용 위험이 증가합니다.",
         "PPI 중복"),
        # 영양제-약물 상호작용
        ("탄산칼슘", "철분", "warning",
         "칼슘이 철분의 흡수를 방해합니다. 최소 2시간 간격을 두고 복용하세요.",
         "칼슘 + 철분 흡수 경쟁"),
        ("탄산칼슘", "아연", "caution",
         "칼슘이 아연의 흡수를 감소시킬 수 있습니다. 시간 간격을 두고 복용하는 것이 좋습니다.",
         "칼슘 + 아연 흡수 경쟁"),
    ]

    intrc_inserted = 0
    intrc_skipped = 0

    for ingr_a, ingr_b, severity, description, mechanism in INTL_INTERACTIONS:
        # 성분명으로 약물/영양제 ID 찾기
        cur.execute(
            """SELECT id, item_name FROM drugs
               WHERE ingredients::text ILIKE %s
               LIMIT 1""",
            (f"%{ingr_a}%",),
        )
        row_a = cur.fetchone()
        if not row_a:
            cur.execute(
                """SELECT id, product_name FROM supplements
                   WHERE ingredients::text ILIKE %s
                   LIMIT 1""",
                (f"%{ingr_a}%",),
            )
            row_a_supp = cur.fetchone()
            if row_a_supp:
                item_a_type, item_a_id, item_a_name = "supplement", row_a_supp[0], row_a_supp[1]
            else:
                intrc_skipped += 1
                continue
        else:
            item_a_type, item_a_id, item_a_name = "drug", row_a[0], row_a[1]

        cur.execute(
            """SELECT id, item_name FROM drugs
               WHERE ingredients::text ILIKE %s
               LIMIT 1""",
            (f"%{ingr_b}%",),
        )
        row_b = cur.fetchone()
        if not row_b:
            cur.execute(
                """SELECT id, product_name FROM supplements
                   WHERE ingredients::text ILIKE %s
                   LIMIT 1""",
                (f"%{ingr_b}%",),
            )
            row_b_supp = cur.fetchone()
            if row_b_supp:
                item_b_type, item_b_id, item_b_name = "supplement", row_b_supp[0], row_b_supp[1]
            else:
                intrc_skipped += 1
                continue
        else:
            item_b_type, item_b_id, item_b_name = "drug", row_b[0], row_b[1]

        # 중복 체크
        source_id = f"INTL-{hashlib.md5(f'{ingr_a}:{ingr_b}'.encode()).hexdigest()[:12]}"
        cur.execute("SELECT id FROM interactions WHERE source_id = %s", (source_id,))
        if cur.fetchone():
            intrc_skipped += 1
            continue

        try:
            cur.execute(
                """INSERT INTO interactions (
                    item_a_type, item_a_id, item_a_name,
                    item_b_type, item_b_id, item_b_name,
                    severity, description, mechanism,
                    source, source_id, evidence_level
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    item_a_type, item_a_id, item_a_name,
                    item_b_type, item_b_id, item_b_name,
                    severity, description, mechanism,
                    "OpenFDA/큐레이션", source_id, "moderate",
                ),
            )
            intrc_inserted += 1
        except Exception as e:
            conn.rollback()
            logger.warning("상호작용 삽입 실패: %s", e)

    conn.commit()
    logger.info("상호작용 삽입 완료: %d건 삽입, %d건 건너뜀", intrc_inserted, intrc_skipped)

    # ─── 4. 캐시 무효화 안내 ─────────────────────────────
    # 최종 통계
    cur.execute("SELECT COUNT(*) FROM drugs")
    total_drugs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM supplements")
    total_supplements = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cur.fetchone()[0]

    cur.close()
    conn.close()

    logger.info("══════════════════════════════════════")
    logger.info("  해외 데이터 수집 완료")
    logger.info("══════════════════════════════════════")
    logger.info("  영양제: +%d건 (전체 %d건)", supp_inserted, total_supplements)
    logger.info("  약물:   +%d건 (전체 %d건)", drug_inserted, total_drugs)
    logger.info("  상호작용: +%d건 (전체 %d건)", intrc_inserted, total_interactions)
    logger.info("══════════════════════════════════════")
    logger.info("⚠ Redis 캐시 초기화 필요: browse counts, search 캐시 삭제 권장")


if __name__ == "__main__":
    main()
