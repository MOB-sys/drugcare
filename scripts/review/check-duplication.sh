#!/usr/bin/env bash
# ============================================================================
# Review Agent — 코드 중복 탐지
# Python/TypeScript 소스에서 중복 코드 블록 감지
#
# 사용법:
#   ./check-duplication.sh [backend_dir] [web_dir]
# ============================================================================
set -euo pipefail

BACKEND_DIR="${1:-src/backend}"
WEB_DIR="${2:-src/web}"
ERRORS=0
WARNINGS=0

# 임계값
MIN_DUP_LINES=10         # 중복으로 간주하는 최소 연속 줄 수
DUP_WARN_PERCENT=5       # 경고 임계값 (%)
DUP_FAIL_PERCENT=10      # 실패 임계값 (%)

echo "=========================================="
echo "  Duplication Check"
echo "=========================================="

# --- 방법 1: jscpd 사용 가능 시 ---
echo ""
echo "--- 중복 코드 분석 ---"

if command -v jscpd &>/dev/null; then
    echo "  jscpd 사용"

    # Python
    if [ -d "$BACKEND_DIR" ]; then
        echo ""
        echo "  [Python Backend]"
        PY_RESULT=$(jscpd "$BACKEND_DIR" \
            --min-lines "$MIN_DUP_LINES" \
            --reporters "consoleFull" \
            --ignore "**/__pycache__/**,**/test*/**,**/alembic/**" \
            --format "python" \
            2>&1 || true)
        echo "$PY_RESULT" | tail -5

        PY_DUP_PERCENT=$(echo "$PY_RESULT" | grep -oE '[0-9.]+%' | head -1 | tr -d '%' || echo "0")
        PY_DUP_INT=${PY_DUP_PERCENT%.*}

        if [ "${PY_DUP_INT:-0}" -ge "$DUP_FAIL_PERCENT" ]; then
            echo "  FAIL: Python 중복률 ${PY_DUP_PERCENT}% (>${DUP_FAIL_PERCENT}%)"
            ERRORS=$((ERRORS + 1))
        elif [ "${PY_DUP_INT:-0}" -ge "$DUP_WARN_PERCENT" ]; then
            echo "  WARN: Python 중복률 ${PY_DUP_PERCENT}% (>${DUP_WARN_PERCENT}%)"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "  PASS: Python 중복률 ${PY_DUP_PERCENT}%"
        fi
    fi

    # TypeScript
    if [ -d "$WEB_DIR/src" ]; then
        echo ""
        echo "  [TypeScript Web]"
        TS_RESULT=$(jscpd "$WEB_DIR/src" \
            --min-lines "$MIN_DUP_LINES" \
            --reporters "consoleFull" \
            --ignore "**/__tests__/**,**/*.test.*,**/*.d.ts" \
            --format "typescript,tsx" \
            2>&1 || true)
        echo "$TS_RESULT" | tail -5

        TS_DUP_PERCENT=$(echo "$TS_RESULT" | grep -oE '[0-9.]+%' | head -1 | tr -d '%' || echo "0")
        TS_DUP_INT=${TS_DUP_PERCENT%.*}

        if [ "${TS_DUP_INT:-0}" -ge "$DUP_FAIL_PERCENT" ]; then
            echo "  FAIL: TypeScript 중복률 ${TS_DUP_PERCENT}% (>${DUP_FAIL_PERCENT}%)"
            ERRORS=$((ERRORS + 1))
        elif [ "${TS_DUP_INT:-0}" -ge "$DUP_WARN_PERCENT" ]; then
            echo "  WARN: TypeScript 중복률 ${TS_DUP_PERCENT}% (>${DUP_WARN_PERCENT}%)"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "  PASS: TypeScript 중복률 ${TS_DUP_PERCENT}%"
        fi
    fi

else
    # --- 방법 2: jscpd 없을 때 간단한 자체 분석 ---
    echo "  jscpd 미설치 — 간이 분석 모드 (npm i -g jscpd 권장)"
    echo ""

    # Python: 동일 함수 시그니처 중복 탐지
    echo "  [Python 동일 함수 시그니처]"
    if [ -d "$BACKEND_DIR" ]; then
        DUP_FUNCS=$(find "$BACKEND_DIR" -name "*.py" -not -path "*/test*" -not -path "*/__pycache__/*" \
            -exec grep -hE '^\s*(async )?def [a-z_]+\(' {} + 2>/dev/null \
            | sed 's/^\s*//' \
            | sort | uniq -d || true)

        if [ -n "$DUP_FUNCS" ]; then
            DUP_COUNT=$(echo "$DUP_FUNCS" | wc -l | xargs)
            echo "  WARN: 동일 시그니처 함수 ${DUP_COUNT}개 (의도적 오버라이드가 아니면 리팩터링 필요)"
            echo "$DUP_FUNCS" | head -10 | sed 's/^/    /'
            WARNINGS=$((WARNINGS + 1))
        else
            echo "  PASS: 함수 시그니처 중복 없음"
        fi
    fi

    # TypeScript: 동일 import 패턴 (과도한 유사 파일 감지)
    echo ""
    echo "  [TypeScript 유사 import 패턴]"
    if [ -d "$WEB_DIR/src" ]; then
        # 각 파일의 import 블록을 해시화하여 동일 패턴 찾기
        DUP_IMPORTS=$(find "$WEB_DIR/src" \( -name "*.ts" -o -name "*.tsx" \) \
            -not -name "*.test.*" -not -name "*.d.ts" -not -path "*/__tests__/*" \
            -exec sh -c '
                imports=$(grep "^import " "$1" 2>/dev/null | sort | md5sum 2>/dev/null | cut -d" " -f1 || echo "")
                lines=$(grep -c "^import " "$1" 2>/dev/null || echo "0")
                if [ "$lines" -gt 5 ]; then
                    echo "$imports $1"
                fi
            ' _ {} \; 2>/dev/null \
            | sort | awk '{hash=$1; $1=""; files[hash]=files[hash] $0} END {for(h in files) {n=split(files[h],a," "); if(n>1) print n"개 파일 동일 import:" files[h]}}' \
            || true)

        if [ -n "$DUP_IMPORTS" ]; then
            echo "  INFO: 유사 import 패턴 감지 (리팩터링 후보)"
            echo "$DUP_IMPORTS" | head -5 | sed 's/^/    /'
        else
            echo "  PASS"
        fi
    fi

    # 공통: 긴 동일 문자열 리터럴 반복
    echo ""
    echo "  [반복 문자열 리터럴 (>3회)]"
    REPEATED_STRINGS=""
    if [ -d "$BACKEND_DIR" ]; then
        PY_STRINGS=$(find "$BACKEND_DIR" -name "*.py" -not -path "*/test*" -not -path "*/__pycache__/*" \
            -exec grep -ohE '"[^"]{20,}"' {} + 2>/dev/null \
            | sort | uniq -c | sort -rn | awk '$1 > 3 {print}' | head -5 || true)
        REPEATED_STRINGS="${PY_STRINGS}"
    fi

    if [ -d "$WEB_DIR/src" ]; then
        TS_STRINGS=$(find "$WEB_DIR/src" \( -name "*.ts" -o -name "*.tsx" \) -not -name "*.test.*" \
            -exec grep -ohE '"[^"]{20,}"' {} + 2>/dev/null \
            | sort | uniq -c | sort -rn | awk '$1 > 3 {print}' | head -5 || true)
        REPEATED_STRINGS="${REPEATED_STRINGS}${TS_STRINGS:+\n}${TS_STRINGS}"
    fi

    if [ -n "$REPEATED_STRINGS" ]; then
        echo "  INFO: 반복 문자열 (상수 추출 검토)"
        echo -e "$REPEATED_STRINGS" | head -5 | sed 's/^/    /'
    else
        echo "  PASS"
    fi
fi

# --- 결과 ---
echo ""
echo "=========================================="
echo "  결과: 오류 ${ERRORS}건, 경고 ${WARNINGS}건"
echo "=========================================="
exit $ERRORS
