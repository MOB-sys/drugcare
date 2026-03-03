-- 건강기능식품 시드 데이터 v2 — 실제 시판 건강기능식품 기반
-- 기존 97건 + 신규 추가 (중복은 slug UNIQUE로 자동 방지)

-- ========== 프로바이오틱스 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 락토핏 골드', 'supp-jonggeundang-lactofit-gold', '종근당건강', '프로바이오틱스 혼합균주',
 '[{"name":"프로바이오틱스 혼합균주","amount":"100","unit":"억 CFU"},{"name":"프락토올리고당","amount":"2000","unit":"mg"}]',
 '유산균 증식 및 유해균 억제, 배변활동 원활', '과다 섭취 시 복부팽만 가능', '1일 1회, 1포', '프로바이오틱스', '시판제품'),
('뉴트리원 프로바이오틱스 19', 'supp-nutrione-probio19', '뉴트리원', '19종 복합 유산균',
 '[{"name":"19종 혼합유산균","amount":"100","unit":"억 CFU"},{"name":"아연","amount":"2.55","unit":"mg"}]',
 '유산균 증식 및 유해균 억제', '유당 불내증이 있는 경우 주의', '1일 1회, 1캡슐', '프로바이오틱스', '시판제품'),
('한미양행 프로바이오틱스 플러스', 'supp-hanmi-probiotics-plus', '한미양행', '락토바실러스 복합균주',
 '[{"name":"락토바실러스 애시도필러스","amount":"50","unit":"억 CFU"},{"name":"비피도박테리움 롱검","amount":"50","unit":"억 CFU"}]',
 '장 내 유익균 증식, 유해균 억제', '개봉 후 빠른 섭취 권장', '1일 1회, 2캡슐', '프로바이오틱스', '시판제품'),
('일양약품 듀오락 골드', 'supp-ilyang-duolac-gold', '일양약품', '듀얼코팅 유산균',
 '[{"name":"락토바실러스 람노서스","amount":"50","unit":"억 CFU"},{"name":"비피도박테리움 애니말리스","amount":"50","unit":"억 CFU"}]',
 '장 건강 개선, 유산균 증식', '냉장 보관 권장', '1일 1회, 1캡슐', '프로바이오틱스', '시판제품'),
('CJ 비오비타 프리미엄', 'supp-cj-biovita-premium', 'CJ제일제당', '생유산균 복합',
 '[{"name":"17종 혼합유산균","amount":"100","unit":"억 CFU"},{"name":"비타민C","amount":"100","unit":"mg"}]',
 '장 건강 및 면역력 강화', NULL, '1일 1회, 1포', '프로바이오틱스', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 오메가-3 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 알티지 오메가3', 'supp-jonggeundang-rtg-omega3', '종근당건강', 'rTG 오메가-3',
 '[{"name":"EPA","amount":"600","unit":"mg"},{"name":"DHA","amount":"400","unit":"mg"}]',
 '혈행 개선, 혈중 중성지방 감소, 기억력 개선', '수술 전 복용 중단 권장', '1일 1회, 2캡슐', '오메가지방산', '시판제품'),
('뉴트리디데이 프리미엄 오메가3', 'supp-nutridday-premium-omega3', '뉴트리디데이', 'rTG 오메가-3',
 '[{"name":"EPA","amount":"500","unit":"mg"},{"name":"DHA","amount":"340","unit":"mg"},{"name":"비타민E","amount":"11.2","unit":"mg"}]',
 '혈중 중성지방 감소, DHA 두뇌 건강', '항응고제 복용 시 의사 상담', '1일 1회, 2캡슐', '오메가지방산', '시판제품'),
('GNM 자연의품격 알티지 오메가3', 'supp-gnm-rtg-omega3', 'GNM자연의품격', 'rTG 오메가-3',
 '[{"name":"EPA","amount":"450","unit":"mg"},{"name":"DHA","amount":"300","unit":"mg"}]',
 '혈행 개선, 건조한 눈 개선', NULL, '1일 1회, 2캡슐', '오메가지방산', '시판제품'),
('대웅제약 오메가쓰리 플러스', 'supp-daewoong-omega3-plus', '대웅제약', '정제어유 오메가-3',
 '[{"name":"EPA","amount":"360","unit":"mg"},{"name":"DHA","amount":"240","unit":"mg"},{"name":"비타민D","amount":"25","unit":"mcg"}]',
 '혈중 중성지방 개선, 뼈 건강', NULL, '1일 1회, 2캡슐', '오메가지방산', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 비타민D ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 비타민D 2000IU', 'supp-jonggeundang-vitd-2000', '종근당건강', '비타민D3',
 '[{"name":"비타민D3(콜레칼시페롤)","amount":"2000","unit":"IU"}]',
 '칼슘 흡수 촉진, 뼈 건강, 면역 기능', '고칼슘혈증 환자 주의', '1일 1회, 1정', '비타민', '시판제품'),
('고려은단 비타민D 4000IU', 'supp-koreaeundan-vitd-4000', '고려은단', '비타민D3',
 '[{"name":"비타민D3(콜레칼시페롤)","amount":"4000","unit":"IU"}]',
 '뼈 건강, 면역력 증진', '과다 섭취 시 고칼슘혈증 위험', '1일 1회, 1정', '비타민', '시판제품'),
('뉴트리원 비타민D 드롭스', 'supp-nutrione-vitd-drops', '뉴트리원', '비타민D3',
 '[{"name":"비타민D3(콜레칼시페롤)","amount":"1000","unit":"IU"}]',
 '뼈 건강, 칼슘 흡수 촉진', NULL, '1일 1회, 1방울', '비타민', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 비타민C ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('고려은단 메가도스C 2000', 'supp-koreaeundan-megadosec', '고려은단', '비타민C',
 '[{"name":"비타민C(아스코르브산)","amount":"2000","unit":"mg"}]',
 '항산화, 면역력 증진, 피로 개선', '위장이 약한 분은 식후 복용', '1일 1회, 1포', '비타민', '시판제품'),
('레모나 비타민C 1000', 'supp-lemona-vitc-1000', '경남제약', '비타민C',
 '[{"name":"비타민C(아스코르브산)","amount":"1000","unit":"mg"}]',
 '항산화, 피부 건강, 면역력', NULL, '1일 1회, 1포', '비타민', '시판제품'),
('일동제약 아로나민C 플러스', 'supp-ildong-aronaminc-plus', '일동제약', '비타민C + 아연',
 '[{"name":"비타민C","amount":"500","unit":"mg"},{"name":"아연","amount":"8.5","unit":"mg"}]',
 '항산화, 면역력 증진', NULL, '1일 1회, 1정', '비타민', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 종합비타민 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('센트룸 멀티비타민', 'supp-centrum-multi', '한국화이자', '종합 비타민미네랄',
 '[{"name":"비타민A","amount":"750","unit":"mcg"},{"name":"비타민C","amount":"100","unit":"mg"},{"name":"비타민D","amount":"10","unit":"mcg"},{"name":"비타민E","amount":"15","unit":"mg"},{"name":"비타민B1","amount":"1.5","unit":"mg"},{"name":"비타민B2","amount":"1.7","unit":"mg"},{"name":"비타민B6","amount":"2","unit":"mg"},{"name":"비타민B12","amount":"6","unit":"mcg"},{"name":"엽산","amount":"400","unit":"mcg"},{"name":"철","amount":"8","unit":"mg"},{"name":"아연","amount":"11","unit":"mg"}]',
 '체내 영양 균형, 에너지 대사, 면역력', '철분 과다 섭취 주의', '1일 1회, 1정', '종합영양', '시판제품'),
('얼라이브 원스데일리 멀티', 'supp-alive-oncedaily', '네이처스웨이', '23종 비타민미네랄',
 '[{"name":"비타민A","amount":"900","unit":"mcg"},{"name":"비타민C","amount":"180","unit":"mg"},{"name":"비타민D","amount":"25","unit":"mcg"},{"name":"비타민K","amount":"80","unit":"mcg"},{"name":"아연","amount":"15","unit":"mg"}]',
 '멀티 영양 보충, 에너지 대사', NULL, '1일 1회, 1정', '종합영양', '시판제품'),
('뉴트리원 올인원 멀티비타민', 'supp-nutrione-allinone-multi', '뉴트리원', '16종 비타민미네랄',
 '[{"name":"비타민C","amount":"200","unit":"mg"},{"name":"비타민D","amount":"25","unit":"mcg"},{"name":"비타민B군 복합","amount":null,"unit":null},{"name":"아연","amount":"8.5","unit":"mg"},{"name":"셀레늄","amount":"55","unit":"mcg"}]',
 '체내 영양 균형', NULL, '1일 1회, 2정', '종합영양', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 홍삼 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('정관장 홍삼정 에브리타임', 'supp-kgc-everytime', '정관장', '홍삼농축액',
 '[{"name":"홍삼농축액","amount":"3000","unit":"mg"},{"name":"진세노사이드 Rg1+Rb1+Rg3","amount":"10","unit":"mg"}]',
 '면역력 증진, 피로 개선, 항산화', '고혈압 환자 의사 상담', '1일 1회, 1포(10ml)', '면역력', '시판제품'),
('정관장 활기력', 'supp-kgc-hwalgeryeok', '정관장', '홍삼 + 비타민B',
 '[{"name":"홍삼농축액","amount":"1600","unit":"mg"},{"name":"비타민B1","amount":"25","unit":"mg"},{"name":"비타민B2","amount":"25","unit":"mg"},{"name":"비타민B6","amount":"25","unit":"mg"}]',
 '피로 개선, 에너지 대사', NULL, '1일 1회, 1병', '면역력', '시판제품'),
('풍기인삼 홍삼진액 골드', 'supp-punggi-hongsam-gold', '풍기특산물영농조합', '6년근 홍삼액',
 '[{"name":"홍삼농축액","amount":"3000","unit":"mg"},{"name":"진세노사이드","amount":"8","unit":"mg"}]',
 '면역력 증진, 피로 개선', '어린이, 임산부 섭취 주의', '1일 1회, 1포', '면역력', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 루테인/눈 건강 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('안국건강 루테인 지아잔틴 미니', 'supp-anguk-lutein-zeaxanthin', '안국건강', '루테인+지아잔틴',
 '[{"name":"루테인","amount":"20","unit":"mg"},{"name":"지아잔틴","amount":"4","unit":"mg"}]',
 '노화로 인한 황반색소 밀도 유지, 눈 건강', NULL, '1일 1회, 1캡슐', '눈건강', '시판제품'),
('뉴트리원 루테인 오메가3', 'supp-nutrione-lutein-omega3', '뉴트리원', '루테인+오메가3',
 '[{"name":"루테인","amount":"20","unit":"mg"},{"name":"EPA","amount":"180","unit":"mg"},{"name":"DHA","amount":"120","unit":"mg"}]',
 '눈 건강, 건조한 눈 개선', NULL, '1일 1회, 1캡슐', '눈건강', '시판제품'),
('GNM 자연의품격 루테인골드', 'supp-gnm-lutein-gold', 'GNM자연의품격', '마리골드 루테인',
 '[{"name":"루테인","amount":"20","unit":"mg"},{"name":"지아잔틴","amount":"4","unit":"mg"},{"name":"비타민A","amount":"700","unit":"mcg"}]',
 '황반색소 밀도 유지, 눈 피로 개선', NULL, '1일 1회, 1캡슐', '눈건강', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 밀크씨슬/간 건강 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 밀크씨슬 간에좋은', 'supp-jonggeundang-milkthistle', '종근당건강', '밀크씨슬(실리마린)',
 '[{"name":"밀크씨슬추출물(실리마린)","amount":"130","unit":"mg"}]',
 '간 건강 보호, 간세포 재생 촉진', '담도 폐쇄 환자 주의', '1일 1회, 1정', '간건강', '시판제품'),
('대웅제약 우루사 간장약', 'supp-daewoong-ursa', '대웅제약', 'UDCA',
 '[{"name":"우르소데옥시콜산(UDCA)","amount":"100","unit":"mg"}]',
 '간기능 개선, 담즙 분비 촉진', '담석 환자 주의', '1일 3회, 1정', '간건강', '시판제품'),
('GNM 밀크씨슬 플러스', 'supp-gnm-milkthistle-plus', 'GNM자연의품격', '밀크씨슬+비타민B',
 '[{"name":"밀크씨슬추출물","amount":"130","unit":"mg"},{"name":"비타민B1","amount":"12","unit":"mg"},{"name":"비타민B6","amount":"15","unit":"mg"}]',
 '간 건강, 피로 개선', NULL, '1일 1회, 1정', '간건강', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 글루코사민/관절 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 글루코사민 골드', 'supp-jonggeundang-glucosamine', '종근당건강', 'N-아세틸글루코사민',
 '[{"name":"N-아세틸글루코사민","amount":"1500","unit":"mg"},{"name":"상어연골추출물","amount":"500","unit":"mg"}]',
 '관절 연골 건강, 관절 기능 개선', '갑각류 알레르기 주의', '1일 3회, 2정', '관절건강', '시판제품'),
('관절엔 콘드로이친 1200', 'supp-gwanjeolen-chondroitin', '안국건강', '콘드로이친+MSM',
 '[{"name":"상어연골분말(콘드로이친)","amount":"1200","unit":"mg"},{"name":"MSM","amount":"1500","unit":"mg"}]',
 '관절 연골 보호, 관절 통증 완화', NULL, '1일 2회, 2정', '관절건강', '시판제품'),
('한미양행 보스웰리아 플러스', 'supp-hanmi-boswellia-plus', '한미양행', '보스웰리아추출물',
 '[{"name":"보스웰리아추출물","amount":"500","unit":"mg"},{"name":"초록입홍합추출물","amount":"200","unit":"mg"}]',
 '관절 건강, 관절 불편감 개선', NULL, '1일 1회, 1정', '관절건강', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 콜라겐/피부 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('뉴트리원 저분자 콜라겐', 'supp-nutrione-collagen', '뉴트리원', '저분자 피쉬 콜라겐',
 '[{"name":"저분자 피쉬콜라겐 펩타이드","amount":"1000","unit":"mg"},{"name":"비타민C","amount":"200","unit":"mg"},{"name":"히알루론산","amount":"20","unit":"mg"}]',
 '피부 보습, 탄력, 자외선 피부손상 개선', NULL, '1일 1회, 1포', '피부건강', '시판제품'),
('닥터린 이너뷰티 콜라겐', 'supp-drlin-innerbeauty-collagen', '뉴트리원', '초저분자 콜라겐',
 '[{"name":"초저분자 콜라겐 트리펩타이드","amount":"500","unit":"mg"},{"name":"엘라스틴","amount":"50","unit":"mg"},{"name":"비타민C","amount":"100","unit":"mg"}]',
 '피부 탄력, 보습 개선', NULL, '1일 1회, 1포', '피부건강', '시판제품'),
('에버콜라겐 타임 비오틴', 'supp-evercollagen-time-biotin', '에버콜라겐', '저분자 콜라겐+비오틴',
 '[{"name":"저분자 콜라겐 펩타이드","amount":"1200","unit":"mg"},{"name":"비오틴","amount":"30","unit":"mcg"},{"name":"비타민C","amount":"100","unit":"mg"}]',
 '피부 건강, 모발 건강', NULL, '1일 1회, 1정', '피부건강', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 마그네슘 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('고려은단 마그네슘 400', 'supp-koreaeundan-mag400', '고려은단', '산화마그네슘',
 '[{"name":"마그네슘","amount":"400","unit":"mg"}]',
 '에너지 대사, 신경 및 근육 기능 유지', '신장 질환자 주의', '1일 1회, 1정', '미네랄', '시판제품'),
('종근당 마그비 프리미엄', 'supp-jonggeundang-magbi', '종근당건강', '마그네슘+비타민B6',
 '[{"name":"마그네슘","amount":"400","unit":"mg"},{"name":"비타민B6","amount":"15","unit":"mg"}]',
 '에너지 대사, 근육 이완, 수면 개선', NULL, '1일 1회, 2정', '미네랄', '시판제품'),
('뉴트리원 마그네슘 트리플렉스', 'supp-nutrione-mag-triplex', '뉴트리원', '3종 마그네슘 복합',
 '[{"name":"산화마그네슘","amount":"200","unit":"mg"},{"name":"구연산마그네슘","amount":"100","unit":"mg"},{"name":"글리시네이트마그네슘","amount":"100","unit":"mg"}]',
 '에너지 대사, 신경·근육 기능', NULL, '1일 1회, 2정', '미네랄', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 철분 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('일동제약 훼럼킨 철분', 'supp-ildong-ferumkin', '일동제약', '헴철',
 '[{"name":"헴철","amount":"12","unit":"mg"},{"name":"비타민C","amount":"50","unit":"mg"},{"name":"엽산","amount":"400","unit":"mcg"}]',
 '철분 보충, 빈혈 예방', '과다 섭취 주의, 차/커피와 간격 두기', '1일 1회, 1캡슐', '미네랄', '시판제품'),
('솔가 젠틀 아이언', 'supp-solgar-gentle-iron', '솔가', '킬레이트 철분',
 '[{"name":"철분(비스글리시네이트철)","amount":"25","unit":"mg"}]',
 '체내 산소 운반, 빈혈 예방', '위장장애 적음', '1일 1회, 1캡슐', '미네랄', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 칼슘 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 칼슘 마그네슘 비타민D', 'supp-jonggeundang-cal-mag-d', '종근당건강', '칼슘+마그네슘+비타민D',
 '[{"name":"칼슘","amount":"500","unit":"mg"},{"name":"마그네슘","amount":"250","unit":"mg"},{"name":"비타민D","amount":"10","unit":"mcg"}]',
 '뼈 건강, 골다공증 예방', '신장질환자 의사 상담', '1일 1회, 2정', '미네랄', '시판제품'),
('뉴트리원 칼슘+D 츄어블', 'supp-nutrione-calcium-d-chew', '뉴트리원', '탄산칼슘+비타민D',
 '[{"name":"칼슘","amount":"600","unit":"mg"},{"name":"비타민D","amount":"25","unit":"mcg"}]',
 '뼈 건강, 칼슘 보충', NULL, '1일 1회, 2정', '미네랄', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 아연 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('뉴트리원 킬레이트 아연', 'supp-nutrione-chelate-zinc', '뉴트리원', '글루콘산아연',
 '[{"name":"아연","amount":"12","unit":"mg"}]',
 '면역력 증진, 정상적인 세포분열', '공복 복용 시 메스꺼움 가능', '1일 1회, 1정', '미네랄', '시판제품'),
('솔가 아연 피콜리네이트', 'supp-solgar-zinc-picolinate', '솔가', '아연 피콜리네이트',
 '[{"name":"아연(피콜리네이트)","amount":"22","unit":"mg"}]',
 '면역 기능, 피부 건강', '구리 결핍 주의(장기 복용 시)', '1일 1회, 1정', '미네랄', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 비타민B군 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('일동제약 아로나민 골드', 'supp-ildong-aronamin-gold', '일동제약', '활성형 비타민B군',
 '[{"name":"벤포티아민(B1)","amount":"100","unit":"mg"},{"name":"리보플라빈(B2)","amount":"5","unit":"mg"},{"name":"피리독살포스페이트(B6)","amount":"50","unit":"mg"},{"name":"메코발라민(B12)","amount":"1500","unit":"mcg"}]',
 '만성 피로, 어깨결림, 눈 피로 개선', NULL, '1일 1회, 1정', '비타민', '시판제품'),
('뉴트리원 비타민B 컴플렉스', 'supp-nutrione-vitb-complex', '뉴트리원', '비타민B군 8종 복합',
 '[{"name":"비타민B1","amount":"100","unit":"mg"},{"name":"비타민B2","amount":"20","unit":"mg"},{"name":"나이아신","amount":"20","unit":"mg"},{"name":"판토텐산","amount":"25","unit":"mg"},{"name":"비타민B6","amount":"25","unit":"mg"},{"name":"비오틴","amount":"150","unit":"mcg"},{"name":"엽산","amount":"400","unit":"mcg"},{"name":"비타민B12","amount":"100","unit":"mcg"}]',
 '에너지 대사, 피로 개선', '소변 색 변화 가능(정상)', '1일 1회, 1정', '비타민', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 코엔자임Q10 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 코큐텐 100', 'supp-jonggeundang-coq10-100', '종근당건강', '코엔자임Q10',
 '[{"name":"코엔자임Q10","amount":"100","unit":"mg"}]',
 '항산화, 심혈관 건강, 에너지 생성', '항응고제 복용 시 상담', '1일 1회, 1캡슐', '항산화', '시판제품'),
('뉴트리원 코큐텐 플러스', 'supp-nutrione-coq10-plus', '뉴트리원', '코엔자임Q10+비타민E',
 '[{"name":"코엔자임Q10","amount":"100","unit":"mg"},{"name":"비타민E","amount":"11.2","unit":"mg"}]',
 '항산화, 세포 에너지 생성', NULL, '1일 1회, 1캡슐', '항산화', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 크릴오일 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 크릴오일 56', 'supp-jonggeundang-krilloil', '종근당건강', '남극 크릴오일',
 '[{"name":"크릴오일","amount":"1000","unit":"mg"},{"name":"인지질(포스파티딜콜린)","amount":"400","unit":"mg"},{"name":"아스타잔틴","amount":"100","unit":"mcg"}]',
 '혈중 중성지방 개선, 기억력 개선', '갑각류 알레르기 주의', '1일 1회, 2캡슐', '혈행개선', '시판제품'),
('뉴트리원 크릴오일 프리미엄', 'supp-nutrione-krilloil-premium', '뉴트리원', '남극 크릴오일',
 '[{"name":"크릴오일","amount":"1000","unit":"mg"},{"name":"EPA","amount":"75","unit":"mg"},{"name":"DHA","amount":"45","unit":"mg"}]',
 '혈행 개선, 뇌 기능 개선', NULL, '1일 1회, 2캡슐', '혈행개선', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 비오틴/모발 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('뉴트리원 비오틴 5000', 'supp-nutrione-biotin-5000', '뉴트리원', '비오틴',
 '[{"name":"비오틴","amount":"5000","unit":"mcg"},{"name":"판토텐산칼슘","amount":"200","unit":"mg"}]',
 '모발 건강, 손톱 건강, 에너지 대사', NULL, '1일 1회, 1정', '피부건강', '시판제품'),
('솔가 비오틴 10000', 'supp-solgar-biotin-10000', '솔가', '비오틴',
 '[{"name":"비오틴","amount":"10000","unit":"mcg"}]',
 '모발 및 손톱 건강', NULL, '1일 1회, 1캡슐', '피부건강', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 프로폴리스 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('종근당 프로폴리스 플러스', 'supp-jonggeundang-propolis', '종근당건강', '프로폴리스추출물',
 '[{"name":"프로폴리스추출물","amount":"500","unit":"mg"},{"name":"플라보노이드","amount":"17","unit":"mg"}]',
 '구강 건강, 항산화, 면역력', '꿀벌 알레르기 주의', '1일 1회, 2캡슐', '면역력', '시판제품'),
('뉴트리원 그린 프로폴리스', 'supp-nutrione-green-propolis', '뉴트리원', '브라질산 그린 프로폴리스',
 '[{"name":"프로폴리스추출물","amount":"600","unit":"mg"},{"name":"아르테필린C","amount":"3.5","unit":"mg"}]',
 '항산화, 구강 건강', NULL, '1일 1회, 1캡슐', '면역력', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 엽산 (임산부) ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('뉴트리원 활성엽산 800', 'supp-nutrione-folicacid-800', '뉴트리원', '활성엽산(5-MTHF)',
 '[{"name":"활성엽산(5-MTHF)","amount":"800","unit":"mcg"},{"name":"비타민B12","amount":"2.4","unit":"mcg"}]',
 '태아 신경관 정상 발달, 세포 분열', NULL, '1일 1회, 1정', '여성건강', '시판제품'),
('일동제약 엽산 400', 'supp-ildong-folicacid-400', '일동제약', '엽산',
 '[{"name":"엽산","amount":"400","unit":"mcg"}]',
 '세포 분열, 혈액 생성', NULL, '1일 1회, 1정', '여성건강', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 식이섬유/다이어트 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('뉴트리원 가르시니아 플러스', 'supp-nutrione-garcinia', '뉴트리원', '가르시니아캄보지아추출물(HCA)',
 '[{"name":"가르시니아캄보지아추출물","amount":"1500","unit":"mg"},{"name":"HCA","amount":"750","unit":"mg"}]',
 '체지방 감소, 탄수화물 → 지방 전환 억제', '임산부, 수유부 섭취 주의', '1일 3회, 2정(식전)', '체지방', '시판제품'),
('GNM 다이어트 잔티젠', 'supp-gnm-diet-xanthigen', 'GNM자연의품격', '잔티젠(석류씨유+후코잔틴)',
 '[{"name":"석류씨유","amount":"200","unit":"mg"},{"name":"갈조추출물(후코잔틴)","amount":"200","unit":"mg"}]',
 '체지방 감소', NULL, '1일 2회, 1캡슐', '체지방', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 셀레늄 ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('뉴트리원 셀레늄 200', 'supp-nutrione-selenium-200', '뉴트리원', 'L-셀레노메티오닌',
 '[{"name":"셀레늄","amount":"200","unit":"mcg"}]',
 '항산화, 갑상선 기능, 면역력', '과다 섭취 시 셀레늄 독성 주의', '1일 1회, 1정', '항산화', '시판제품')
ON CONFLICT (slug) DO NOTHING;

-- ========== 비타민K ==========
INSERT INTO supplements (product_name, slug, company, main_ingredient, ingredients, functionality, precautions, intake_method, category, source)
VALUES
('솔가 비타민K2 MK7', 'supp-solgar-vitk2-mk7', '솔가', '비타민K2(MK-7)',
 '[{"name":"비타민K2(메나퀴논-7)","amount":"100","unit":"mcg"}]',
 '뼈 건강, 칼슘 대사', '항응고제(와파린) 복용 시 반드시 의사 상담', '1일 1회, 1캡슐', '비타민', '시판제품')
ON CONFLICT (slug) DO NOTHING;
