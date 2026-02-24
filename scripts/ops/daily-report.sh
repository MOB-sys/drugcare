#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Ops — 일일 운영 보고서 (매일 09:00 cron 권장)
# ==============================================================================
set -euo pipefail

# --- 설정 ---
API_BASE="${API_BASE_URL:-http://localhost:8000}"
LOG_DIR="${LOG_DIR:-/var/log/yakmeogeo}"
REPORT_DIR="${LOG_DIR}/reports"
HEALTH_LOG="${LOG_DIR}/health-check.log"
ALERT_WEBHOOK="${ALERT_WEBHOOK_URL:-}"
TODAY=$(date '+%Y-%m-%d')
REPORT_FILE="${REPORT_DIR}/daily-report-${TODAY}.md"

mkdir -p "$REPORT_DIR"

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# --- 보고서 생성 ---
cat > "$REPORT_FILE" << HEADER
# 약먹어 일일 운영 보고서
- **날짜:** ${TODAY}
- **생성 시각:** $(timestamp)

---

HEADER

# 1. 서비스 상태
echo "## 1. 서비스 상태" >> "$REPORT_FILE"

HEALTH_RESPONSE=$(curl -sf --max-time 10 "${API_BASE}/api/v1/health" 2>/dev/null || echo '{"error": "unreachable"}')
echo '```json' >> "$REPORT_FILE"
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null >> "$REPORT_FILE" || echo "$HEALTH_RESPONSE" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 2. Docker 컨테이너 상태
if command -v docker &> /dev/null; then
    echo "## 2. Docker 컨테이너 상태" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    docker ps --filter "name=yakmeogeo" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null >> "$REPORT_FILE" || echo "Docker 접근 불가" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    # 3. 리소스 사용량
    echo "## 3. 리소스 사용량" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    docker stats --no-stream --filter "name=yakmeogeo" --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null >> "$REPORT_FILE" || echo "Docker stats 접근 불가" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# 4. 헬스체크 로그 요약 (최근 24시간)
echo "## 4. 헬스체크 요약 (최근 24시간)" >> "$REPORT_FILE"
if [ -f "$HEALTH_LOG" ]; then
    YESTERDAY=$(date -v-1d '+%Y-%m-%d' 2>/dev/null || date -d '1 day ago' '+%Y-%m-%d' 2>/dev/null || echo "")
    TOTAL_CHECKS=$(grep -c "헬스체크 시작" "$HEALTH_LOG" 2>/dev/null || echo "0")
    SUCCESS_CHECKS=$(grep -c "✅ 정상" "$HEALTH_LOG" 2>/dev/null || echo "0")
    FAIL_CHECKS=$(grep -c "🔴 실패" "$HEALTH_LOG" 2>/dev/null || echo "0")
    WARN_CHECKS=$(grep -c "⚠️" "$HEALTH_LOG" 2>/dev/null || echo "0")

    echo "| 항목 | 수치 |" >> "$REPORT_FILE"
    echo "|------|------|" >> "$REPORT_FILE"
    echo "| 전체 체크 | ${TOTAL_CHECKS}회 |" >> "$REPORT_FILE"
    echo "| 정상 | ${SUCCESS_CHECKS}회 |" >> "$REPORT_FILE"
    echo "| 실패 | ${FAIL_CHECKS}회 |" >> "$REPORT_FILE"
    echo "| 경고 | ${WARN_CHECKS}회 |" >> "$REPORT_FILE"
else
    echo "헬스체크 로그 없음" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 5. 디스크 사용량
echo "## 5. 디스크 사용량" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
df -h / >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 6. DB 사이즈 (Docker PostgreSQL)
if command -v docker &> /dev/null; then
    echo "## 6. 데이터베이스 크기" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    docker exec yakmeogeo-db psql -U yakmeogeo -d yakmeogeo -c \
        "SELECT pg_size_pretty(pg_database_size('yakmeogeo')) AS db_size;" \
        2>/dev/null >> "$REPORT_FILE" || echo "DB 접근 불가" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# 7. 최근 에러 로그
echo "## 7. 최근 에러 로그 (마지막 20건)" >> "$REPORT_FILE"
if command -v docker &> /dev/null; then
    echo '```' >> "$REPORT_FILE"
    docker logs yakmeogeo-backend --since 24h 2>&1 | grep -i "error\|exception\|critical" | tail -20 >> "$REPORT_FILE" 2>/dev/null || echo "에러 로그 없음" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
else
    echo "Docker 환경이 아닌 경우 수동 확인 필요" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

echo "---" >> "$REPORT_FILE"
echo "_보고서 자동 생성: $(timestamp)_" >> "$REPORT_FILE"

echo "[$(timestamp)] 일일 보고서 생성 완료: $REPORT_FILE"

# Slack/Discord 알림 발송
if [ -n "$ALERT_WEBHOOK" ]; then
    curl -sf -X POST "$ALERT_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"📊 약먹어 일일 보고서 (${TODAY}) 생성 완료. 헬스체크: ${SUCCESS_CHECKS}/${TOTAL_CHECKS} 정상\"}" \
        > /dev/null 2>&1 || true
fi
