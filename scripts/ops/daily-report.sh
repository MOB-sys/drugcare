#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Ops — 일일 운영 보고서 (매일 09:00 cron 권장)
# 듀얼 플랫폼: API + 웹 + 광고 + SEO 종합 보고
# ==============================================================================
set -euo pipefail

# --- 설정 ---
PROJECT_DIR="${PROJECT_DIR:-$HOME/workspace/yakmeogeo}"
API_BASE="${API_BASE_URL:-http://localhost:8000}"
TODAY=$(date +%Y%m%d)
REPORT_DIR="${PROJECT_DIR}/.agents/ops-squad/reporter/daily-reports"
REPORT_FILE="${REPORT_DIR}/DAILY-${TODAY}.md"
ALERT_WEBHOOK="${ALERT_WEBHOOK_URL:-}"

mkdir -p "$REPORT_DIR"

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# --- 최근 24시간 헬스체크 로그 요약 ---
HEALTH_DIR="${PROJECT_DIR}/.agents/ops-squad/health-checker/logs"
TOTAL_CHECKS=$(find "$HEALTH_DIR" -name "HEALTH-${TODAY}*" -type f 2>/dev/null | wc -l | tr -d ' ')
OK_CHECKS=$(grep -l '"overall": "ok"' "$HEALTH_DIR"/HEALTH-${TODAY}* 2>/dev/null | wc -l | tr -d ' ')

# --- QA 테스트 결과 ---
QA_DIR="${PROJECT_DIR}/.agents/ops-squad/qa-monitor/reports"
LATEST_QA=$(ls -t "$QA_DIR"/QA-* 2>/dev/null | head -1)
QA_SUMMARY="보고서 없음"
if [ -n "$LATEST_QA" ]; then
    QA_SUMMARY=$(head -5 "$LATEST_QA" | tail -1)
fi

# --- API 서비스 상태 ---
HEALTH_RESPONSE=$(curl -sf --max-time 10 "${API_BASE}/api/v1/health" 2>/dev/null || echo '{"error": "unreachable"}')

# --- 보고서 생성 ---
cat > "$REPORT_FILE" << EOF
# 📊 약먹어 일일 운영 보고서
**날짜:** $(date '+%Y년 %m월 %d일')

---

## 1. 서비스 가용성
- 헬스체크: ${OK_CHECKS} / ${TOTAL_CHECKS} 정상
- 가동률: $([ "$TOTAL_CHECKS" -gt 0 ] && echo "$((OK_CHECKS * 100 / TOTAL_CHECKS))%" || echo "데이터 없음")
- API 상태:
\`\`\`json
$(echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE")
\`\`\`

## 2. QA 테스트
- 최근 결과: ${QA_SUMMARY}

## 3. 트래픽 (GA4 대시보드 확인)
- [ ] 페이지뷰
- [ ] 검색 유입 비율
- [ ] 신규 사용자

## 4. 광고 수익 (AdSense + AdMob 대시보드 확인)
- [ ] 웹 AdSense 수익
- [ ] 앱 AdMob 수익

## 5. SEO 지표 (Search Console 확인)
- [ ] 인덱싱 페이지 수
- [ ] 검색 노출 수
- [ ] 평균 CTR

## 6. 조치 필요 사항
- (자동 감지된 이슈 여기에 기록)

---
*자동 생성 보고서 ($(timestamp)). GA4/AdSense/Search Console은 수동 확인 필요.*
EOF

echo "✅ 일일 보고서 생성: ${REPORT_FILE}"

# --- 알림 ---
if [ -n "$ALERT_WEBHOOK" ]; then
    curl -sf -X POST "$ALERT_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"📊 약먹어 일일 보고서 ($(date '+%Y-%m-%d')) 생성 완료. 헬스체크: ${OK_CHECKS}/${TOTAL_CHECKS} 정상\"}" \
        > /dev/null 2>&1 || true
fi
