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

# --- Crontab 안내 ---
echo ""
echo "=== Crontab 설정 안내 ==="
echo "아래 명령을 crontab -e 에 추가하세요:"
echo ""
echo "# 헬스체크 (30분 간격)"
echo "*/30 * * * * $OPS_DIR/health-check.sh >> /var/log/yakmeogeo-health.log 2>&1"
echo ""
echo "# QA 모니터링 (1시간 간격)"
echo "0 * * * * $OPS_DIR/qa-monitor.sh >> /var/log/yakmeogeo-qa.log 2>&1"
echo ""
echo "# 일간 리포트 (매일 09:00)"
echo "0 9 * * * $OPS_DIR/daily-report.sh >> /var/log/yakmeogeo-report.log 2>&1"
echo ""
echo "=== 셋업 완료 ==="
