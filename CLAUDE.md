# 🏥 약먹어 (YakMeogeo) — AI Agent Team Operating Manual

> **이 파일은 Claude Code가 세션 시작 시 가장 먼저 읽는 "회사 매뉴얼"입니다.**
> 모든 에이전트의 행동 기준이 됩니다.

---

## 프로젝트 개요

- **서비스명:** 약먹어 (YakMeogeo / 久藥師)
- **프로젝트 코드명:** yakmeogeo
- **한줄 설명:** "이 약이랑 이 영양제, 같이 먹어도 돼?" — 3초 만에 확인하는 복약 안전 체커
- **수익 모델:** 100% 광고 수익 (웹: AdSense / 앱: AdMob + 네이버 광고)
- **대상 사용자:** 다제 복용자(40~60대), 영양제 헤비유저(20~40대), 부모님 약 관리자(30~50대)

---

## ⚠️ 듀얼 플랫폼 전략 (핵심)

```
                    FastAPI 백엔드 (기존 — 100% 유지)
                 15 API / 7 테이블 / 209 테스트 / Redis
                     ↕              ↕              ↕
              PC 브라우저      모바일 브라우저    네이티브 앱
              (Next.js)       (Next.js 반응형)   (Flutter)
                 │                  │                │
              AdSense            AdSense           AdMob
              SEO 검색 유입      즉석 체크         푸시 리마인더
              약물 상세 SSG     진입장벽 제로      복약함 관리
                                                   카메라 약 식별
```

### 역할 분담
- **Next.js 웹 (신규)** = 신규 유입 엔진 → "비타민D 오메가3 같이" 검색 → 웹 유입 → AdSense 수익
- **Flutter 앱 (기존)** = 리텐션 엔진 → 푸시 리마인더 → 매일 앱 진입 → AdMob 수익
- **웹 → 앱 전환:** 웹에서 상호작용 체크 후 "매일 복약 리마인더 받으려면 앱 설치" 유도

### 플랫폼별 기능 매트릭스
| 기능 | 웹 (Next.js) | 앱 (Flutter) |
|------|:-----------:|:----------:|
| 상호작용 체크 | ✅ 핵심 | ✅ 핵심 |
| 약물/영양제 상세 정보 | ✅ SSG | ✅ |
| 복약함 관리 | ✅ 쿠키/localStorage | ✅ SharedPreferences |
| 복약 리마인더 | ❌ | ✅ 푸시 알림 |
| 약 사진 식별 | ❌ | ✅ 카메라 (Phase 2) |
| SEO 검색 유입 | ✅ 핵심 | ❌ |
| 광고 | AdSense | AdMob |
| 앱 설치 유도 | ✅ 스마트 배너 | N/A |

---

## 기술 스택

### 기존 (Sprint 6 완료 — 변경 최소화)

| 영역 | 기술 | 상태 |
|------|------|------|
| **백엔드 API** | FastAPI (Python 3.11+) + SQLAlchemy 2.0 async + Pydantic 2 | ✅ 15 API, 209 테스트 |
| **데이터베이스** | PostgreSQL 16 + Redis 7 | ✅ 7 테이블, 캐시 완비 |
| **모바일 앱** | Flutter 3.35+ (Riverpod + Go Router + Dio) | ✅ 9 화면, 131 테스트 |
| **데이터 파이프라인** | 식약처 3종 API 수집기 + 파서 + 검증기 | ✅ 완비 |
| **AI** | OpenAI GPT-4o (AsyncOpenAI, Semaphore 3) | ✅ 캐시 30일 |
| **인프라** | Docker + Nginx SSL + GitHub Actions CI/CD | ✅ 프로덕션 구성 |
| **인증** | 디바이스 UUID (X-Device-ID 헤더) | ✅ 회원가입 없음 |

### 신규 (추가 개발)

| 영역 | 기술 | 사유 |
|------|------|------|
| **웹 프론트엔드** | Next.js 15 (App Router) + TypeScript | SSR/SSG → SEO |
| **웹 스타일링** | Tailwind CSS 4 | 반응형, 유틸리티 퍼스트 |
| **웹 광고** | Google AdSense | 웹 트래픽 수익화 |
| **SEO 분석** | Google Analytics 4 + Search Console + 네이버 서치어드바이저 | 검색 성과 추적 |
| **웹 배포** | Vercel | Next.js 최적 호스팅 |

---

## 기존 백엔드 자산 참조 (신규 개발 시 필수)

### DB 스키마 (7개 — 변경 금지, 추가만 허용)
| 테이블 | 핵심 컬럼 | 용도 |
|--------|----------|------|
| `drugs` | item_seq, item_name, ingredients(JSONB) | 의약품 마스터 |
| `supplements` | product_name, ingredients(JSONB) | 영양제 마스터 |
| `interactions` | item_a/b, severity, description, source | 상호작용 |
| `user_cabinets` | device_id, item_type, item_id | 복약함 |
| `reminders` | device_id, reminder_time, days_of_week | 리마인더 |
| `feedbacks` | device_id, category, content | 피드백 |
| `app_metrics` | device_id, event_type, event_data | 메트릭스 |

### 기존 API (15개 — 웹에서 동일하게 호출)
| 그룹 | Path | 웹 활용 |
|------|------|---------|
| Drugs | `GET /api/v1/drugs/search` | 약물 검색 |
| Drugs | `GET /api/v1/drugs/{id}` | 약물 상세 (SSG) |
| Supplements | `GET /api/v1/supplements/search` | 영양제 검색 |
| Supplements | `GET /api/v1/supplements/{id}` | 영양제 상세 (SSG) |
| Interactions | `POST /api/v1/interactions/check` | **핵심** 상호작용 체크 |
| Cabinet | `POST/GET/DELETE /api/v1/cabinet` | 복약함 |
| Reminders | CRUD `/api/v1/reminders` | ❌ 앱 전용 |
| Feedback | `POST /api/v1/feedback` | 피드백 |
| Metrics | `POST /api/v1/metrics/event` | 이벤트 |

### 백엔드 최소 변경 사항
| 항목 | 변경 |
|------|------|
| CORS | 웹 도메인 추가 (yakmeogeo.com, localhost:3000) |
| DeviceAuth | 웹 세션쿠키 분기 (X-Device-ID 없으면 쿠키 session_id 확인) |
| Nginx | Next.js 프록시 룰 추가 |
| DB | drugs/supplements에 `slug` 컬럼 추가 (마이그레이션 v003) |
| 신규 API | slug 조회 4개 + count 2개 = 6개 엔드포인트 추가 |

### Redis 캐시 TTL (웹도 동일 활용)
| 대상 | TTL |
|------|-----|
| 검색 결과 | 24시간 |
| 약물/영양제 상세 | 3일 |
| 상호작용 체크 | 7일 |
| AI 설명 | 30일 |

---

## Next.js 렌더링 전략 (SEO 핵심)

| 페이지 | 렌더링 | 이유 |
|--------|--------|------|
| `/drugs/[slug]` | **SSG** (1만개+) | 검색 인덱싱 핵심 |
| `/supplements/[slug]` | **SSG** (500개+) | 검색 인덱싱 |
| `/check` | **CSR** | 동적 입력 |
| `/check/result` | **SSR** | OG 이미지 동적 생성, 공유 가능 |
| `/cabinet` | **CSR** | localStorage, SEO 불필요 |
| `/tips/[slug]` | **SSG** | 건강팁 콘텐츠 |
| `/` | **SSG + ISR** | 메인 랜딩 |

---

## 에이전트 시스템 규약

### 파일 접근
- 각 에이전트는 AGENT.md 정의 권한 범위만 수정
- `.agents/shared/` 는 모든 에이전트 읽기/쓰기
- **기존 백엔드/Flutter 코드 수정 시 PM 승인 필수**

### 작업 흐름
1. STATUS_BOARD.md 등록 → 작업 시작
2. 완료 → outbox 보고
3. 에러 → ERROR_LOG.md
4. 설계 변경 → DECISIONS_LOG.md
5. **약물 데이터 변경 → 데이터 검증 필수**

### 코드 스타일
- **Python:** snake_case, PascalCase 클래스, docstring
- **Dart:** camelCase, PascalCase 클래스
- **TypeScript:** camelCase, PascalCase 컴포넌트, JSDoc
- 한 함수 50줄 이하

### 커밋 규칙
`feat:` `fix:` `data:` `seo:` `web:` `app:` `api:` `ad:` `docs:` `test:`

### 금지 사항
- 🚫 시크릿 키 하드코딩
- 🚫 타 에이전트 영역 무단 수정
- 🚫 테스트 없이 완료 처리
- 🚫 약물 데이터 임의 생성 (공공데이터 기반 필수)
- 🚫 의학적 진단/치료 문구 사용 (면책조항 필수)
- 🚫 기존 API 응답 구조 일방 변경 (앱 호환 유지)

### 필수 법적 요건
- 모든 결과 화면: "의사/약사의 전문적 판단을 대체하지 않습니다"
- 건강정보 = 민감정보 → 개인정보보호법 준수
- 복용 정보 디바이스 우선 저장
- 건강기능식품 광고 규제 (질병 치료 효능 금지)

---

## KPI 목표

| 지표 | 3개월 | 6개월 | 12개월 | 24개월 |
|------|-------|-------|--------|--------|
| MAU | 3,000 | 15,000 | 80,000 | 500,000 |
| DAU | 500 | 3,000 | 15,000 | 100,000 |
| 검색 유입 | 20% | 35% | 45% | 50%+ |
| 인덱싱 페이지 | 500 | 2,000 | 10,000+ | 15,000+ |
| 월 광고수익 | 7만 | 45만 | 300만 | 2,000만+ |
| D7 리텐션(앱) | 25% | 35% | 40% | 45%+ |
| 웹→앱 전환 | — | 5% | 8% | 10% |
