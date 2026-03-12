#!/usr/bin/env bash
# Review Agent — 일간 리포트 생성 스크립트
set -euo pipefail

PROJECT_DIR="${1:-.}"
REPORT_DIR="${PROJECT_DIR}/.agents/ops-squad/qa-monitor/reports"
DATE=$(date '+%Y%m%d')
REPORT_FILE="${REPORT_DIR}/REVIEW-DAILY-${DATE}.md"
SUMMARY_FILE="/tmp/daily-review-report.md"

mkdir -p "$REPORT_DIR"

# 리포트 헤더
cat > "$SUMMARY_FILE" << HEADER
# Review Agent 일간 리포트 — $(date '+%Y-%m-%d')

## 검사 결과 요약

HEADER

TOTAL_ERRORS=0
TOTAL_WARNINGS=0

# 보안 검사
echo "--- 보안 검사 실행 ---"
if bash "${PROJECT_DIR}/scripts/review/check-security.sh" "${PROJECT_DIR}/src/web" >> "$SUMMARY_FILE" 2>&1; then
    echo "### 보안: PASS" >> "$SUMMARY_FILE"
else
    echo "### 보안: FAIL" >> "$SUMMARY_FILE"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi
echo "" >> "$SUMMARY_FILE"

# SEO 검사
echo "--- SEO 검사 실행 ---"
if bash "${PROJECT_DIR}/scripts/review/check-seo.sh" "${PROJECT_DIR}/src/web" >> "$SUMMARY_FILE" 2>&1; then
    echo "### SEO: PASS" >> "$SUMMARY_FILE"
else
    echo "### SEO: FAIL" >> "$SUMMARY_FILE"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi
echo "" >> "$SUMMARY_FILE"

# 다크모드 검사
echo "--- 다크모드 검사 실행 ---"
bash "${PROJECT_DIR}/scripts/review/check-darkmode.sh" "${PROJECT_DIR}/src/web" >> "$SUMMARY_FILE" 2>&1 || true
echo "" >> "$SUMMARY_FILE"

# 프로덕션 헤더 검사
echo "--- 프로덕션 헤더 검사 실행 ---"
if bash "${PROJECT_DIR}/scripts/review/check-headers.sh" "https://pillright.com" >> "$SUMMARY_FILE" 2>&1; then
    echo "### 프로덕션 헤더: PASS" >> "$SUMMARY_FILE"
else
    echo "### 프로덕션 헤더: FAIL" >> "$SUMMARY_FILE"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi
echo "" >> "$SUMMARY_FILE"

# 복잡도 검사
echo "--- 복잡도 검사 실행 ---"
if [ -f "${PROJECT_DIR}/scripts/review/check-complexity.sh" ]; then
    if bash "${PROJECT_DIR}/scripts/review/check-complexity.sh" "${PROJECT_DIR}/src/backend" "${PROJECT_DIR}/src/web" >> "$SUMMARY_FILE" 2>&1; then
        echo "### 복잡도: PASS" >> "$SUMMARY_FILE"
    else
        echo "### 복잡도: FAIL" >> "$SUMMARY_FILE"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi
    echo "" >> "$SUMMARY_FILE"
fi

# 품질 점수
echo "--- 품질 점수 계산 ---"
if [ -f "${PROJECT_DIR}/scripts/review/check-quality.sh" ]; then
    bash "${PROJECT_DIR}/scripts/review/check-quality.sh" "${PROJECT_DIR}" --report >> "$SUMMARY_FILE" 2>&1 || true
    echo "" >> "$SUMMARY_FILE"
fi

# 테스트 파일 카운트
echo "--- 테스트 통계 ---"
WEB_TEST_COUNT=$(find "${PROJECT_DIR}/src/web/src" -name "*.test.*" 2>/dev/null | wc -l | xargs)
cat >> "$SUMMARY_FILE" << STATS

## 통계
| 항목 | 값 |
|------|-----|
| 웹 테스트 파일 수 | ${WEB_TEST_COUNT}개 |
| 총 오류 | ${TOTAL_ERRORS}건 |
| 총 경고 | ${TOTAL_WARNINGS}건 |
| 검사 시각 | $(date '+%Y-%m-%d %H:%M KST') |
STATS

# 리포트 저장
cp "$SUMMARY_FILE" "$REPORT_FILE"
echo ""
echo "리포트 생성 완료: $REPORT_FILE"

# CI에서 실패 여부 반환
exit $TOTAL_ERRORS
