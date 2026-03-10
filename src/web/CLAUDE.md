# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

약잘알 (PillRight) — 약/영양제 상호작용 3초 체커. Next.js 15 웹 프론트엔드.
FastAPI 백엔드(`src/backend/`)의 API를 호출하는 클라이언트 앱이며, Vercel에 배포된다.

## Commands

```bash
npm run dev          # 로컬 개발 서버 (localhost:3000)
npm run build        # 프로덕션 빌드 (SSG 25,000+ 페이지 생성, ~15분)
npm run lint         # ESLint
npx tsc --noEmit     # TypeScript 타입 체크
npm run test         # Vitest 단위 테스트 (watch 모드)
npm run test:run     # Vitest 단일 실행 (CI용)
npm run test:e2e     # Playwright E2E 테스트
vercel --prod        # Vercel 프로덕션 배포 (git push 불필요)
```

단일 테스트 실행:
```bash
npx vitest run src/lib/utils/retry.test.ts     # 특정 단위 테스트
npx playwright test e2e/seo.spec.ts            # 특정 E2E 테스트
```

## Architecture

### 렌더링 전략
- **SSG** (`generateStaticParams`): `/drugs/[slug]` (1만+), `/supplements/[slug]` (500+), `/ingredients/[slug]` (20), `/categories/[slug]` (12), `/tips/[slug]`, `/professional/drugs/[slug]`
- **SSR**: `/check/result` (동적 OG 이미지), `/drugs/browse/[letter]`
- **CSR** (`"use client"`): `/check`, `/cabinet`, `/drugs`, `/supplements`, `/symptoms`, `/drugs/side-effects`, `/drugs/conditions`, `/drugs/identify`
- **ISR** (24h): `/` (홈), `/news`

### API 레이어
`src/lib/api/client.ts`의 `fetchApi<T>()` — 모든 백엔드 호출의 단일 진입점.
- 백엔드 URL: `NEXT_PUBLIC_API_URL` (기본 `http://localhost:8000`)
- `next.config.ts`에서 `/api/*` → 백엔드로 rewrite (CORS 우회)
- 응답 형식: `{ success, data, error, meta: { timestamp } }`
- 클라이언트 rate limit: 엔드포인트 그룹별 10초/30회
- 재시도: `withRetry()` 래퍼 (지수 백오프)

### 정적 데이터
`src/lib/data/` — SSG 페이지에 사용되는 정적 콘텐츠:
- `tips.ts` — 건강팁 (17개)
- `ingredients.ts` — 성분 가이드 (20개)
- `drugCategories.ts` — 약물 분류 (12개)
- `commonSideEffects.ts`, `conditions.ts`, `symptoms.ts`, `foodKeywords.ts` — 검색 키워드

### 인증
회원가입 없이 디바이스 UUID 기반. 웹에서는 세션 쿠키(`credentials: "include"`).

### 스타일링
Tailwind CSS 4 + CSS 변수 (`--color-primary`, `--color-text`, `--color-surface` 등).
다크모드: `<html>` 요소의 `dark` 클래스 토글 → `dark:` 프리픽스로 스타일 분기.
색상 변수는 `src/app/globals.css`에서 정의.

### 경로 별칭
`@/*` → `./src/*` (tsconfig.json)

## Key Patterns

### 페이지 작성 시
- SSG 페이지는 `generateStaticParams` + `generateMetadata` 필수
- 모든 상세 페이지에 JSON-LD 구조화 데이터 포함 (SEO)
- `Breadcrumbs` 컴포넌트를 모든 페이지 상단에 배치
- 면책조항 필수: "의사/약사의 전문적 판단을 대체하지 않습니다"

### API 함수 추가 시
- `src/lib/api/`에 도메인별 파일 (drugs.ts, supplements.ts, interactions.ts 등)
- `fetchApi<T>` 사용, 타입은 `src/types/`에 정의
- 서버 컴포넌트에서 직접 호출 가능 (rewrite 경유)

### 컴포넌트 규칙
- `"use client"` 는 상태/이벤트가 필요한 컴포넌트에만 명시
- 공통: `src/components/common/`, 기능별: `src/components/{feature}/`
- label과 keyword가 있는 데이터에서 두 값은 반드시 일치시킬 것 (사용자 혼란 방지)

## External Services

| 서비스 | 환경변수 | 용도 |
|--------|---------|------|
| 백엔드 API | `NEXT_PUBLIC_API_URL` | FastAPI 서버 |
| Google Analytics | `NEXT_PUBLIC_GA_ID` | 트래픽 분석 |
| Google AdSense | `NEXT_PUBLIC_ADSENSE_ID` | 광고 수익 |
| Sentry | `NEXT_PUBLIC_SENTRY_DSN`, `SENTRY_AUTH_TOKEN` | 에러 추적 |
| Kakao SDK | `NEXT_PUBLIC_KAKAO_JS_KEY` | 카카오톡 공유 |
| reCAPTCHA | `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` | 폼 스팸 방지 |

## Testing

- **단위 테스트**: Vitest + Testing Library, `src/**/*.test.{ts,tsx}`
- **E2E**: Playwright, `e2e/*.spec.ts`, Chromium + iPhone 14 프로젝트
- E2E는 `localhost:3000` 개발 서버 자동 시작

## Deployment

Vercel (Seoul `icn1` 리전). `vercel --prod`로 직접 배포.
Sentry sourcemap 업로드는 `SENTRY_AUTH_TOKEN` 설정 시에만 활성화.
