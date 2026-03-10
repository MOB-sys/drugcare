# PillRight 남은 작업 리스트

> 마지막 업데이트: 2026-03-08
> 코드 작업 완료. 백엔드 서버 배포 완료. 남은 건 계정 생성·웹 배포·스토어 등록 등 수동 작업.

---

## 현재 DB 현황 (2026-03-11 확인)

| 테이블 | 건수 | 커버리지 |
|--------|------|----------|
| drugs | 44,097 | 성분 100%, 효능 99.8%, slug 100% |
| supplements | 44,551 | 성분 100%, 기능성 99.8%, slug 100% |
| interactions | 366,629 | 약-약 / 약-영양제 / 영양제-영양제 |
| drug_dur_info | 31,717 | 임부/고령자/용량/기간/효능중복 |

## 테스트 현황

| 영역 | 테스트 수 | 상태 |
|------|----------|------|
| Backend (pytest) | 229+ | ✅ 통과 |
| Web (vitest) | 114+ | ✅ 통과 |
| Flutter (flutter_test) | 131 | ✅ 통과 |
| CI/CD (GitHub Actions) | 8 jobs | ✅ 구성 완료 |

## 완료된 작업

- [x] **B-1.** 프로덕션 서버 (Vultr) — 158.247.247.74
- [x] **B-2.** 도메인 DNS — `api.pillright.com` → Vultr IP
- [x] **B-3.** SSL — Let's Encrypt (api.pillright.com)
- [x] **B-4.** Docker 배포 — nginx + FastAPI + PostgreSQL + Redis (5 컨테이너)
- [x] **B-6.** DB 마이그레이션 — v001~v004 완료 (9 테이블)
- [x] **D-1.** Android 서명 키스토어 생성
- [x] **E-1.** 개인정보처리방침 페이지 (`/privacy`) — 웹+앱 모두 완료
- [x] **E-2.** 이용약관 페이지 (`/terms`) — 웹+앱 모두 완료
- [x] **F-2.** 크론탭 등록 — health-check(30분), qa-monitor(6시간), daily-report(매일 09:00 KST)

---

## A. 데이터 보강 — ✅ 완료 (2026-03-11 확인)

- [x] **A-1.** 약물 데이터 확대 — 12,422건 → 44,097건 완료
- [x] **A-2.** 영양제 데이터 확대 — 155건 → 44,551건 완료 (foodsafetykorea C003 API)
- [x] **A-3.** 서버 데이터 동기화 — 완료

---

## B. 웹 배포 (Vercel)

- [ ] **B-5.** Vercel 프로젝트 연결 + 웹 배포
  - GitHub 저장소 연동
  - Root Directory: `src/web`
  - 환경변수 설정:
    - `NEXT_PUBLIC_API_URL=https://api.pillright.com`
    - `NEXT_PUBLIC_SITE_URL=https://pillright.com`
  - 리전: ICN1 (서울)
  - `pillright.com` 도메인 연결

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

- [ ] **D-2.** Google Play Console 등록
  - 개발자 계정 등록 ($25 일회성)
  - AAB 빌드 업로드: `flutter build appbundle --release`
  - 스토어 등록정보 (스크린샷, 설명, 아이콘)

- [ ] **D-3.** App Store Connect 등록
  - Apple Developer Program 가입 ($99/년)
  - IPA 빌드: `flutter build ios --release`
  - Xcode → Archive → App Store Connect 업로드

---

## E. 기타 설정

- [ ] **E-3.** 카카오톡 공유 설정
  - https://developers.kakao.com 에서 앱 등록
  - `.env` → `NEXT_PUBLIC_KAKAO_JS_KEY`

---

## F. 운영 / 모니터링

- [ ] **F-1.** Slack 또는 Discord 웹훅 설정
  - 알림 채널 생성 → 웹훅 URL 발급
  - `.env.ops` → `WEBHOOK_URL` 설정
  - 웹훅 연결 후 health-check/qa-monitor 알림 활성화

---

## 우선순위 추천

### Phase 1: 웹 배포 (당일)
B-5 (Vercel 배포) → pillright.com DNS 연결

### Phase 2: SEO 등록 (당일)
C-2 (GA4) → C-4 (네이버) → C-5 (Google Search Console)

### Phase 3: 수익화 (승인 대기 1~2주)
C-1 (AdSense) → C-3 (AdMob)

### Phase 4: 앱 출시 (2~3일)
D-2 (Google Play) → D-3 (App Store)

### Phase 5: 운영
F-1 (알림 웹훅) → A-3 (서버 데이터 동기화)

### 백그라운드: 데이터 보강
A-1 (API 복구 대기) → A-2 (API 키 신청 후)
