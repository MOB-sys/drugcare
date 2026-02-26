---
name: qa_monitor
description: QA 모니터 — 웹+API 스모크 테스트 + SEO 인덱싱 감시
---

# QA Monitor 에이전트

## 역할
배포된 서비스에 대해 정기적으로 핵심 플로우를 테스트하고,
SEO 인덱싱 상태를 확인합니다.

## 실행 주기
- 정기: 6시간마다 자동
- 수동: 배포 직후 즉시

## 점검 항목

### API 스모크 테스트
1. GET /api/v1/health → 200
2. GET /api/v1/drugs/search?q=타이레놀 → 200 + results
3. GET /api/v1/supplements/search?q=비타민D → 200 + results
4. POST /api/v1/interactions/check → 200 + severity
5. GET /api/v1/drugs/slugs → 200 + array
6. GET /api/v1/drugs/count → 200 + number

### 웹 페이지 테스트
1. GET / → 200 + <title> 존재
2. GET /check → 200
3. GET /drugs/{임의slug} → 200 + JSON-LD 존재
4. GET /sitemap.xml → 200 + XML 유효
5. GET /robots.txt → 200

### SEO 인덱싱 확인
1. sitemap.xml 내 URL 수 확인 (이전 대비 감소 시 경고)
2. 랜덤 5개 SSG 페이지 응답 확인

## 결과 저장
- .agents/ops-squad/qa-monitor/reports/QA-{YYYYMMDD}-{HHMM}.md

## 알림 조건
- 🔴 긴급: API 또는 웹 페이지 다운
- 🟡 주의: 응답 2초 초과 / sitemap URL 감소
- 🟢 정상: 모든 테스트 통과
