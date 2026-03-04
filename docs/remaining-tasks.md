# 약먹어 (YakMeogeo) 남은 작업 리스트

> 마지막 업데이트: 2026-03-04
> 코드 작업은 사실상 완료. 남은 건 계정 생성·API 키 발급·스토어 등록 등 수동 설정 작업.

---

## 현재 DB 현황

| 테이블 | 건수 | 커버리지 |
|--------|------|----------|
| drugs | 12,422 | 성분 100%, 효능 99.8% (e약은요 기준), slug 100% |
| supplements | 155 | 성분 100%, slug 100% |
| interactions | 346,108 | 약-약 333,493 / 약-영양제 12,554 / 영양제-영양제 61 |
| drug_dur_info | 31,728 | 임부/고령자/용량/기간/효능중복 |

## 테스트 현황

| 영역 | 테스트 수 | 상태 |
|------|----------|------|
| Backend (pytest) | 229+ | ✅ 통과 |
| Web (vitest) | 114+ | ✅ 통과 |
| Flutter (flutter_test) | 131 | ✅ 통과 |
| CI/CD (GitHub Actions) | 8 jobs | ✅ 구성 완료 |

---

## A. 데이터 보강 (API 의존 — 대기)

- [ ] **A-1.** DUR 자동삽입 약물 7,710건 상세정보(효능/용법/주의사항) 보강
  - 필요: 허가정보 API 복구 (현재 data.go.kr 500 에러)
  - 실행: `python -m scripts.data-import.retry_permission_collector`

- [ ] **A-2.** 영양제 데이터 확대 (155건 → 500+건)
  - 필요: foodsafetykorea.go.kr API 키 신청 (data.go.kr 키와 별도)
  - 신청: https://www.foodsafetykorea.go.kr → 인증키 발급
  - 실행: `python -m scripts.data-import.run_collectors --supplements`

---

## B. 프로덕션 배포 (인프라)

- [ ] **B-1.** 프로덕션 DB (PostgreSQL) 프로비저닝
  - Oracle Cloud / AWS RDS / 직접 설치 중 택1
  - DB 생성 후 `alembic upgrade head` 실행

- [ ] **B-2.** 도메인 DNS 설정
  - `pillright.com` → Vercel (웹)
  - `api.pillright.com` → 서버 IP (API)
  - A/CNAME 레코드 설정

- [ ] **B-3.** SSL 인증서 발급
  - API 서버: Let's Encrypt + certbot 자동갱신
  - 웹: Vercel 자동 SSL

- [ ] **B-4.** Docker 컨테이너 서버 배포
  - `docker-compose up -d`
  - nginx + FastAPI + PostgreSQL + Redis

- [ ] **B-5.** Vercel 프로젝트 연결 + 웹 배포
  - GitHub 저장소 연동
  - 환경변수 설정 (NEXT_PUBLIC_API_URL 등)
  - 리전: ICN1 (서울)

- [ ] **B-6.** DB 마이그레이션 실행
  - `alembic upgrade head` (001~004)
  - 데이터 수집 스크립트 순차 실행

---

## C. 수익화 설정 (계정 필요)

- [ ] **C-1.** Google AdSense 승인 신청
  - https://adsense.google.com 에서 사이트 등록
  - 승인 후 `.env` → `NEXT_PUBLIC_ADSENSE_ID` 설정

- [ ] **C-2.** Google Analytics 4 설정
  - https://analytics.google.com 에서 속성 생성
  - `.env` → `NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX`

- [ ] **C-3.** AdMob 광고 단위 6개 생성
  - https://admob.google.com 에서 앱 등록
  - 배너 / 전면 / 네이티브 × Android / iOS = 6개
  - `scripts/build-flutter.sh` 또는 `.env.flutter.prod`에 ID 설정

- [ ] **C-4.** 네이버 서치어드바이저 등록
  - https://searchadvisor.naver.com 에서 사이트 등록
  - `.env` → `NEXT_PUBLIC_NAVER_SITE_VERIFICATION`
  - 사이트맵 제출: `https://pillright.com/sitemap.xml`

- [ ] **C-5.** Google Search Console 등록
  - https://search.google.com/search-console 에서 속성 추가
  - 사이트맵 제출
  - 인덱싱 요청

---

## D. 앱 스토어 출시

- [ ] **D-1.** Android 서명 키스토어 생성
  - `keytool -genkey -v -keystore release.keystore ...`
  - `android/key.properties` 설정

- [ ] **D-2.** Google Play Console 등록
  - 개발자 계정 등록 ($25 일회성)
  - AAB 빌드 업로드: `flutter build appbundle --release`
  - 스토어 등록정보 (스크린샷, 설명, 아이콘)

- [ ] **D-3.** App Store Connect 등록
  - Apple Developer Program 가입 ($99/년)
  - IPA 빌드: `flutter build ios --release`
  - Xcode → Archive → App Store Connect 업로드

---

## E. 법적 / 정책 페이지

- [ ] **E-1.** 개인정보처리방침 페이지 (`/privacy`)
  - 필수: 개인정보보호법 준수
  - 내용: 수집 항목, 이용 목적, 보유 기간, 제3자 제공 등

- [ ] **E-2.** 이용약관 페이지 (`/terms`)
  - 필수: 서비스 이용 조건, 면책조항
  - "의사/약사의 전문적 판단을 대체하지 않습니다" 포함

- [ ] **E-3.** 카카오톡 공유 설정
  - https://developers.kakao.com 에서 앱 등록
  - `.env` → `NEXT_PUBLIC_KAKAO_JS_KEY`

---

## F. 운영 / 모니터링

- [ ] **F-1.** Slack 또는 Discord 웹훅 설정
  - 알림 채널 생성 → 웹훅 URL 발급
  - `.env.ops` → `WEBHOOK_URL` 설정

- [ ] **F-2.** 크론탭 등록
  - health-check: 30분 간격
  - qa-monitor: 6시간 간격
  - daily-report: 매일 09:00
  - 실행: `scripts/ops/setup-ops.sh`

---

## 우선순위 추천

### Phase 1: 배포 (1~2일)
B-1 → B-6 → B-4 → B-2 → B-3 → B-5

### Phase 2: 법적 + SEO (1일)
E-1 → E-2 → C-2 → C-4 → C-5

### Phase 3: 수익화 (승인 대기)
C-1 → C-3

### Phase 4: 앱 출시 (2~3일)
D-1 → D-2 → D-3

### Phase 5: 운영 안정화
F-1 → F-2

### 백그라운드: 데이터 보강
A-1 (API 복구 대기) → A-2 (API 키 신청 후)
