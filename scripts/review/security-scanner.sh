#!/bin/bash
# ============================================================================
# 보안 스캐너 — 소스코드 취약점 자동 탐지
# drugcare 프로젝트의 백엔드/프론트엔드 보안 이슈를 스캔
#
# 사용법:
#   ./security-scanner.sh [project_dir]
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${1:-$HOME/workspace/yakmeogeo}"
REPORT_DIR="${SCRIPT_DIR}/reports"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="${REPORT_DIR}/scan_${TIMESTAMP}.txt"

ERRORS=0
WARNINGS=0

mkdir -p "$REPORT_DIR"

log() { echo "$1" | tee -a "$REPORT_FILE"; }

header() {
    log ""
    log "=========================================="
    log "  $1"
    log "=========================================="
}

check_pass() { log "  PASS: $1"; }

check_fail() {
    log "  FAIL: $1"
    ERRORS=$((ERRORS + 1))
}

check_warn() {
    log "  WARN: $1"
    WARNINGS=$((WARNINGS + 1))
}

# --- 백엔드 스캔 ---

header "1. 하드코딩 시크릿 스캔 (Python)"
PATTERNS='(api_key|secret|password|token|private_key)\s*=\s*["\x27][^"\x27]{8,}'
FOUND=$(grep -rnE "$PATTERNS" "${PROJECT_DIR}/src/backend/" \
    --include="*.py" \
    | grep -v '\.env' \
    | grep -v 'test' \
    | grep -v 'settings\.' \
    | grep -v 'os\.environ' \
    | grep -v 'config\.' \
    | grep -v '#' \
    || true)
if [ -n "$FOUND" ]; then
    check_fail "하드코딩 시크릿 의심"
    log "$FOUND"
else
    check_pass "하드코딩 시크릿 없음"
fi

header "2. SQL Injection 위험 패턴 (Python)"
RAW_SQL=$(grep -rnE '(text\(|execute\(|raw_sql|\.raw\()' "${PROJECT_DIR}/src/backend/" \
    --include="*.py" \
    | grep -v 'test' \
    | grep -v 'alembic' \
    | grep -v '#' \
    || true)
if [ -n "$RAW_SQL" ]; then
    check_warn "Raw SQL 사용 (수동 검토 필요)"
    log "$RAW_SQL"
else
    check_pass "Raw SQL 패턴 없음 (ORM 100%)"
fi

header "3. eval/exec 사용 (Python)"
EVAL=$(grep -rnE '\b(eval|exec)\s*\(' "${PROJECT_DIR}/src/backend/" \
    --include="*.py" \
    | grep -v 'test' \
    | grep -v '#' \
    || true)
if [ -n "$EVAL" ]; then
    check_fail "eval/exec 사용 발견"
    log "$EVAL"
else
    check_pass "eval/exec 미사용"
fi

header "4. 검색 쿼리 max_length 검증"
NO_MAXLEN=$(grep -rnE 'q:\s*str\s*=\s*Query\(' "${PROJECT_DIR}/src/backend/routers/" \
    --include="*.py" \
    | grep -v 'max_length' \
    || true)
if [ -n "$NO_MAXLEN" ]; then
    check_warn "max_length 미적용 검색 쿼리"
    log "$NO_MAXLEN"
else
    check_pass "모든 검색 쿼리에 max_length 적용"
fi

header "5. Slug 검증 (Path 파라미터)"
SLUG_NOVALIDATION=$(grep -rnE 'by-slug|by_slug' "${PROJECT_DIR}/src/backend/routers/" \
    --include="*.py" -A3 \
    | grep 'slug: str$' \
    || true)
if [ -n "$SLUG_NOVALIDATION" ]; then
    check_warn "slug 검증 없는 엔드포인트"
    log "$SLUG_NOVALIDATION"
else
    check_pass "모든 slug에 패턴 검증 적용"
fi

header "6. DB SSL 설정"
DB_SSL=$(grep -rn 'ssl' "${PROJECT_DIR}/src/backend/core/database.py" || true)
if [ -n "$DB_SSL" ]; then
    check_pass "DB SSL 설정 존재"
else
    check_warn "DB SSL 미설정"
fi

# --- 프론트엔드 스캔 ---

header "7. dangerouslySetInnerHTML (React)"
DANGEROUS=$(grep -rn 'dangerouslySetInnerHTML' "${PROJECT_DIR}/src/web/src/" \
    --include="*.tsx" --include="*.ts" \
    | grep -v 'test' \
    || true)
if [ -n "$DANGEROUS" ]; then
    check_warn "dangerouslySetInnerHTML 사용 (수동 검토)"
    log "$DANGEROUS"
else
    check_pass "dangerouslySetInnerHTML 미사용"
fi

header "8. 하드코딩 시크릿 스캔 (TypeScript)"
TS_SECRETS=$(grep -rnE '(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*["\x27][^"\x27]{8,}' \
    "${PROJECT_DIR}/src/web/src/" \
    --include="*.ts" --include="*.tsx" \
    | grep -v '\.test\.' \
    | grep -v 'process\.env' \
    | grep -v 'type ' \
    | grep -v 'interface ' \
    | grep -v '//' \
    || true)
if [ -n "$TS_SECRETS" ]; then
    check_fail "하드코딩 시크릿 의심 (TypeScript)"
    log "$TS_SECRETS"
else
    check_pass "하드코딩 시크릿 없음"
fi

header "9. .env 파일 Git 추적 여부"
if [ -d "${PROJECT_DIR}/.git" ]; then
    TRACKED_ENV=$(cd "$PROJECT_DIR" && git ls-files '*.env' '*.env.*' 2>/dev/null \
        | grep -v '.env.example' \
        | grep -v '.env.mt' \
        || true)
    if [ -n "$TRACKED_ENV" ]; then
        check_fail ".env 파일이 Git에 추적됨"
        log "$TRACKED_ENV"
    else
        check_pass ".env 파일 Git 미추적"
    fi
else
    log "  SKIP: Git 저장소 아님"
fi

# --- 인프라 스캔 ---

header "10. Docker 보안"
if [ -f "${PROJECT_DIR}/Dockerfile" ] || [ -f "${PROJECT_DIR}/docker-compose.yml" ]; then
    ROOT_USER=$(grep -rn 'USER root' "${PROJECT_DIR}/Dockerfile" 2>/dev/null || true)
    if [ -n "$ROOT_USER" ]; then
        check_warn "Dockerfile에 root 사용"
    else
        check_pass "non-root 사용자"
    fi

    PRIVILEGED=$(grep -rn 'privileged: true' "${PROJECT_DIR}/docker-compose.yml" 2>/dev/null || true)
    if [ -n "$PRIVILEGED" ]; then
        check_fail "privileged 모드 사용"
    else
        check_pass "privileged 모드 미사용"
    fi
else
    log "  SKIP: Docker 설정 없음"
fi

header "11. Nginx 보안 헤더"
NGINX_CONF=$(find "${PROJECT_DIR}" -name "nginx*.conf" -o -name "default.conf" 2>/dev/null | head -5)
if [ -n "$NGINX_CONF" ]; then
    for conf in $NGINX_CONF; do
        for h in "X-Frame-Options" "X-Content-Type-Options" "Strict-Transport-Security"; do
            if grep -q "$h" "$conf" 2>/dev/null; then
                check_pass "$h 설정됨 ($conf)"
            else
                check_warn "$h 미설정 ($conf)"
            fi
        done
    done
else
    log "  SKIP: Nginx 설정 없음"
fi

# --- 결과 ---

header "스캔 결과 요약"
log ""
log "  오류: ${ERRORS}건"
log "  경고: ${WARNINGS}건"
log "  보고서: ${REPORT_FILE}"
log ""

if [ $ERRORS -gt 0 ]; then
    log "  상태: FAIL"
    exit 1
else
    log "  상태: PASS (경고 ${WARNINGS}건)"
    exit 0
fi
