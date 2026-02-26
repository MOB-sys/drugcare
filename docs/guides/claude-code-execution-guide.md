# 🚀 Claude Code 실행 가이드 — 약먹어 듀얼 플랫폼

> 터미널에서 Claude Code에게 직접 입력하는 명령어 가이드.
> 기존 FastAPI + Flutter 위에 Next.js 웹을 추가하는 스프린트 구성.

---

## 사전 준비

```bash
# 1. 프로젝트 폴더로 이동
cd ~/workspace/yakmeogeo

# 2. 폴더 구조 생성 (setup-project.sh 실행)
bash setup-project.sh .

# 3. CLAUDE.md 복사 (이미 루트에 없는 경우)
cp CLAUDE.md ./CLAUDE.md

# 4. 에이전트 파일 배치 (dev-squad-agents.md에서 각 AGENT.md 추출하여 복사)
# → 또는 Claude Code에게 아래와 같이 지시

# 5. Claude Code 실행
claude
```

---

## 스프린트 개요

| 스프린트 | 기간 | 내용 | 핵심 |
|---------|------|------|------|
| **Web-1** | 2~3일 | 백엔드 최소 변경 + Next.js 초기화 | 기반 구축 |
| **Web-2** | 3~4일 | 상호작용 체크 웹 페이지 (핵심 기능) | 핵심 가치 |
| **Web-3** | 3~4일 | 약물/영양제 SSG 상세 페이지 (1만개+) | SEO 자산 |
| **Web-4** | 2~3일 | SEO 완성 + AdSense 연동 | 수익화 |
| **Web-5** | 2~3일 | 복약함 웹 + 앱 설치 유도 + QA | 전환 루프 |
| **App-1** | 2~3일 | Flutter 플랫폼 빌드 생성 + 스토어 준비 | 앱 출시 |

---

## Sprint Web-1: 기반 구축 (2~3일)

> 목표: 백엔드에 slug API 추가 + Next.js 프로젝트 초기화

### Step 1: 백엔드 최소 변경

```
PM 에이전트로 행동해. CLAUDE.md와 .agents/dev-squad/pm/AGENT.md를 읽어.

Sprint Web-1을 시작한다.
작업 1: 백엔드에 웹 지원을 위한 최소 변경을 수행해줘.

구체적으로:
1. drugs, supplements 테이블에 slug 컬럼 추가 (Alembic 마이그레이션 v003)
   - slug는 item_seq 기반 또는 item_name의 URL-safe 변환
   - 기존 데이터에 대해 slug 일괄 생성하는 마이그레이션 포함
2. 신규 API 6개 추가:
   - GET /api/v1/drugs/slugs → 전체 slug 목록
   - GET /api/v1/drugs/slug/{slug} → slug로 약물 조회
   - GET /api/v1/supplements/slugs → 전체 slug 목록
   - GET /api/v1/supplements/slug/{slug} → slug로 영양제 조회
   - GET /api/v1/drugs/count → 총 약물 수
   - GET /api/v1/supplements/count → 총 영양제 수
3. CORS 미들웨어에 localhost:3000, yakmeogeo.com 추가
4. DeviceAuth 미들웨어에 웹 세션쿠키 분기 추가

⚠️ 중요: 기존 15개 API 응답 구조 변경 금지. 기존 209개 테스트 전부 통과 유지.

Backend 에이전트의 AGENT.md 규칙을 따라 Sub-agent로 실행해줘.
완료 후 테스트 결과 보고해줘.
```

### Step 2: Next.js 프로젝트 초기화

```
이제 Next.js 웹 프로젝트를 초기화해줘.

1. src/web/ 에서 Next.js 15 프로젝트 생성:
   - npx create-next-app@latest . --typescript --tailwind --app --src-dir
   - 또는 수동으로 package.json + next.config.ts + tsconfig.json 생성
2. 기본 레이아웃 (layout.tsx) 설정:
   - 한국어 lang="ko"
   - 브랜드 색상 #00BFA5
   - 반응형 메타태그
   - GA4 스크립트 (환경변수)
3. API 호출 래퍼 (src/web/src/lib/api/) 생성:
   - FastAPI 백엔드 호출 fetch 함수
   - 환경변수: NEXT_PUBLIC_API_URL, INTERNAL_API_URL
   - 에러 처리 + 타입 안전성
4. 공통 타입 (src/web/src/types/) 정의:
   - Drug, Supplement, Interaction 등 (기존 백엔드 응답과 동일 구조)
   - Severity enum (danger/warning/caution/info/safe)
5. 공통 컴포넌트:
   - Header (로고 + 네비게이션)
   - Footer (면책조항 + 링크)
   - DisclaimerBanner

Web Frontend 에이전트의 AGENT.md 규칙을 따라 실행해줘.
```

### Step 3: 연동 테스트

```
백엔드와 웹이 잘 연동되는지 확인해줘.

1. 백엔드 실행: cd src/backend && uvicorn app.main:app --reload --port 8000
2. 웹 실행: cd src/web && npm run dev (포트 3000)
3. 웹에서 백엔드 API 호출 테스트:
   - / 페이지에서 약물 검색 API 호출 성공 확인
   - CORS 에러 없는지 확인
4. STATUS_BOARD 업데이트
```

---

## Sprint Web-2: 상호작용 체크 (3~4일)

> 목표: 핵심 기능 — 웹에서 약물/영양제 상호작용 체크

```
PM, Sprint Web-2를 시작한다.
약먹어 웹의 핵심 기능인 상호작용 체크 페이지를 만들어줘.

1. /check 페이지 (CSR):
   - 약물/영양제 검색 바 (자동완성)
   - 2개 이상 선택 → "상호작용 확인" 버튼
   - 선택된 아이템 목록 표시 (삭제 가능)
   - 모바일/PC 반응형

2. /check/result 페이지 (SSR):
   - POST /api/v1/interactions/check 호출
   - 결과 요약: "N개 조합 중 M개 상호작용 발견"
   - 신호등 시스템: danger(빨강)/warning(주황)/caution(노랑)/info(파랑)/safe(녹색)
   - 각 상호작용 카드: 약물A ↔ 약물B, severity 배지, 설명, AI 설명
   - 면책조항 배너 (상단 고정)
   - AdSense 배너 (결과 하단)
   - "앱에서 매일 복약 리마인더 받기" CTA

3. OG 이미지 동적 생성 (선택):
   - /api/og/check?items=... → 상호작용 결과 요약 이미지
   - 카카오톡/SNS 공유 시 미리보기

디자인은 Flutter 앱의 신호등 시스템과 동일하게.
Web Frontend + SEO Engineer Sub-agent 협업으로 실행해줘.
```

---

## Sprint Web-3: SSG 상세 페이지 (3~4일)

> 목표: 약물 1만개+ 영양제 500개+ 정적 페이지 생성 → SEO 핵심 자산

```
PM, Sprint Web-3를 시작한다.
SEO의 핵심인 약물/영양제 상세 페이지를 SSG로 생성해줘.

1. /drugs/[slug] 페이지 (SSG):
   - generateStaticParams: /api/v1/drugs/slugs 호출 → 전체 slug 목록
   - generateMetadata: 약물별 title, description, og:image
   - 페이지 내용:
     * 약물명, 제조사, 분류 (전문/일반)
     * 효능효과
     * 용법용량
     * 주의사항 (접고 펼치기)
     * 성분 정보
     * "이 약과의 상호작용 확인하기" → /check 링크
     * 면책조항
     * AdSense 배너
   - JSON-LD 구조화 데이터 (Drug 스키마)

2. /supplements/[slug] 페이지 (SSG):
   - 동일 패턴
   - JSON-LD: DietarySupplement 스키마

3. SEO:
   - sitemap.xml 자동 생성 (1만개+ URL)
   - robots.txt
   - 네이버 서치어드바이저 메타태그

Web Frontend + SEO Engineer + Data Engineer 협업.
⚠️ 빌드 시간 주의: 1만개 SSG는 시간이 오래 걸릴 수 있음.
→ 필요 시 ISR(revalidate: 86400)로 대체 검토.
```

---

## Sprint Web-4: SEO + 광고 (2~3일)

> 목표: AdSense 연동 + SEO 마무리 + Core Web Vitals 최적화

```
PM, Sprint Web-4를 시작한다.

1. AdSense 연동:
   - Google AdSense 스크립트 삽입 (layout.tsx)
   - 광고 배치:
     * 결과 페이지 하단: 배너 (320x100)
     * 약물 상세 하단: 배너
     * 콘텐츠 사이: 네이티브 광고
   - 광고 로드 실패 시 graceful 처리 (빈 공간 숨김)
   - ⚠️ 면책조항/위험 경고를 광고가 가리지 않을 것

2. SEO 최종 점검:
   - Google Search Console 사이트 등록
   - 네이버 서치어드바이저 등록
   - sitemap.xml 제출
   - Core Web Vitals 체크:
     * LCP < 2.5초 (SSG 페이지)
     * FID < 100ms
     * CLS < 0.1
   - 페이지 속도 최적화: Image 최적화, 코드 스플리팅

3. 건강팁 콘텐츠 (선택):
   - /tips/[slug] SSG 페이지 5~10개
   - "무심코 먹으면 위험한 영양제 조합" 등 바이럴 콘텐츠

SEO Engineer 메인 + Web Frontend 서포트로 실행.
```

---

## Sprint Web-5: 복약함 + 앱 유도 + QA (2~3일)

> 목표: 웹 복약함 + 웹→앱 전환 루프 + 최종 QA

```
PM, Sprint Web-5를 시작한다.

1. 웹 복약함 (/cabinet — CSR):
   - localStorage에 복약함 저장 (회원가입 불필요)
   - 약물/영양제 추가 → 자동 상호작용 체크
   - "앱에서 복약 리마인더 받기" → 앱스토어 링크

2. 웹→앱 전환 루프:
   - 모바일 웹 SmartAppBanner (상단)
   - 결과 페이지: "이 조합을 매일 관리하세요 → 앱 설치" CTA
   - 복약함 페이지: "푸시 알림으로 복약 잊지 마세요 → 앱 설치" CTA
   - UTM 파라미터로 웹→앱 전환 추적

3. 최종 QA:
   - 전체 웹 페이지 수동 테스트 (PC + 모바일)
   - 백엔드 기존 209개 테스트 통과 확인
   - Flutter 앱 131개 테스트 통과 확인
   - 웹 테스트 작성 (Vitest + Playwright)
   - SEO 테스트 (sitemap, 메타태그, JSON-LD)
   - 크로스 플랫폼: 동일 API 결과 웹-앱 일치 확인

4. Nginx 프록시 설정:
   - / → Next.js (Vercel 또는 로컬)
   - /api/ → FastAPI
   - SSL 유지

Tester 메인 + 전체 팀 서포트.
```

---

## Sprint App-1: 앱 출시 준비 (2~3일)

> 목표: Flutter 플랫폼 빌드 + 스토어 등록

```
PM, Sprint App-1을 시작한다.
Flutter 앱의 플랫폼 빌드를 생성하고 스토어 출시를 준비해줘.

1. 플랫폼 디렉토리 생성:
   cd src/frontend
   flutter create --platforms=android,ios .

2. Android 설정:
   - AndroidManifest.xml: 인터넷/알림/카메라 권한
   - AdMob App ID 설정
   - minSdkVersion 조정
   - 앱 아이콘 / 스플래시 설정
   - ProGuard 규칙 (난독화)

3. iOS 설정:
   - Info.plist: 알림 권한, ATT 설명, AdMob App ID
   - Podfile CocoaPods 설정
   - 앱 아이콘 / 스플래시 설정

4. 프로덕션 설정:
   - 테스트 AdMob ID → 프로덕션 ID 교체
   - API URL 환경변수 설정
   - 릴리스 빌드 테스트

5. 앱 131개 테스트 전부 통과 확인

App Frontend 에이전트 메인으로 실행.
```

---

## 배포 후: Ops Squad 활성화

```bash
# 1. 스크립트 실행 권한
chmod +x scripts/ops/*.sh

# 2. Cron job 등록
crontab -e
# 위 ops-squad-agents.md의 cron 설정 추가

# 3. 수동 테스트
bash scripts/ops/health-check.sh
bash scripts/ops/qa-monitor.sh
bash scripts/ops/daily-report.sh

# 4. 로그 확인
tail -f ~/workspace/logs/ym-health.log
```

---

## 트러블슈팅

| 상황 | 해결 |
|------|------|
| 기존 테스트 깨짐 | "기존 209개/131개 테스트 전부 통과하도록 수정해" |
| CORS 에러 | "CORS 미들웨어에 localhost:3000 추가됐는지 확인해" |
| SSG 빌드 너무 느림 | "ISR(revalidate: 86400)로 전환 검토해" |
| 웹-앱 결과 불일치 | "동일 API에 웹/앱 방식으로 호출해서 결과 비교해" |
| 컨텍스트 초과 | 새 세션에서 "CLAUDE.md와 STATUS_BOARD.md 읽고 이어서" |
| 에이전트 규칙 무시 | "AGENT.md 다시 읽고 권한 범위 확인해" |
