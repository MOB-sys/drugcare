#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Ops — 운영 환경 초기 셋업
# Usage: ./scripts/ops/setup-ops.sh
# ==============================================================================
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/workspace/yakmeogeo}"
OPS_DIR="$PROJECT_DIR/scripts/ops"
LOG_BASE="$PROJECT_DIR/.agents/ops-squad"

echo "=== 약먹어 Ops 셋업 ==="

# --- 로그 디렉토리 생성 ---
echo "1. 로그 디렉토리 생성..."
mkdir -p "$LOG_BASE/health-checker/logs"
mkdir -p "$LOG_BASE/qa-monitor/logs"
mkdir -p "$LOG_BASE/reporter/logs"
echo "   ✅ 완료"

# --- 스크립트 실행 권한 ---
echo "2. 스크립트 실행 권한 설정..."
chmod +x "$OPS_DIR/health-check.sh"
chmod +x "$OPS_DIR/qa-monitor.sh"
chmod +x "$OPS_DIR/daily-report.sh"
echo "   ✅ 완료"

# --- 환경 설정 파일 ---
ENV_FILE="$OPS_DIR/.env.ops"
if [ ! -f "$ENV_FILE" ]; then
    echo "3. 환경 설정 파일 생성..."
    cat > "$ENV_FILE" << 'EOF'
# 약먹어 Ops 환경 설정
# 실제 값으로 수정 후 사용하세요.

PROJECT_DIR=$HOME/workspace/yakmeogeo
API_BASE_URL=https://api.pillright.com
WEB_BASE_URL=https://pillright.com
DOMAIN=pillright.com

# 알림 Webhook (Slack / Discord 등)
ALERT_WEBHOOK_URL=

# 로그 디렉토리 (기본값 사용 시 비워두기)
# LOG_DIR=
EOF
    echo "   ✅ $ENV_FILE 생성 완료"
else
    echo "3. 환경 설정 파일이 이미 존재합니다: $ENV_FILE"
fi

# --- Maintenance Toolkit 셋업 ---
MT_DIR="$PROJECT_DIR/scripts/maintenance"
MT_HOME="$HOME/.pillright-mt"

echo "4. Maintenance Toolkit 디렉토리 생성..."
mkdir -p "$MT_HOME/logs"
mkdir -p "$MT_HOME/state/escalation"
mkdir -p "$MT_HOME/state/healing"
mkdir -p "$MT_HOME/state/watchdog"
mkdir -p "$MT_HOME/run"
mkdir -p "$MT_HOME/backups/db"
echo "   ✅ 완료"

echo "5. Maintenance 스크립트 실행 권한 설정..."
chmod +x "$MT_DIR/backup/db-backup.sh" 2>/dev/null || true
chmod +x "$MT_DIR/escalation/alert-escalation.sh" 2>/dev/null || true
chmod +x "$MT_DIR/self-healing/healing-engine.sh" 2>/dev/null || true
chmod +x "$MT_DIR/watchdog/watchdog-daemon.sh" 2>/dev/null || true
echo "   ✅ 완료"

if [ ! -f "$MT_DIR/config/.env.mt.local" ]; then
    echo "6. Maintenance 환경 설정 생성..."
    cp "$MT_DIR/config/.env.mt" "$MT_DIR/config/.env.mt.local"
    echo "   ✅ $MT_DIR/config/.env.mt.local — 실제 값으로 수정하세요"
else
    echo "6. Maintenance 환경 설정이 이미 존재합니다"
fi

# --- 안내 ---
echo ""
echo "=== 셋업 완료 ==="
echo ""
echo "📌 Watchdog 데몬 사용 (권장 — cron 대체):"
echo "  시작:  $MT_DIR/watchdog/watchdog-daemon.sh start"
echo "  상태:  $MT_DIR/watchdog/watchdog-daemon.sh status"
echo "  중지:  $MT_DIR/watchdog/watchdog-daemon.sh stop"
echo "  로그:  tail -f $MT_HOME/logs/watchdog.log"
echo ""
echo "📌 Watchdog이 자동으로 수행하는 작업:"
echo "  - 자율 복구 (1분마다): 9개 장애 패턴 감지 + 자동 복구"
echo "  - DB 백업 (24시간마다): pg_dump + gzip + 검증"
echo "  - QA 스모크테스트 (6시간마다): 기존 qa-monitor.sh 연동"
echo "  - 일일 리포트 (24시간마다): 기존 daily-report.sh 연동"
echo ""
echo "📌 Watchdog 자체 감시 cron (선택):"
echo "  */5 * * * * $MT_DIR/watchdog/watchdog-daemon.sh status > /dev/null 2>&1 || $MT_DIR/watchdog/watchdog-daemon.sh start"
echo ""
