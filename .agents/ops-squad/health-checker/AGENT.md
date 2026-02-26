---
name: health_checker
description: 헬스 체커 — 서버 상태 + 웹 응답 + SSL 감시
---

# Health Checker 에이전트

## 실행 주기: 30분마다

## 점검 항목
1. FastAPI: GET /api/v1/health (DB + Redis)
2. Next.js 웹: GET / (200 확인)
3. Docker 컨테이너 상태 (backend, postgres, redis, nginx)
4. Vercel 배포 상태 (웹)
5. SSL 인증서 만료일 (30일 이내 경고)
6. 디스크 사용량 (90% 이상 경고)

## 결과 저장
- .agents/ops-squad/health-checker/logs/HEALTH-{YYYYMMDD}-{HHMM}.json

## 알림 조건
- 🔴 서비스 다운 / 5XX 연속 3회
- 🟡 응답 2초 이상 / SSL 30일 이내
- 🟢 정상
