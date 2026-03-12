#!/usr/bin/env bash
# ============================================================================
# Review Agent — 코드 복잡도 분석
# Python 함수/파일 길이, TypeScript 파일 길이, 순환 복잡도 검사
# ============================================================================
set -euo pipefail

BACKEND_DIR="${1:-src/backend}"
WEB_DIR="${2:-src/web}"
ERRORS=0
WARNINGS=0

# 임계값
PY_FUNC_MAX=50          # Python 함수 최대 줄 수
PY_FILE_MAX=500         # Python 파일 최대 줄 수
TS_FILE_MAX=400         # TypeScript 파일 최대 줄 수
TS_COMPONENT_MAX=300    # React 컴포넌트 파일 최대 줄 수
RADON_THRESHOLD="C"     # 순환 복잡도 임계값 (A=최상, F=최하)

echo "=========================================="
echo "  Complexity Check"
echo "=========================================="

# --- C-1: Python 함수 길이 ---
echo ""
echo "--- C-1: Python 함수 길이 (>${PY_FUNC_MAX}줄) ---"

LONG_FUNCS=""
if [ -d "$BACKEND_DIR" ]; then
    # awk로 def/async def 사이 줄 수 계산
    LONG_FUNCS=$(find "$BACKEND_DIR" -name "*.py" -not -path "*/test*" -not -path "*/__pycache__/*" -not -path "*/alembic/*" | while read -r f; do
        awk '
        /^(    )?((async )?def |class )/ {
            if (func_name != "" && NR - func_start > max_lines) {
                printf "%s:%d: %s (%d줄)\n", FILENAME, func_start, func_name, NR - func_start
            }
            func_name = $0
            func_start = NR
        }
        END {
            if (func_name != "" && NR - func_start > max_lines) {
                printf "%s:%d: %s (%d줄)\n", FILENAME, func_start, func_name, NR - func_start
            }
        }
        ' max_lines="$PY_FUNC_MAX" "$f"
    done || true)
fi

if [ -n "$LONG_FUNCS" ]; then
    FUNC_COUNT=$(echo "$LONG_FUNCS" | wc -l | xargs)
    echo "WARN: ${PY_FUNC_MAX}줄 초과 함수 ${FUNC_COUNT}개"
    echo "$LONG_FUNCS"
    WARNINGS=$((WARNINGS + FUNC_COUNT))
else
    echo "PASS"
fi

# --- C-2: Python 파일 길이 ---
echo ""
echo "--- C-2: Python 파일 길이 (>${PY_FILE_MAX}줄) ---"

LONG_PY=""
if [ -d "$BACKEND_DIR" ]; then
    LONG_PY=$(find "$BACKEND_DIR" -name "*.py" -not -path "*/test*" -not -path "*/__pycache__/*" -not -path "*/alembic/*" | while read -r f; do
        lines=$(wc -l < "$f" | xargs)
        if [ "$lines" -gt "$PY_FILE_MAX" ]; then
            echo "$f: ${lines}줄"
        fi
    done || true)
fi

if [ -n "$LONG_PY" ]; then
    PY_COUNT=$(echo "$LONG_PY" | wc -l | xargs)
    echo "WARN: ${PY_FILE_MAX}줄 초과 파일 ${PY_COUNT}개"
    echo "$LONG_PY"
    WARNINGS=$((WARNINGS + PY_COUNT))
else
    echo "PASS"
fi

# --- C-3: TypeScript 파일 길이 ---
echo ""
echo "--- C-3: TypeScript 파일 길이 (>${TS_FILE_MAX}줄) ---"

LONG_TS=""
if [ -d "$WEB_DIR/src" ]; then
    LONG_TS=$(find "$WEB_DIR/src" \( -name "*.ts" -o -name "*.tsx" \) -not -path "*/test*" -not -path "*/__tests__/*" -not -name "*.test.*" -not -name "*.d.ts" | while read -r f; do
        lines=$(wc -l < "$f" | xargs)
        threshold=$TS_FILE_MAX
        # 컴포넌트 파일은 더 엄격
        if echo "$f" | grep -q "components/"; then
            threshold=$TS_COMPONENT_MAX
        fi
        if [ "$lines" -gt "$threshold" ]; then
            echo "$f: ${lines}줄 (임계값 ${threshold})"
        fi
    done || true)
fi

if [ -n "$LONG_TS" ]; then
    TS_COUNT=$(echo "$LONG_TS" | wc -l | xargs)
    echo "WARN: 초과 파일 ${TS_COUNT}개"
    echo "$LONG_TS"
    WARNINGS=$((WARNINGS + TS_COUNT))
else
    echo "PASS"
fi

# --- C-4: 순환 복잡도 (radon 사용 가능 시) ---
echo ""
echo "--- C-4: 순환 복잡도 (Python) ---"

if command -v radon &>/dev/null; then
    COMPLEX=$(radon cc "$BACKEND_DIR" -n "$RADON_THRESHOLD" -s --no-assert 2>/dev/null \
        | grep -v "^$" \
        | grep -v "test" \
        || true)
    if [ -n "$COMPLEX" ]; then
        COMPLEX_COUNT=$(echo "$COMPLEX" | grep -cE "^\s+[A-Z]" || echo "0")
        echo "WARN: 복잡도 ${RADON_THRESHOLD} 이상 함수 ${COMPLEX_COUNT}개"
        echo "$COMPLEX" | head -20
        WARNINGS=$((WARNINGS + 1))
    else
        echo "PASS"
    fi
else
    echo "SKIP: radon 미설치 (pip install radon)"
fi

# --- C-5: export 집중도 (TypeScript) ---
echo ""
echo "--- C-5: 단일 파일 과다 export (>15개) ---"

HEAVY_EXPORTS=""
if [ -d "$WEB_DIR/src" ]; then
    HEAVY_EXPORTS=$(find "$WEB_DIR/src" \( -name "*.ts" -o -name "*.tsx" \) -not -name "*.test.*" -not -name "*.d.ts" -not -name "index.ts" | while read -r f; do
        count=$(grep -cE "^export " "$f" 2>/dev/null || echo "0")
        if [ "$count" -gt 15 ]; then
            echo "$f: export ${count}개"
        fi
    done || true)
fi

if [ -n "$HEAVY_EXPORTS" ]; then
    echo "WARN: 과다 export 파일"
    echo "$HEAVY_EXPORTS"
    WARNINGS=$((WARNINGS + 1))
else
    echo "PASS"
fi

# --- 결과 ---
echo ""
echo "=========================================="
echo "  결과: 오류 ${ERRORS}건, 경고 ${WARNINGS}건"
echo "=========================================="
exit $ERRORS
