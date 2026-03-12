# ============================================================================
# PillRight Maintenance Toolkit — 환경 설정 (drugcare 통합)
# cp .env.mt .env.mt.local && vi .env.mt.local
# ============================================================================

# --- 프로젝트 ---
PROJECT_DIR="${HOME}/workspace/yakmeogeo"
PROJECT_NAME="yakmeogeo"

# --- 서비스 URL (기존 health-check.sh 변수와 통일) ---
API_BASE="${API_BASE_URL:-https://api.pillright.com}"
WEB_BASE="${WEB_BASE_URL:-https://pillright.com}"
DOMAIN="pillright.com"

# --- Docker 컨테이너명 (기존과 동일) ---
DB_CONTAINER="yakmeogeo-db"
REDIS_CONTAINER="yakmeogeo-redis"
BACKEND_CONTAINER="yakmeogeo-backend"
NGINX_CONTAINER="yakmeogeo-nginx"

# --- DB ---
DB_NAME="yakmeogeo"
DB_USER="yakmeogeo"

# --- 디렉토리 ---
LOG_DIR="${HOME}/.pillright-mt/logs"
STATE_DIR="${HOME}/.pillright-mt/state"
PID_DIR="${HOME}/.pillright-mt/run"
BACKUP_DIR="${HOME}/.pillright-mt/backups/db"

# --- 백업 ---
BACKUP_RETENTION_DAYS=14
S3_BUCKET=""
S3_PREFIX="yakmeogeo/db-backups"

# --- 알림: Webhook (기존 ALERT_WEBHOOK_URL 그대로 사용) ---
ALERT_WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}"

# --- 알림: SMS 에스컬레이션 ---
SMS_WEBHOOK_URL=""
OWNER_PHONE=""

# --- 알림: 전화 에스컬레이션 ---
PHONE_WEBHOOK_URL=""
OWNER_EMAIL=""

# --- Watchdog 주기 (초) ---
HEALING_INTERVAL=60
BACKUP_INTERVAL=86400
QA_INTERVAL=21600
DAILY_REPORT_INTERVAL=86400

# --- 기존 ops 스크립트 연동 ---
QA_SCRIPT="${PROJECT_DIR}/scripts/ops/qa-monitor.sh"
DAILY_REPORT_SCRIPT="${PROJECT_DIR}/scripts/ops/daily-report.sh"
SECURITY_MONITOR_SCRIPT="${PROJECT_DIR}/scripts/review/request-monitor.sh"
