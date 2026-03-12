#!/bin/bash
# ============================================================================
# 의존성 감사 도구 — pip-audit + npm audit 통합 실행
# Python/Node.js 의존성의 알려진 취약점을 스캔
#
# 사용법:
#   ./dependency-audit.sh [project_dir]
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${1:-$HOME/workspace/yakmeogeo}"
REPORT_DIR="${SCRIPT_DIR}/reports"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="${REPORT_DIR}/dep_audit_${TIMESTAMP}.txt"

ERRORS=0
WARNINGS=0
HAS_PYTHON=false
HAS_NODE=false

mkdir -p "$REPORT_DIR"

log() { echo "$1" | tee -a "$REPORT_FILE"; }

header() {
    log ""
    log "=========================================="
    log "  $1"
    log "=========================================="
}

# --- Python 의존성 ---

header "Python 의존성 감사"

if [ -f "${PROJECT_DIR}/pyproject.toml" ] || [ -f "${PROJECT_DIR}/requirements.txt" ]; then
    HAS_PYTHON=true

    # pip-audit 확인
    if command -v pip-audit &>/dev/null; then
        log "  pip-audit 실행 중..."
        if [ -f "${PROJECT_DIR}/requirements.txt" ]; then
            pip-audit -r "${PROJECT_DIR}/requirements.txt" 2>&1 | tee -a "$REPORT_FILE" || {
                log "  WARN: pip-audit에서 취약점 발견"
                WARNINGS=$((WARNINGS + 1))
            }
        else
            (cd "$PROJECT_DIR" && pip-audit 2>&1 | tee -a "$REPORT_FILE") || {
                log "  WARN: pip-audit에서 취약점 발견"
                WARNINGS=$((WARNINGS + 1))
            }
        fi
    else
        log "  SKIP: pip-audit 미설치 (pip install pip-audit)"
    fi

    # safety 확인
    if command -v safety &>/dev/null; then
        log ""
        log "  safety check 실행 중..."
        if [ -f "${PROJECT_DIR}/requirements.txt" ]; then
            safety check -r "${PROJECT_DIR}/requirements.txt" 2>&1 | tee -a "$REPORT_FILE" || {
                log "  WARN: safety에서 취약점 발견"
                WARNINGS=$((WARNINGS + 1))
            }
        fi
    else
        log "  SKIP: safety 미설치 (pip install safety)"
    fi

    # 버전 고정 여부 확인
    header "Python 의존성 버전 고정 확인"
    if [ -f "${PROJECT_DIR}/pyproject.toml" ]; then
        UNPINNED=$(grep -E '">=' "${PROJECT_DIR}/pyproject.toml" | grep -v '==' || true)
        if [ -n "$UNPINNED" ]; then
            log "  WARN: 미고정 의존성 발견 (>=만 사용)"
            log "$UNPINNED"
            WARNINGS=$((WARNINGS + 1))
        else
            log "  PASS: 모든 의존성 버전 고정됨"
        fi
    fi

    if [ ! -f "${PROJECT_DIR}/requirements.txt" ]; then
        log "  WARN: requirements.txt 미존재 (pip-compile 권장)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    log "  SKIP: Python 프로젝트 아님"
fi

# --- Node.js 의존성 ---

header "Node.js 의존성 감사"

WEB_DIR="${PROJECT_DIR}/src/web"
if [ -f "${WEB_DIR}/package.json" ]; then
    HAS_NODE=true

    log "  npm audit 실행 중..."
    (cd "$WEB_DIR" && npm audit 2>&1 | tee -a "$REPORT_FILE") || true

    # critical 체크
    log ""
    log "  Critical 취약점 체크..."
    if (cd "$WEB_DIR" && npm audit --audit-level=critical 2>/dev/null); then
        log "  PASS: critical 취약점 없음"
    else
        log "  FAIL: critical 취약점 발견!"
        ERRORS=$((ERRORS + 1))
    fi

    # high 체크
    if (cd "$WEB_DIR" && npm audit --audit-level=high 2>/dev/null); then
        log "  PASS: high 취약점 없음"
    else
        log "  WARN: high 취약점 발견"
        WARNINGS=$((WARNINGS + 1))
    fi

    # 오래된 패키지 확인
    header "Node.js 오래된 패키지"
    (cd "$WEB_DIR" && npm outdated 2>&1 | tee -a "$REPORT_FILE") || true
else
    log "  SKIP: Node.js 프로젝트 아님 (${WEB_DIR})"
fi

# --- 결과 ---

header "의존성 감사 결과"
log ""
log "  Python: $([ "$HAS_PYTHON" = true ] && echo '스캔 완료' || echo 'N/A')"
log "  Node.js: $([ "$HAS_NODE" = true ] && echo '스캔 완료' || echo 'N/A')"
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
