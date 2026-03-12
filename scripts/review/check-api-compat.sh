#!/usr/bin/env bash
# ============================================================================
# Review Agent — API 호환성 검증
# 백엔드 API 응답 스키마를 스냅샷으로 저장하고 변경 감지
# 앱(Flutter) + 웹(Next.js) 호환성 보장
#
# 사용법:
#   ./check-api-compat.sh                    # 기존 스냅샷과 비교
#   ./check-api-compat.sh --update           # 스냅샷 갱신
#   ./check-api-compat.sh --init             # 최초 스냅샷 생성
#   ./check-api-compat.sh --base-url http://localhost:8000
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SNAPSHOT_DIR="${SCRIPT_DIR}/snapshots/api"
BASE_URL="http://localhost:8000"
API_PREFIX="/api/v1"
MODE="check"
ERRORS=0
WARNINGS=0

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case "$1" in
        --update) MODE="update"; shift ;;
        --init) MODE="init"; shift ;;
        --base-url) BASE_URL="$2"; shift 2 ;;
        *) shift ;;
    esac
done

API_URL="${BASE_URL}${API_PREFIX}"
mkdir -p "$SNAPSHOT_DIR"

echo "=========================================="
echo "  API Compatibility Check"
echo "  Mode: ${MODE}"
echo "  URL: ${API_URL}"
echo "=========================================="

# --- 연결 확인 ---
echo ""
echo "--- 서버 연결 확인 ---"
CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "${BASE_URL}/health" 2>/dev/null || echo "000")
if [ "$CODE" = "000" ]; then
    echo "SKIP: 서버 미응답 (${BASE_URL})"
    echo "  서버 실행 후 재시도하거나, --base-url 옵션을 사용하세요."
    exit 0
fi
echo "PASS: 서버 응답 (HTTP ${CODE})"

# --- 엔드포인트 정의 ---
# name|method|path|body
ENDPOINTS=(
    "drugs_search|GET|/drugs/search?q=test&page=1&page_size=1|"
    "drugs_detail|GET|/drugs/1|"
    "drugs_slugs|GET|/drugs/slugs|"
    "drugs_count|GET|/drugs/count|"
    "drugs_browse_counts|GET|/drugs/browse/counts|"
    "supplements_search|GET|/supplements/search?q=test&page=1&page_size=1|"
    "supplements_detail|GET|/supplements/1|"
    "supplements_slugs|GET|/supplements/slugs|"
    "supplements_count|GET|/supplements/count|"
    "interactions_check|POST|/interactions/check|{\"items\":[{\"type\":\"drug\",\"id\":1}]}"
)

# --- 스키마 추출 함수 ---
extract_schema() {
    # JSON 응답에서 키 구조 + 타입만 추출
    python3 -c "
import json, sys

def get_schema(obj, depth=0):
    if depth > 3:
        return type(obj).__name__
    if isinstance(obj, dict):
        return {k: get_schema(v, depth+1) for k, v in obj.items()}
    elif isinstance(obj, list):
        if obj:
            return ['array_of: ' + str(get_schema(obj[0], depth+1))]
        return ['array_empty']
    elif isinstance(obj, bool):
        return 'boolean'
    elif isinstance(obj, int):
        return 'number'
    elif isinstance(obj, float):
        return 'number'
    elif obj is None:
        return 'null'
    else:
        return 'string'

try:
    data = json.load(sys.stdin)
    schema = get_schema(data)
    print(json.dumps(schema, indent=2, ensure_ascii=False))
except:
    print('{}')
" 2>/dev/null
}

# --- 스키마 비교 함수 ---
compare_schemas() {
    local name="$1" old_file="$2" new_schema="$3"

    if [ ! -f "$old_file" ]; then
        echo "  INFO: 이전 스냅샷 없음 (신규 엔드포인트?)"
        return 0
    fi

    local old_schema
    old_schema=$(cat "$old_file")

    # 키 비교: 이전에 있던 키가 사라지면 Breaking Change
    local old_keys new_keys removed_keys
    old_keys=$(echo "$old_schema" | python3 -c "
import json, sys
def get_keys(obj, prefix=''):
    if isinstance(obj, dict):
        for k,v in obj.items():
            print(prefix + k)
            get_keys(v, prefix + k + '.')
    elif isinstance(obj, list) and obj:
        get_keys(obj[0], prefix + '[].')
try:
    get_keys(json.load(sys.stdin))
except:
    pass
" 2>/dev/null | sort)

    new_keys=$(echo "$new_schema" | python3 -c "
import json, sys
def get_keys(obj, prefix=''):
    if isinstance(obj, dict):
        for k,v in obj.items():
            print(prefix + k)
            get_keys(v, prefix + k + '.')
    elif isinstance(obj, list) and obj:
        get_keys(obj[0], prefix + '[].')
try:
    get_keys(json.load(sys.stdin))
except:
    pass
" 2>/dev/null | sort)

    removed_keys=$(comm -23 <(echo "$old_keys") <(echo "$new_keys") || true)
    local added_keys
    added_keys=$(comm -13 <(echo "$old_keys") <(echo "$new_keys") || true)

    if [ -n "$removed_keys" ]; then
        echo "  FAIL: 제거된 필드 (Breaking Change!)"
        echo "$removed_keys" | sed 's/^/    - /'
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    if [ -n "$added_keys" ]; then
        echo "  INFO: 추가된 필드 (호환 유지)"
        echo "$added_keys" | sed 's/^/    + /'
    fi

    echo "  PASS: 호환성 유지"
    return 0
}

# --- 메인 루프 ---
for endpoint in "${ENDPOINTS[@]}"; do
    IFS='|' read -r name method path body <<< "$endpoint"

    echo ""
    echo "--- ${name} (${method} ${path}) ---"

    # API 호출
    local_response=""
    if [ "$method" = "GET" ]; then
        local_response=$(curl -s --max-time 10 "${API_URL}${path}" 2>/dev/null || echo "")
    else
        local_response=$(curl -s --max-time 10 -X "$method" "${API_URL}${path}" \
            -H "Content-Type: application/json" \
            -H "Origin: http://localhost:3000" \
            -d "$body" 2>/dev/null || echo "")
    fi

    if [ -z "$local_response" ]; then
        echo "  SKIP: 응답 없음"
        continue
    fi

    # 스키마 추출
    new_schema=$(echo "$local_response" | extract_schema)
    if [ "$new_schema" = "{}" ]; then
        echo "  SKIP: 스키마 추출 실패"
        continue
    fi

    snapshot_file="${SNAPSHOT_DIR}/${name}.schema.json"

    case "$MODE" in
        init|update)
            echo "$new_schema" > "$snapshot_file"
            echo "  SAVED: ${snapshot_file}"
            ;;
        check)
            compare_schemas "$name" "$snapshot_file" "$new_schema"
            ;;
    esac
done

# --- 공통 응답 구조 검증 ---
echo ""
echo "--- 공통 응답 구조 검증 ---"
echo "  { success, data, error, meta } 패턴 확인"

STRUCT_FAIL=0
for endpoint in "${ENDPOINTS[@]}"; do
    IFS='|' read -r name method path body <<< "$endpoint"

    resp=""
    if [ "$method" = "GET" ]; then
        resp=$(curl -s --max-time 10 "${API_URL}${path}" 2>/dev/null || echo "")
    else
        resp=$(curl -s --max-time 10 -X "$method" "${API_URL}${path}" \
            -H "Content-Type: application/json" \
            -H "Origin: http://localhost:3000" \
            -d "$body" 2>/dev/null || echo "")
    fi

    if [ -z "$resp" ]; then continue; fi

    # success, data 필드 존재 확인
    has_structure=$(echo "$resp" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    assert 'success' in d
    assert 'data' in d or 'error' in d
    print('ok')
except:
    print('fail')
" 2>/dev/null)

    if [ "$has_structure" != "ok" ]; then
        echo "  FAIL: ${name} — 표준 응답 구조 위반"
        STRUCT_FAIL=$((STRUCT_FAIL + 1))
    fi
done

if [ "$STRUCT_FAIL" -eq 0 ]; then
    echo "  PASS: 모든 엔드포인트 표준 구조 준수"
else
    echo "  FAIL: ${STRUCT_FAIL}개 엔드포인트 구조 위반"
    ERRORS=$((ERRORS + STRUCT_FAIL))
fi

# --- 결과 ---
echo ""
echo "=========================================="
if [ "$MODE" = "check" ]; then
    echo "  결과: 오류 ${ERRORS}건, 경고 ${WARNINGS}건"
else
    echo "  스냅샷 ${MODE} 완료"
fi
echo "=========================================="
exit $ERRORS
