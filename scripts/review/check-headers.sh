#!/usr/bin/env bash
# Review Agent — 프로덕션 보안 헤더/CSP 검증 스크립트
set -euo pipefail

TARGET_URL="${1:-https://pillright.com}"
ERRORS=0
WARNINGS=0

echo "=========================================="
echo "  Production Headers Check: $TARGET_URL"
echo "=========================================="

# 헤더 가져오기
HEADERS=$(curl -sI "$TARGET_URL" --max-time 15 2>/dev/null || true)
if [ -z "$HEADERS" ]; then
    echo "FAIL: $TARGET_URL 에 접속할 수 없습니다"
    exit 1
fi

check_header() {
    local name="$1"
    local expected="$2"
    local value
    value=$(echo "$HEADERS" | grep -i "^${name}:" | head -1 | sed "s/^[^:]*: *//" | tr -d '\r')

    if [ -z "$value" ]; then
        echo "FAIL: $name — 누락"
        ERRORS=$((ERRORS + 1))
    elif echo "$value" | grep -qi "$expected"; then
        echo "PASS: $name"
    else
        echo "WARN: $name — 기대값 불일치"
        echo "       기대: $expected"
        echo "       실제: $value"
        WARNINGS=$((WARNINGS + 1))
    fi
}

echo ""
echo "--- 보안 헤더 ---"
check_header "X-Frame-Options" "DENY"
check_header "X-Content-Type-Options" "nosniff"
check_header "Strict-Transport-Security" "max-age="
check_header "Referrer-Policy" "strict-origin"
check_header "Permissions-Policy" "camera=()"
check_header "X-DNS-Prefetch-Control" "off"

# CSP 세부 검증
echo ""
echo "--- CSP 디렉티브 검증 ---"
CSP=$(echo "$HEADERS" | grep -i "^content-security-policy:" | head -1 | sed "s/^[^:]*: *//" | tr -d '\r')

if [ -z "$CSP" ]; then
    echo "FAIL: Content-Security-Policy 헤더 없음"
    ERRORS=$((ERRORS + 1))
else
    for directive in "default-src" "script-src" "style-src" "img-src" "connect-src" "frame-src" "object-src"; do
        if echo "$CSP" | grep -q "$directive"; then
            echo "PASS: CSP $directive"
        else
            echo "FAIL: CSP $directive 누락"
            ERRORS=$((ERRORS + 1))
        fi
    done

    # connect-src에 API 도메인 포함 확인
    echo ""
    echo "--- CSP connect-src API 도메인 ---"
    if echo "$CSP" | grep -q "api.pillright.com"; then
        echo "PASS: api.pillright.com 포함"
    else
        echo "FAIL: api.pillright.com 누락 (검색 차단 위험)"
        ERRORS=$((ERRORS + 1))
    fi

    # connect-src에 Sentry 포함 확인
    if echo "$CSP" | grep -q "sentry.io"; then
        echo "PASS: sentry.io 포함"
    else
        echo "WARN: sentry.io 누락 (에러 추적 차단 가능)"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

echo ""
echo "=========================================="
echo "  결과: 오류 ${ERRORS}건, 경고 ${WARNINGS}건"
echo "=========================================="
exit $ERRORS
