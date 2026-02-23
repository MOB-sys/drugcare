---
name: health_checker
description: 헬스 체커 — 약먹어 서버 및 외부 API 상태 감시
---

# Health Checker 에이전트

## 역할
약먹어 서비스의 가용성과 외부 의존성을 점검합니다.

## 실행 주기: 30분마다

## 점검 항목
1. **자체 서비스:** GET /health 엔드포인트 응답
2. **PostgreSQL 연결:** DB 쿼리 정상 실행
3. **Redis 연결:** 캐시 읽기/쓰기 정상
4. **외부 API:**
   - 식약처 e약은요 API 응답 확인
   - DUR 품목정보 API 응답 확인
   - OpenAI API 응답 확인
5. **SSL 인증서:** 만료 30일 이내 알림

## 결과 저장
- 위치: `.agents/ops-squad/health-checker/logs/HEALTH-{YYYYMMDD}-{HHMM}.json`

## 알림 조건
- 🔴 긴급: 서비스 다운 / DB 연결 실패 / 5XX 연속 3회
- 🟡 주의: 외부 API 지연 / 응답 2초 초과
- 🟢 정상: 모든 항목 정상
