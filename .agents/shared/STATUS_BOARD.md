# 📊 Status Board — 약먹어 작업 현황판

> 마지막 업데이트: 2026-02-24

## 현재 스프린트: Sprint 6 (베타 출시)

### 완료된 스프린트
| Sprint | 기간 | 핵심 내용 | 상태 |
|--------|------|---------|------|
| Sprint 1 | 1~2주 | 데이터 기반 구축 — FastAPI + DB 스키마 + 데이터 수집 | ✅ DONE |
| Sprint 2 | 3~4주 | 상호작용 엔진 — 서비스 계층 + 라우터 DB 연동 + 130개 테스트 | ✅ DONE |
| Sprint 3 | 5~6주 | Flutter 프론트엔드 — 6개 화면 + API 연동 + 56개 테스트 | ✅ DONE |
| Sprint 4 | 7~8주 | 부가 기능 — AI 설명 + 로컬 알림 + 광고 강화 | ✅ DONE |
| Sprint 5 | 9~10주 | QA + 최적화 — 테스트 강화 + CI/CD + 보안 미들웨어 | ✅ DONE |

### Sprint 6 작업 목록
| # | 태스크 | 담당 | 상태 | 우선순위 | 비고 |
|---|--------|------|------|---------|------|
| 6-1 | 법률 문서 최종본 (이용약관/개인정보처리방침) | Frontend | ✅ DONE | P0 | 플레이스홀더→정식 베타본 |
| 6-2 | Ops Squad 스크립트 (헬스체크/일일보고서/QA모니터) | Ops | ✅ DONE | P0 | crontab 예시 포함 |
| 6-3 | 프로덕션 배포 인프라 (Nginx + docker-compose.prod) | Architect | ✅ DONE | P0 | SSL/HTTPS + Certbot |
| 6-4 | 베타 피드백 수집 (API + 프론트엔드) | Backend/Frontend | ✅ DONE | P0 | /feedback 엔드포인트 + UI |
| 6-5 | 앱 메트릭스 + Kill Criteria 대시보드 | Backend | ✅ DONE | P0 | /metrics 엔드포인트 |
| 6-6 | SEO 최적화 랜딩 페이지 | Frontend | ✅ DONE | P1 | Schema.org + OG 태그 |
| 6-7 | DB 마이그레이션 v002 (feedbacks + app_metrics) | Data | ✅ DONE | P0 | Alembic 002 |
| 6-8 | CI/CD 워크플로우 + 테스트 추가 | Tester | ✅ DONE | P1 | 피드백/메트릭스 테스트 |

### 상태 범례
- ⬜ TODO: 시작 전
- 🔵 IN_PROGRESS: 진행 중
- 🟡 REVIEW: 리뷰 대기
- ✅ DONE: 완료
- 🔴 BLOCKED: 차단됨 (사유 기재 필수)

### 블로커 목록
| 태스크 | 블로커 내용 | 해결 방안 | 담당 |
|--------|-----------|---------|------|
| — | 없음 | — | — |

### Kill Criteria 현황
| 지표 | 목표 | 현재 | 상태 |
|------|------|------|------|
| D7 리텐션 | ≥ 25% | 베타 출시 후 측정 | ⬜ |
| 앱스토어 평점 | ≥ 4.0 | 베타 출시 후 측정 | ⬜ |
| 주간 체크 횟수 | ≥ 500회 | 베타 출시 후 측정 | ⬜ |

### 프로덕션 체크리스트
- [x] 이용약관 / 개인정보처리방침 최종본
- [x] 면책조항 모든 결과 화면 표시
- [x] Ops Squad 스크립트 (헬스체크, QA 모니터, 일일 보고서)
- [x] 프로덕션 Docker Compose + Nginx SSL
- [x] 피드백 수집 API + UI
- [x] Kill Criteria 대시보드 API
- [x] SEO 랜딩 페이지
- [x] CI/CD 워크플로우
- [x] DB 마이그레이션 v002
- [ ] TestFlight / Google Play Beta 빌드 업로드
- [ ] 프로덕션 .env 시크릿 설정
- [ ] SSL 인증서 발급 (Let's Encrypt)
- [ ] 베타 테스터 100명 모집
