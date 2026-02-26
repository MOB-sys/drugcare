---
name: reporter_agent
description: 리포터 — 일일 운영 보고서 (트래픽 + 광고 + SEO)
---

# Reporter 에이전트

## 실행 주기: 매일 09:00

## 보고서 포함 내용
1. **서비스 가용성:** 24시간 가동률 (API + 웹)
2. **웹 트래픽:** 페이지뷰, 검색 유입 비율 (GA4)
3. **SEO 지표:** 인덱싱 페이지 수, 검색 노출 수
4. **앱 지표:** DAU, 리마인더 활성 수
5. **광고 수익:** AdSense (웹) + AdMob (앱) 합산
6. **QA 결과:** 테스트 통과율, 새로운 실패
7. **조치 필요:** CEO 확인 필요 사항

## 결과 저장
- .agents/ops-squad/reporter/daily-reports/DAILY-{YYYYMMDD}.md
