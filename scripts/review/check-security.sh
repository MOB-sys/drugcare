#!/usr/bin/env bash
# Review Agent — 보안 검사 스크립트
set -euo pipefail

WEB_DIR="${1:-src/web}"
ERRORS=0
WARNINGS=0

echo "=========================================="
echo "  Security Check"
echo "=========================================="

# S-2: 시크릿 키 하드코딩 검사
echo ""
echo "--- S-2: 시크릿 키 하드코딩 스캔 ---"
PATTERNS='(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*["'"'"'][^"'"'"']{8,}'
FOUND=$(grep -rniE "$PATTERNS" "$WEB_DIR/src/" --include="*.ts" --include="*.tsx" \
  | grep -v '\.test\.' \
  | grep -v 'process\.env' \
  | grep -v '// ' \
  | grep -v 'type ' \
  | grep -v 'interface ' \
  | grep -v 'ApiError' \
  || true)

if [ -n "$FOUND" ]; then
    echo "FAIL: 하드코딩된 시크릿 의심"
    echo "$FOUND"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS"
fi

# S-3: dangerouslySetInnerHTML
echo ""
echo "--- S-3: dangerouslySetInnerHTML 사용 ---"
DANGEROUS=$(grep -rn 'dangerouslySetInnerHTML' "$WEB_DIR/src/" --include="*.tsx" --include="*.ts" \
  | grep -v '\.test\.' || true)
if [ -n "$DANGEROUS" ]; then
    echo "WARN: dangerouslySetInnerHTML 사용 발견 (수동 검토 필요):"
    echo "$DANGEROUS"
    WARNINGS=$((WARNINGS + 1))
else
    echo "PASS"
fi

# S-6: .env 파일 스테이징 방지
echo ""
echo "--- S-6: .env 파일 커밋 방지 ---"
STAGED_ENV=$(git diff --cached --name-only 2>/dev/null | grep '\.env' || true)
if [ -n "$STAGED_ENV" ]; then
    echo "FAIL: .env 파일이 스테이징됨:"
    echo "$STAGED_ENV"
    ERRORS=$((ERRORS + 1))
else
    echo "PASS"
fi

# S-5: npm audit (CI 환경에서만)
if [ "${CI:-}" = "true" ]; then
    echo ""
    echo "--- S-5: npm audit ---"
    cd "$WEB_DIR"
    if npm audit --audit-level=critical 2>/dev/null; then
        echo "PASS: critical 취약점 없음"
    else
        echo "FAIL: critical 취약점 발견"
        ERRORS=$((ERRORS + 1))
    fi
    if ! npm audit --audit-level=high 2>/dev/null; then
        echo "WARN: high 취약점 발견 (상세 확인 필요)"
        WARNINGS=$((WARNINGS + 1))
    fi
    cd - > /dev/null
fi

echo ""
echo "=========================================="
echo "  결과: 오류 ${ERRORS}건, 경고 ${WARNINGS}건"
echo "=========================================="
exit $ERRORS
