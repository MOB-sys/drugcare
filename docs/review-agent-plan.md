# Review Agent 시스템 설계 문서

> 약먹어(PillRight) 프로젝트 자동화 코드 품질 관리 시스템
> 작성일: 2026-03-11

---

## 1. Review Agent 역할과 범위

### 1.1 목적

커밋, PR, 정기 스케줄 시점에 자동으로 보안/접근성/성능/SEO/다크모드/타입/테스트를 검증하여, 프로덕션 배포 전에 문제를 차단한다.

### 1.2 기존 에이전트와의 관계

| 기존 에이전트 | Review Agent 관계 |
|---|---|
| `reviewer` (dev-squad) | 수동 코드 리뷰 → Review Agent가 **자동화 레이어** 담당 |
| `qa-monitor` (ops-squad) | 배포 후 스모크 테스트 → Review Agent는 **배포 전** 검증 |
| `health-checker` (ops-squad) | 인프라 상태 → Review Agent는 **코드 품질** 전담 |

### 1.3 범위

```
┌─────────────────────────────────────────────────┐
│                  Review Agent                    │
│                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Pre-     │ │ CI/CD    │ │ Scheduled        │ │
│  │ commit   │ │ Pipeline │ │ Review           │ │
│  │ Hooks    │ │ (PR)     │ │ (Daily)          │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│                                                 │
│  검증 대상:                                      │
│  - src/web/     (Next.js)                       │
│  - src/backend/ (FastAPI) — lint/type만          │
│  - src/frontend/ (Flutter) — analyze만           │
│  - next.config.ts (CSP/헤더)                     │
│  - .github/workflows/                           │
└─────────────────────────────────────────────────┘
```

---

## 2. 자동 리뷰 체크리스트

### 2.1 보안 (Security)

| # | 체크 항목 | 검증 방법 | 트리거 |
|---|----------|----------|--------|
| S-1 | CSP 헤더 유효성 | `next.config.ts` 파싱 + 프로덕션 헤더 검증 | PR, Weekly |
| S-2 | 시크릿 키 하드코딩 | grep 패턴 (API_KEY, SECRET, PASSWORD, token) | Pre-commit |
| S-3 | `dangerouslySetInnerHTML` 사용 | grep 스캔 | Pre-commit, PR |
| S-4 | HTTPS 강제 (HSTS 헤더) | `next.config.ts` headers() 검증 | PR |
| S-5 | 의존성 취약점 | `npm audit --audit-level=high` | PR, Weekly |
| S-6 | `.env` 파일 커밋 방지 | `.gitignore` 검증 + pre-commit | Pre-commit |
| S-7 | X-Frame-Options DENY | 헤더 설정 검증 | PR |

**구현 — `scripts/review/check-security.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail

WEB_DIR="${1:-src/web}"
ERRORS=0

# S-2: 시크릿 키 하드코딩 검사
echo "=== S-2: 시크릿 키 스캔 ==="
PATTERNS='(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*["\x27][^"\x27]{8,}'
if grep -rniE "$PATTERNS" "$WEB_DIR/src/" --include="*.ts" --include="*.tsx" \
   | grep -v '.test.' | grep -v 'process.env' | grep -v '// ' | grep -v 'type '; then
    echo "❌ 하드코딩된 시크릿 발견"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ 통과"
fi

# S-3: dangerouslySetInnerHTML
echo "=== S-3: dangerouslySetInnerHTML ==="
DANGEROUS=$(grep -rn 'dangerouslySetInnerHTML' "$WEB_DIR/src/" --include="*.tsx" || true)
if [ -n "$DANGEROUS" ]; then
    echo "⚠️ dangerouslySetInnerHTML 사용 발견 (수동 검토 필요):"
    echo "$DANGEROUS"
fi

# S-5: npm audit
echo "=== S-5: 의존성 취약점 ==="
cd "$WEB_DIR"
if npm audit --audit-level=high 2>/dev/null; then
    echo "✅ 고위험 취약점 없음"
else
    echo "❌ 고위험 취약점 발견"
    ERRORS=$((ERRORS + 1))
fi

exit $ERRORS
```

### 2.2 접근성 (Accessibility)

| # | 체크 항목 | 검증 방법 | 트리거 |
|---|----------|----------|--------|
| A-1 | `img`에 `alt` 속성 | ESLint `jsx-a11y` 규칙 | Pre-commit |
| A-2 | 폼 요소에 `label` 연결 | ESLint `jsx-a11y` | Pre-commit |
| A-3 | skip-to-content 링크 | E2E 테스트 | PR |
| A-4 | 색상 대비 비율 (WCAG AA) | Lighthouse CI 접근성 점수 ≥ 90 | PR |
| A-5 | 키보드 탐색 가능 | E2E 포커스 테스트 | PR |
| A-6 | ARIA 속성 올바른 사용 | `axe-core` Playwright 통합 | Weekly |

**ESLint 접근성 플러그인 설정:**
```bash
cd src/web && npm install --save-dev eslint-plugin-jsx-a11y
```

`src/web/eslint.config.mjs`에 추가:
```js
import jsxA11y from 'eslint-plugin-jsx-a11y';

export default [
  // ... 기존 설정
  {
    plugins: { 'jsx-a11y': jsxA11y },
    rules: {
      'jsx-a11y/alt-text': 'error',
      'jsx-a11y/label-has-associated-control': 'error',
      'jsx-a11y/no-noninteractive-element-interactions': 'warn',
      'jsx-a11y/click-events-have-key-events': 'warn',
    },
  },
];
```

### 2.3 성능 (Performance)

| # | 체크 항목 | 기준 | 트리거 |
|---|----------|------|--------|
| P-1 | Lighthouse Performance 점수 | ≥ 90 | PR |
| P-2 | 번들 사이즈 회귀 | `@next/bundle-analyzer` 비교 | PR |
| P-3 | `"use client"` 남용 | SSG/SSR 가능 컴포넌트 감지 | PR |
| P-4 | 이미지 최적화 | `next/image` 사용 확인 | Pre-commit |
| P-5 | Core Web Vitals | LCP < 2.5s, CLS < 0.1, INP < 200ms | Weekly |

**Lighthouse CI 설정 (`src/web/lighthouserc.json`):**
```json
{
  "ci": {
    "collect": {
      "startServerCommand": "npm run start",
      "startServerReadyPattern": "ready on",
      "url": [
        "http://localhost:3000/",
        "http://localhost:3000/check",
        "http://localhost:3000/drugs"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:seo": ["error", { "minScore": 0.95 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }]
      }
    }
  }
}
```

### 2.4 SEO

| # | 체크 항목 | 검증 방법 | 트리거 |
|---|----------|----------|--------|
| SEO-1 | SSG 페이지에 `generateMetadata` 존재 | grep 스캔 | PR |
| SEO-2 | JSON-LD 구조화 데이터 유효 | Google 구조화 테스트 API | Weekly |
| SEO-3 | `sitemap.xml` URL 수 감소 방지 | 이전 배포 대비 비교 | PR |
| SEO-4 | `robots.txt` 올바름 | 내용 검증 | PR |
| SEO-5 | OG/Twitter 메타태그 | E2E 검증 | PR |

**구현 — `scripts/review/check-seo.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail
WEB_DIR="${1:-src/web}"
ERRORS=0

echo "=== SEO-1: generateMetadata 확인 ==="
for page_file in $(find "$WEB_DIR/src/app" -name "page.tsx" -path "*/\[*\]/*"); do
    if ! grep -q "generateMetadata\|metadata" "$page_file"; then
        echo "❌ $page_file — generateMetadata 없음"
        ERRORS=$((ERRORS + 1))
    fi
done

echo "검사 완료: $ERRORS개 오류"
exit $ERRORS
```

### 2.5 다크모드 일관성

| # | 체크 항목 | 검증 방법 | 트리거 |
|---|----------|----------|--------|
| DM-1 | 하드코딩 색상 없음 | `bg-white`, `text-black` 등 감지 | Pre-commit |
| DM-2 | `dark:` 프리픽스 매칭 | 직접 색상값에 `dark:` 대응 필요 | PR |
| DM-3 | 시각적 회귀 없음 | Playwright 다크모드 스크린샷 비교 | Weekly |

**구현 — `scripts/review/check-darkmode.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail
WEB_DIR="${1:-src/web}"
WARNINGS=0

echo "=== DM-1: 하드코딩 색상 감지 ==="
HARDCODED=$(grep -rn \
    -e 'bg-white' -e 'bg-black' -e 'text-white' -e 'text-black' \
    -e 'bg-gray-' -e 'text-gray-' -e 'border-gray-' \
    "$WEB_DIR/src/" --include="*.tsx" \
    | grep -v '.test.' \
    | grep -v 'dark:' \
    | grep -v '// review-ok' \
    || true)

if [ -n "$HARDCODED" ]; then
    echo "⚠️ CSS 변수 대신 하드코딩 색상 사용 (dark: 프리픽스 필요):"
    echo "$HARDCODED" | head -20
    WARNINGS=$((WARNINGS + 1))
fi

echo "경고 $WARNINGS건"
```

### 2.6 타입 안전성

| # | 체크 항목 | 검증 방법 | 트리거 |
|---|----------|----------|--------|
| T-1 | TypeScript strict 컴파일 | `npx tsc --noEmit` | Pre-commit, PR |
| T-2 | `any` 타입 사용 금지 | ESLint `@typescript-eslint/no-explicit-any` | Pre-commit |
| T-3 | API 응답 타입 일치 | `src/types/` 타입 vs 실제 응답 비교 | Weekly |

### 2.7 테스트 커버리지

| # | 체크 항목 | 기준 | 트리거 |
|---|----------|------|--------|
| TC-1 | Vitest 단위 테스트 통과 | 100% 통과 | Pre-commit, PR |
| TC-2 | 커버리지 하한 | ≥ 60% (web), ≥ 70% (backend) | PR |
| TC-3 | 새 컴포넌트에 테스트 존재 | `*.tsx` → `*.test.tsx` 매칭 | PR |
| TC-4 | E2E 테스트 통과 | Playwright 전체 통과 | PR (main 머지 전) |
| TC-5 | 테스트 파일 증감 모니터링 | 이전 대비 감소 시 경고 | PR |

---

## 3. 실행 트리거

### 3.1 트리거별 실행 범위

```
┌────────────────────────────────────────────────────────────┐
│                    트리거 → 검증 매핑                        │
├─────────────┬──────────────────────────────────────────────┤
│ Pre-commit  │ 빠른 검사만 (< 10초)                          │
│ (로컬)      │ S-2, S-3, S-6, A-1, A-2, P-4, DM-1,        │
│             │ T-1, T-2, TC-1                               │
├─────────────┼──────────────────────────────────────────────┤
│ PR CI       │ 전체 자동 검증 (< 10분)                       │
│ (GitHub     │ S-1~S-7, A-1~A-5, P-1~P-4, SEO-1~SEO-6,    │
│  Actions)   │ DM-1~DM-2, T-1~T-2, TC-1~TC-5              │
├─────────────┼──────────────────────────────────────────────┤
│ Daily       │ 심층 검증 (< 30분)                            │
│ (Scheduled) │ S-5, A-6, P-5, SEO-2, DM-3, T-3            │
│             │ + 프로덕션 헤더/CSP 실제 검증                  │
│             │ + 의존성 업데이트 알림                          │
└─────────────┴──────────────────────────────────────────────┘
```

### 3.2 스케줄

| 트리거 | 시점 | 환경 |
|--------|------|------|
| Pre-commit | 매 커밋 | 로컬 개발 머신 |
| PR CI | PR 생성/업데이트 + main push | GitHub Actions |
| Daily Review | 매일 09:00 KST | GitHub Actions (cron) |

---

## 4. CSP/헤더 프로덕션 환경 검증

### 4.1 문제 발생 패턴

1. **로컬 vs 프로덕션 불일치:** 로컬에서는 `localhost:8000` 직접 호출 → CORS/CSP 문제 없음. 프로덕션에서 `api.pillright.com` 크로스 오리진 → CSP 차단
2. **서드파티 추가 누락:** AdSense, GA4, Kakao SDK 등 새 서비스 추가 시 CSP 업데이트 누락
3. **connect-src 누락:** API URL 변경 시 CSP에 반영 안 됨

### 4.2 검증 스크립트

**`scripts/review/check-headers.sh`:**
```bash
#!/usr/bin/env bash
set -euo pipefail

TARGET_URL="${1:-https://pillright.com}"
ERRORS=0

echo "=== 프로덕션 보안 헤더 검증: $TARGET_URL ==="
HEADERS=$(curl -sI "$TARGET_URL" --max-time 15)

check_header() {
    local name="$1" expected="$2"
    local value=$(echo "$HEADERS" | grep -i "^${name}:" | head -1 | cut -d: -f2- | xargs)
    if [ -z "$value" ]; then
        echo "❌ $name — 누락"
        ERRORS=$((ERRORS + 1))
    elif echo "$value" | grep -qi "$expected"; then
        echo "✅ $name"
    else
        echo "⚠️ $name — 기대: $expected, 실제: $value"
        ERRORS=$((ERRORS + 1))
    fi
}

check_header "X-Frame-Options" "DENY"
check_header "X-Content-Type-Options" "nosniff"
check_header "Strict-Transport-Security" "max-age="
check_header "Content-Security-Policy" "default-src"
check_header "Referrer-Policy" "strict-origin"
check_header "Permissions-Policy" "camera=()"

# CSP 세부 검증
echo ""
echo "=== CSP 세부 검증 ==="
CSP=$(echo "$HEADERS" | grep -i "^content-security-policy:" | head -1 | cut -d: -f2-)

for directive in "default-src" "script-src" "style-src" "connect-src" "frame-src" "object-src 'none'"; do
    if echo "$CSP" | grep -q "$directive"; then
        echo "✅ CSP: $directive 존재"
    else
        echo "❌ CSP: $directive 누락"
        ERRORS=$((ERRORS + 1))
    fi
done

# connect-src에 API 도메인 포함 확인
if echo "$CSP" | grep -q "api.pillright.com"; then
    echo "✅ CSP connect-src: api.pillright.com 포함"
else
    echo "❌ CSP connect-src: api.pillright.com 누락"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "결과: $ERRORS개 오류"
exit $ERRORS
```

### 4.3 CSP 변경 시 자동 검증 흐름

```
next.config.ts 수정
    ↓
pre-commit: next.config.ts 변경 감지 → CSP 경고 표시
    ↓
PR CI: 빌드 후 로컬 서버에서 헤더 검증
    ↓
Weekly: 프로덕션 URL에서 실제 헤더 검증
```

---

## 5. GitHub Actions CI/CD 파이프라인 통합

### 5.1 현재 CI 구조

```
.github/workflows/ci.yml — 8개 job:
├── backend-lint
├── backend-test
├── flutter-analyze
├── flutter-test
├── flutter-build-android
├── flutter-build-ios
├── web-test (vitest run)
├── web-build
└── web-lighthouse (lhci autorun)
```

### 5.2 추가할 Review Agent Job

**`.github/workflows/ci.yml`에 추가:**

```yaml
  web-review:
    name: Web Review Agent
    runs-on: ubuntu-latest
    needs: [web-test]
    defaults:
      run:
        working-directory: src/web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: src/web/package-lock.json
      - run: npm ci

      # T-1: TypeScript strict 컴파일
      - name: TypeScript Check
        run: npx tsc --noEmit

      # S-5: 의존성 취약점
      - name: Security Audit
        run: npm audit --audit-level=high || true

      # S-2, S-3: 시크릿 + dangerouslySetInnerHTML
      - name: Security Scan
        run: bash ../../scripts/review/check-security.sh .

      # SEO 검증
      - name: SEO Check
        run: bash ../../scripts/review/check-seo.sh .

      # 다크모드 검증
      - name: Dark Mode Check
        run: bash ../../scripts/review/check-darkmode.sh .

      # 테스트 커버리지
      - name: Test Coverage
        run: npx vitest run --coverage --reporter=json

      # 테스트 파일 수 변화
      - name: Test Count Check
        run: |
          COUNT=$(find src -name "*.test.*" | wc -l)
          echo "현재 테스트 파일: ${COUNT}개"
```

### 5.3 일간 정기 리뷰 워크플로우

**`.github/workflows/daily-review.yml` (신규):**

```yaml
name: Daily Review Agent

on:
  schedule:
    - cron: '0 0 * * *'  # 매일 09:00 KST (UTC 00:00)
  workflow_dispatch:

jobs:
  production-review:
    name: Production Review
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: src/web/package-lock.json

      - name: Install Dependencies
        run: cd src/web && npm ci

      # 프로덕션 헤더/CSP 검증
      - name: Production Headers Check
        run: bash scripts/review/check-headers.sh https://pillright.com

      # 의존성 업데이트 확인
      - name: Outdated Dependencies
        run: |
          cd src/web
          echo "## 업데이트 가능 패키지"
          npm outdated --json 2>/dev/null | head -50 || echo "모두 최신"

      # Lighthouse CI (프로덕션)
      - name: Lighthouse Production
        run: |
          npm install -g @lhci/cli
          lhci autorun --collect.url=https://pillright.com/ \
                        --collect.url=https://pillright.com/check \
                        --collect.numberOfRuns=3 \
                        --assert.assertions.categories:performance="error;minScore=0.85" \
                        --assert.assertions.categories:accessibility="error;minScore=0.9" \
                        --assert.assertions.categories:seo="error;minScore=0.95"

      # 실패 시 GitHub Issue 자동 생성
      - name: Create Issue on Failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `[Review Agent] 일간 리뷰 실패 - ${new Date().toISOString().split('T')[0]}`,
              body: '일간 자동 리뷰에서 문제가 발견되었습니다. Actions 로그를 확인하세요.',
              labels: ['review-agent', 'quality']
            });
```

---

## 6. Pre-commit Hooks 설정

### 6.1 설치

```bash
cd /Users/lastdance/Desktop/workspace/drugcare
npm install --save-dev husky lint-staged
npx husky init
cd src/web && npm install --save-dev lint-staged
```

### 6.2 Husky pre-commit hook

**`.husky/pre-commit`:**
```bash
#!/usr/bin/env sh

# Web (Next.js) 변경 감지
WEB_CHANGED=$(git diff --cached --name-only -- 'src/web/' | head -1)
if [ -n "$WEB_CHANGED" ]; then
    echo "🔍 [Review Agent] 웹 코드 검증 중..."
    cd src/web
    npx lint-staged
    npx tsc --noEmit
    cd ../..
fi

# Backend (FastAPI) 변경 감지
BACKEND_CHANGED=$(git diff --cached --name-only -- 'src/backend/' | head -1)
if [ -n "$BACKEND_CHANGED" ]; then
    echo "🔍 [Review Agent] 백엔드 코드 검증 중..."
    cd src/backend
    ruff check . || exit 1
    ruff format --check . || exit 1
    cd ../..
fi

# 시크릿 키 스캔 (전체)
echo "🔍 [Review Agent] 시크릿 키 스캔..."
SECRETS=$(git diff --cached --diff-filter=ACM -U0 \
  | grep -iE '(api[_-]?key|secret|password|token)\s*[:=]\s*["\x27][A-Za-z0-9+/]{16,}' \
  | grep -v 'process\.env' | grep -v 'NEXT_PUBLIC_' || true)
if [ -n "$SECRETS" ]; then
    echo "❌ 시크릿 키 하드코딩 의심:"
    echo "$SECRETS"
    exit 1
fi

# next.config.ts 변경 시 CSP 경고
CONFIG_CHANGED=$(git diff --cached --name-only -- 'src/web/next.config.ts' | head -1)
if [ -n "$CONFIG_CHANGED" ]; then
    echo "⚠️ [Review Agent] next.config.ts 변경됨 — CSP/헤더 검토 필요"
    echo "    배포 후 scripts/review/check-headers.sh 실행 권장"
fi
```

### 6.3 lint-staged 설정

**`src/web/package.json`에 추가:**
```json
{
  "lint-staged": {
    "src/**/*.{ts,tsx}": [
      "eslint --fix --max-warnings 0",
      "prettier --write"
    ]
  }
}
```

---

## 7. 리뷰 결과 리포트 형식

### 7.1 PR 코멘트 형식

```markdown
## 🔍 Review Agent 결과

**커밋:** abc1234
**판정:** ✅ 통과 / ❌ 실패 / ⚠️ 경고

### 보안
| 항목 | 결과 | 상세 |
|------|------|------|
| 시크릿 키 | ✅ | 하드코딩 없음 |
| CSP 설정 | ✅ | 7개 디렉티브 정상 |
| npm audit | ⚠️ | moderate 2건 (high 없음) |

### 접근성
| 항목 | 결과 | 상세 |
|------|------|------|
| Lighthouse | ✅ | 92점 |

### 성능
| 항목 | 결과 | 상세 |
|------|------|------|
| Lighthouse | ✅ | 94점 |
| 번들 사이즈 | ✅ | +2.3KB (허용) |

### 테스트
| 항목 | 결과 | 상세 |
|------|------|------|
| Vitest | ✅ | 114/114 통과 |
| 커버리지 | ✅ | 63% |
```

### 7.2 주간 리포트 형식

**저장 위치:** `.agents/ops-squad/qa-monitor/reports/REVIEW-WEEKLY-{YYYYMMDD}.md`

```markdown
# 📊 주간 코드 품질 리뷰 — {날짜}

## 요약
- **전체 판정:** ✅ 양호
- **검사 항목:** 28개 (통과 25 / 경고 3 / 실패 0)

## 프로덕션 환경
| 항목 | 상태 | 값 |
|------|------|-----|
| CSP 헤더 | ✅ | 7 디렉티브 정상 |
| HSTS | ✅ | max-age=31536000 |
| Lighthouse Performance | ✅ | 93 |
| Lighthouse Accessibility | ✅ | 91 |
| Lighthouse SEO | ✅ | 97 |

## 트렌드
| 지표 | 2주 전 | 1주 전 | 이번 주 |
|------|--------|--------|--------|
| 테스트 수 | 110 | 112 | 114 |
| 커버리지 | 58% | 61% | 63% |
| Lighthouse Perf | 91 | 92 | 93 |
| 번들 크기 | 245KB | 248KB | 247KB |
```

---

## 8. 단계별 구현 로드맵

### Phase 1: 기반 구축 (1~2일)

| 작업 | 파일 | 소요 |
|------|------|------|
| `scripts/review/` 디렉토리 생성 | `scripts/review/` | 10분 |
| check-security.sh 작성 | `scripts/review/check-security.sh` | 30분 |
| check-seo.sh 작성 | `scripts/review/check-seo.sh` | 30분 |
| check-darkmode.sh 작성 | `scripts/review/check-darkmode.sh` | 30분 |
| check-headers.sh 작성 | `scripts/review/check-headers.sh` | 30분 |
| Husky + lint-staged 설치 | 루트 package.json, `.husky/` | 30분 |
| pre-commit hook 작성 | `.husky/pre-commit` | 30분 |

### Phase 2: CI 통합 (1~2일)

| 작업 | 파일 | 소요 |
|------|------|------|
| ci.yml에 web-review job 추가 | `.github/workflows/ci.yml` | 1시간 |
| lighthouserc.json 생성 | `src/web/lighthouserc.json` | 30분 |
| ESLint jsx-a11y 플러그인 추가 | `src/web/eslint.config.mjs` | 30분 |
| PR 코멘트 자동 게시 step 추가 | ci.yml | 1시간 |

### Phase 3: 일간 리뷰 (1일)

| 작업 | 파일 | 소요 |
|------|------|------|
| daily-review.yml 생성 | `.github/workflows/daily-review.yml` | 1시간 |
| generate-daily-report.sh 작성 | `scripts/review/generate-daily-report.sh` | 1시간 |
| 실패 시 GitHub Issue 자동 생성 | daily-review.yml | 30분 |

### Phase 4: 고도화 (1~2일, 선택)

| 작업 | 파일 | 소요 |
|------|------|------|
| axe-core Playwright 통합 | `e2e/accessibility-axe.spec.ts` | 1시간 |
| 번들 사이즈 비교 자동화 | ci.yml | 1시간 |
| 다크모드 스크린샷 비교 | `e2e/dark-mode-visual.spec.ts` | 2시간 |
| Slack/Discord 웹훅 알림 | weekly-review.yml | 30분 |

### 전체 일정

```
Day 1: Phase 1 — 스크립트 + pre-commit hook
Day 2: Phase 2 — CI 통합
Day 3: Phase 3 — 일간 리뷰
Day 4: Phase 4 — 고도화 (선택)
```

---

## 파일 구조 요약

```
drugcare/
├── .husky/
│   └── pre-commit                    # (신규)
├── .github/workflows/
│   ├── ci.yml                        # (수정) web-review job 추가
│   └── daily-review.yml              # (신규)
├── scripts/review/                   # (신규)
│   ├── check-security.sh
│   ├── check-seo.sh
│   ├── check-darkmode.sh
│   ├── check-headers.sh
│   └── generate-daily-report.sh
├── src/web/
│   ├── lighthouserc.json             # (신규)
│   └── package.json                  # (수정) lint-staged 추가
└── docs/
    └── review-agent-plan.md          # 이 문서
```
