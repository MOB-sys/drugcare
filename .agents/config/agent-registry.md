# 🤖 Agent Registry — 약먹어 에이전트 등록부

> 듀얼 플랫폼 (Next.js 웹 + Flutter 앱) 전략에 최적화된 에이전트 구성

---

## Dev Squad (개발팀 — 9명)

| 에이전트 | 역할 | 파일 접근 권한 | 우선순위 |
|---------|------|--------------|---------|
| **PM** | 작업 분배, 진행 관리, 품질 게이트키핑 | 전체 읽기, shared/ + inbox 쓰기 | P0 |
| **Architect** | 시스템 설계, API 명세, DB 스키마, 웹-앱-백 통합 설계 | docs/, shared/ 쓰기 | P0 |
| **Data Engineer** | 약물 데이터 수집, 파싱, 검증, 상호작용 엔진 | src/backend/data/, scripts/data/ | P0 |
| **Backend** | FastAPI API 구현, DB 연동, 미들웨어 | src/backend/ | P1 |
| **Web Frontend** | Next.js 웹 UI, SSG/SSR, 반응형 | src/web/ | P1 |
| **App Frontend** | Flutter 앱 UI, 앱 빌드, 네이티브 기능 | src/frontend/ | P1 |
| **SEO Engineer** | 메타태그, 구조화 데이터, sitemap, Core Web Vitals | src/web/ (SEO 관련), tests/web/seo/ | P1 |
| **Reviewer** | 코드 리뷰, 보안 감사, API 호환성 검증 | 전체 읽기, shared/ 쓰기 | P2 |
| **Tester** | 테스트 작성/실행, 크로스 플랫폼 검증 | tests/, src/ 읽기 | P2 |

## Ops Squad (운영팀 — 3명)

| 에이전트 | 역할 | 실행 주기 | 알림 조건 |
|---------|------|---------|---------|
| **QA Monitor** | 웹+API E2E 스모크 테스트, SEO 인덱싱 확인 | 6시간마다 | 테스트 실패, 인덱싱 이상 |
| **Health Checker** | API + 웹 응답 시간, SSL, Docker 상태 | 30분마다 | 서비스 다운, 응답 지연 |
| **Reporter** | 일일 운영 보고서 (트래픽, 광고수익, SEO 지표) | 매일 09:00 | 항상 |

---

## 에이전트 간 핵심 의존성

```
CEO 지시
  │
  ├── PM → 작업 분배 → STATUS_BOARD 관리
  │     │
  │     ├── Architect → ARCHITECTURE.md, API_CONTRACT.md 작성
  │     │     │
  │     │     ├── Backend → FastAPI API 구현 (기존 + slug API 추가)
  │     │     │     ↕ API_CONTRACT.md 계약 기준
  │     │     ├── Web Frontend → Next.js 페이지 구현 (SSG/SSR/CSR)
  │     │     │     ↕ SEO Engineer 메타태그/구조화 데이터 삽입
  │     │     └── App Frontend → Flutter 빌드 생성 + 앱 설치 유도 기능
  │     │
  │     ├── Data Engineer → 약물 데이터 수집/검증 (독립 작업 가능)
  │     │
  │     ├── SEO Engineer → 메타태그, sitemap, JSON-LD 구현
  │     │     └── Web Frontend의 SSG 페이지에 SEO 레이어 삽입
  │     │
  │     ├── Reviewer → 코드 리뷰 (API 호환성 = 웹-앱 동시 확인)
  │     │
  │     └── Tester → 테스트 작성/실행
  │
  └── Ops Squad → 배포 후 모니터링
        ├── QA Monitor → 웹+API 스모크 테스트
        ├── Health Checker → 인프라 상태
        └── Reporter → 일일 종합 보고
```

---

## 크로스 플랫폼 규칙

### API 호환성 (가장 중요)
1. 기존 API 응답 구조 변경 시: **Web Frontend + App Frontend 둘 다 영향 분석 필수**
2. 신규 API 추가 시: API_CONTRACT.md에 웹/앱 사용 여부 명시
3. 인증 변경 시: X-Device-ID (앱) + 세션쿠키 (웹) 둘 다 테스트

### 디자인 일관성
- 신호등 시스템 (danger/warning/caution/info/safe) 웹-앱 동일
- 브랜드 색상 #00BFA5 (민트/청록) 동일
- 면책조항 배너 웹-앱 동일 위치 (결과 상단)
