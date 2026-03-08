# PillRight 배포 매뉴얼

> 코드 개발 완료 후, 프로덕션 런칭까지 남은 작업을 단계별로 정리한 실행 매뉴얼입니다.
> 각 단계는 독립적으로 실행 가능하며, 체크박스로 진행 상황을 추적하세요.

---

## Step 1. 프로덕션 서버 준비

### 1-1. 서버 프로비저닝
- [ ] 클라우드 서버 생성 (Oracle Cloud Free Tier / AWS EC2 / 기타)
  - 최소 스펙: 2 vCPU, 4GB RAM, 50GB SSD
  - OS: Ubuntu 22.04 LTS
- [ ] SSH 접속 확인
```bash
ssh user@YOUR_SERVER_IP
```

### 1-2. 서버 초기 설정
```bash
# Docker 설치
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 프로젝트 클론
git clone https://github.com/YOUR_REPO/drugcare.git /opt/pillright
cd /opt/pillright

# 로그 디렉토리 생성
sudo mkdir -p /var/log/pillright
sudo chown $USER:$USER /var/log/pillright
```

### 1-3. 프로덕션 환경변수 설정
```bash
cp .env.production.example .env
nano .env
```

**필수 변경 항목:**
| 변수 | 설명 | 예시 |
|------|------|------|
| `DB_PASSWORD` | PostgreSQL 비밀번호 | 강력한 랜덤 문자열 |
| `REDIS_PASSWORD` | Redis 비밀번호 | 강력한 랜덤 문자열 |
| `DATA_GO_KR_SERVICE_KEY` | 공공데이터포털 API 키 | data.go.kr에서 발급 |
| `OPENAI_API_KEY` | OpenAI API 키 | platform.openai.com에서 발급 |
| `ALERT_WEBHOOK_URL` | Slack/Discord 웹훅 (선택) | Step 7 참조 |

---

## Step 2. DNS + SSL 설정

### 2-1. 도메인 DNS 레코드 설정
도메인 등록기관(가비아, Cloudflare 등)에서 아래 레코드 추가:

| 타입 | 이름 | 값 | 용도 |
|------|------|-----|------|
| A | `api.pillright.com` | `YOUR_SERVER_IP` | API 서버 |
| CNAME | `pillright.com` | `cname.vercel-dns.com` | 웹 (Vercel) |
| CNAME | `www.pillright.com` | `cname.vercel-dns.com` | www 리다이렉트 |

### 2-2. SSL 인증서 발급 (서버에서 실행)
```bash
cd /opt/pillright
bash scripts/deploy/init-ssl.sh api.pillright.com support@pillright.com
```
> Let's Encrypt 인증서가 자동 발급되며, certbot 컨테이너가 자동 갱신합니다.

---

## Step 3. 백엔드 배포

### 3-1. Docker 빌드 + 서비스 시작
```bash
cd /opt/pillright
bash scripts/deploy/deploy.sh
```
> 이 스크립트가 자동으로: Docker 이미지 빌드 → DB/Redis 시작 → Alembic 마이그레이션 → 서비스 시작 → 헬스체크

### 3-2. 배포 확인
```bash
# 헬스체크
curl https://api.pillright.com/api/v1/health

# 기대 응답:
# {"success":true,"data":{"status":"healthy","database":"ok","redis":"ok"}}
```

### 3-3. 약물 데이터 적재
```bash
# 컨테이너 내부에서 데이터 수집 스크립트 실행
docker exec -it yakmeogeo-backend python -m scripts.data-import.run_all
```
> 또는 기존 DB 덤프가 있다면:
```bash
cat dump.sql | docker exec -i yakmeogeo-db psql -U yakmeogeo -d yakmeogeo
```

---

## Step 4. 웹 (Next.js) Vercel 배포

### 4-1. Vercel 프로젝트 생성
1. [vercel.com](https://vercel.com) 로그인
2. "Add New Project" → GitHub 저장소 연결
3. **Framework Preset:** Next.js
4. **Root Directory:** `src/web`
5. **Build Command:** `next build` (기본값)
6. **Output Directory:** `.next` (기본값)

### 4-2. 환경변수 설정 (Vercel Dashboard > Settings > Environment Variables)

| 변수 | 값 | 필수 |
|------|-----|------|
| `NEXT_PUBLIC_API_URL` | `https://api.pillright.com` | ✅ |
| `NEXT_PUBLIC_SITE_URL` | `https://pillright.com` | ✅ |
| `NEXT_PUBLIC_GA_ID` | `G-XXXXXXXXXX` | Step 5-1 후 |
| `NEXT_PUBLIC_ADSENSE_ID` | `ca-pub-XXXXXXX` | Step 6-1 후 |
| `NEXT_PUBLIC_NAVER_SITE_VERIFICATION` | 네이버 인증 코드 | Step 5-3 후 |
| `NEXT_PUBLIC_KAKAO_JS_KEY` | 카카오 JS 키 | Step 6-3 후 |
| `NEXT_PUBLIC_IOS_APP_ID` | App Store ID | Step 8-2 후 |

### 4-3. 커스텀 도메인 연결
1. Vercel Dashboard → Domains
2. `pillright.com` 추가
3. `www.pillright.com` 추가 (→ pillright.com 리다이렉트)
4. DNS 설정이 Step 2에서 완료되었으면 자동 SSL 발급

### 4-4. 배포 확인
```
https://pillright.com 접속 → 메인 페이지 표시 확인
https://pillright.com/check → 상호작용 체크 페이지 확인
```

---

## Step 5. SEO + 분석 설정

### 5-1. Google Analytics 4
1. [analytics.google.com](https://analytics.google.com) 접속
2. "관리" → "속성 만들기"
   - 속성 이름: PillRight
   - 시간대: 한국
   - 통화: KRW
3. 데이터 스트림 추가 → "웹" → `https://pillright.com`
4. **측정 ID** (G-XXXXXXXXXX) 복사
5. Vercel 환경변수에 `NEXT_PUBLIC_GA_ID` 추가 후 재배포

### 5-2. Google Search Console
1. [search.google.com/search-console](https://search.google.com/search-console) 접속
2. "속성 추가" → URL 접두어 → `https://pillright.com`
3. 소유권 확인 (HTML 태그 또는 DNS TXT 레코드)
4. **사이트맵 제출:**
   - URL: `https://pillright.com/sitemap.xml`
   - "Sitemaps" 메뉴에서 제출
5. **색인 생성 요청:**
   - "URL 검사" → 주요 페이지 URL 입력 → "색인 생성 요청"
   - 우선 제출 페이지: `/`, `/check`, `/drugs`, `/supplements`, `/tips`

### 5-3. 네이버 서치어드바이저
1. [searchadvisor.naver.com](https://searchadvisor.naver.com) 접속
2. "사이트 등록" → `https://pillright.com`
3. 소유확인 → HTML 태그 방식 선택 → 인증 코드 복사
4. Vercel 환경변수에 `NEXT_PUBLIC_NAVER_SITE_VERIFICATION` 추가 후 재배포
5. 소유확인 완료 후 사이트맵 제출: `https://pillright.com/sitemap.xml`

---

## Step 6. 수익화 설정

### 6-1. Google AdSense (웹 광고)
1. [adsense.google.com](https://adsense.google.com) 접속
2. 사이트 추가: `pillright.com`
3. AdSense 코드 → Vercel 환경변수 `NEXT_PUBLIC_ADSENSE_ID`에 추가
4. **승인 대기: 2~4주** (사이트에 충분한 콘텐츠가 있어야 함)
5. 승인 후 광고 단위 자동 활성화 (코드에 이미 AdBanner 컴포넌트 배치됨)

### 6-2. Google AdMob (앱 광고)
1. [admob.google.com](https://admob.google.com) 접속
2. 앱 추가: Android + iOS 각각
3. **광고 단위 6개 생성:**

| 플랫폼 | 유형 | 용도 |
|--------|------|------|
| Android | 배너 | 하단 배너 |
| Android | 전면 | 결과 확인 후 |
| Android | 네이티브 | 홈 피드 |
| iOS | 배너 | 하단 배너 |
| iOS | 전면 | 결과 확인 후 |
| iOS | 네이티브 | 홈 피드 |

4. 각 광고 단위 ID를 `.env.prod`에 입력:
```bash
# src/frontend/.env.prod
API_BASE_URL=https://api.pillright.com
ADMOB_ANDROID_BANNER=ca-app-pub-XXXX/YYYY
ADMOB_ANDROID_INTERSTITIAL=ca-app-pub-XXXX/YYYY
ADMOB_ANDROID_NATIVE=ca-app-pub-XXXX/YYYY
ADMOB_IOS_BANNER=ca-app-pub-XXXX/YYYY
ADMOB_IOS_INTERSTITIAL=ca-app-pub-XXXX/YYYY
ADMOB_IOS_NATIVE=ca-app-pub-XXXX/YYYY
```

### 6-3. 카카오 Share SDK
1. [developers.kakao.com](https://developers.kakao.com) 접속
2. "내 애플리케이션" → 앱 추가
   - 앱 이름: PillRight
   - 사업자명: (본인 정보)
3. "플랫폼" → 웹 도메인 추가: `https://pillright.com`
4. "앱 키" → **JavaScript 키** 복사
5. Vercel 환경변수에 `NEXT_PUBLIC_KAKAO_JS_KEY` 추가 후 재배포

---

## Step 7. 모니터링 설정

### 7-1. Slack 웹훅 생성 (또는 Discord)
**Slack:**
1. [api.slack.com/apps](https://api.slack.com/apps) → "Create New App"
2. "Incoming Webhooks" 활성화
3. 채널 선택 → 웹훅 URL 복사
4. 서버 `.env`의 `ALERT_WEBHOOK_URL`에 입력

**Discord:**
1. 서버 설정 → 연동 → 웹훅 → 새 웹훅
2. 웹훅 URL 복사
3. 서버 `.env`의 `ALERT_WEBHOOK_URL`에 입력

### 7-2. Crontab 등록 (프로덕션 서버에서)
```bash
# crontab 편집
crontab -e

# 아래 내용 추가:
# 헬스체크: 30분마다
*/30 * * * * API_BASE_URL=http://localhost:8000 LOG_DIR=/var/log/pillright /opt/pillright/scripts/ops/health-check.sh >> /var/log/pillright/cron.log 2>&1

# QA 모니터: 6시간마다
0 */6 * * * API_BASE_URL=http://localhost:8000 LOG_DIR=/var/log/pillright /opt/pillright/scripts/ops/qa-monitor.sh >> /var/log/pillright/cron.log 2>&1

# 일일 보고서: 매일 09:00
0 9 * * * API_BASE_URL=http://localhost:8000 LOG_DIR=/var/log/pillright /opt/pillright/scripts/ops/daily-report.sh >> /var/log/pillright/cron.log 2>&1

# 로그 정리: 매주 일요일 03:00
0 3 * * 0 find /var/log/pillright -name "*.log" -mtime +30 -delete 2>/dev/null
```

---

## Step 8. 앱스토어 출시

### 8-1. Google Play (Android)

**사전 준비:**
- [ ] Google Play Console 개발자 계정 등록 ($25 일회성) → [play.google.com/console](https://play.google.com/console)

**빌드:**
```bash
cd src/frontend

# 프로덕션 빌드 (AAB)
flutter build appbundle --release \
  --dart-define=API_BASE_URL=https://api.pillright.com \
  --dart-define=ADMOB_ANDROID_BANNER=ca-app-pub-XXXX/YYYY \
  --dart-define=ADMOB_ANDROID_INTERSTITIAL=ca-app-pub-XXXX/YYYY \
  --dart-define=ADMOB_ANDROID_NATIVE=ca-app-pub-XXXX/YYYY

# 결과: build/app/outputs/bundle/release/app-release.aab
```

**업로드:**
1. Google Play Console → "앱 만들기"
   - 앱 이름: PillRight
   - 기본 언어: 한국어
   - 앱 유형: 앱
   - 무료/유료: 무료
2. "프로덕션" → "새 버전 만들기" → AAB 업로드
3. **스토어 등록정보 작성:**
   - 간단한 설명: "이 약이랑 이 영양제, 같이 먹어도 될까? 3초 만에 확인하는 복약 안전 체커"
   - 자세한 설명: 약물 상호작용 체크, 복약 리마인더, 건강팁 등 기능 설명
   - 스크린샷: 최소 2장 (홈, 결과 화면)
   - 카테고리: 의료
   - 콘텐츠 등급: 설문 작성
4. **개인정보처리방침 URL:** `https://pillright.com/privacy`
5. 검토 제출 → **승인 대기: 1~7일**

### 8-2. App Store (iOS)

**사전 준비:**
- [ ] Apple Developer Program 가입 ($99/년) → [developer.apple.com](https://developer.apple.com)
- [ ] Xcode에서 Team 설정 + Provisioning Profile 생성

**빌드:**
```bash
cd src/frontend

# iOS 빌드
flutter build ipa --release \
  --dart-define=API_BASE_URL=https://api.pillright.com \
  --dart-define=ADMOB_IOS_BANNER=ca-app-pub-XXXX/YYYY \
  --dart-define=ADMOB_IOS_INTERSTITIAL=ca-app-pub-XXXX/YYYY \
  --dart-define=ADMOB_IOS_NATIVE=ca-app-pub-XXXX/YYYY

# 결과: build/ios/ipa/pillright.ipa
```

**업로드:**
1. Xcode → Product → Archive → Distribute App → App Store Connect
2. 또는 `xcrun altool --upload-app -f build/ios/ipa/pillright.ipa`
3. [App Store Connect](https://appstoreconnect.apple.com) 에서:
   - 앱 정보 입력 (이름, 부제, 카테고리: 의료)
   - 스크린샷 업로드 (iPhone 6.7", 6.1", iPad)
   - 개인정보처리방침 URL: `https://pillright.com/privacy`
   - 빌드 선택 → 심사 제출
4. **승인 대기: 1~3일**

**승인 후:**
- App Store ID를 Vercel 환경변수 `NEXT_PUBLIC_IOS_APP_ID`에 추가
- 재배포하면 웹에서 Apple Smart Banner 자동 활성화

---

## Step 9. 데이터 보강 (백그라운드)

### 9-1. DUR 데이터 보강
- 정부 API (nedrug.mfds.go.kr) 복구 시 실행
```bash
docker exec -it yakmeogeo-backend python -m scripts.data-import.collectors.dur_interaction_collector
```

### 9-2. 영양제 데이터 확장
- foodsafetykorea.go.kr API 키 승인 후 실행
```bash
docker exec -it yakmeogeo-backend python -m scripts.data-import.collectors.supplement_collector
```

---

## 런칭 체크리스트

| # | 항목 | 완료 |
|---|------|------|
| 1 | 서버 프로비저닝 + SSH 접속 | ☐ |
| 2 | .env 프로덕션 값 세팅 | ☐ |
| 3 | DNS A/CNAME 레코드 설정 | ☐ |
| 4 | SSL 인증서 발급 | ☐ |
| 5 | Docker 배포 + 헬스체크 확인 | ☐ |
| 6 | 약물 데이터 적재 | ☐ |
| 7 | Vercel 배포 + 도메인 연결 | ☐ |
| 8 | GA4 설정 + 환경변수 | ☐ |
| 9 | Google Search Console + 사이트맵 | ☐ |
| 10 | 네이버 서치어드바이저 등록 | ☐ |
| 11 | AdSense 신청 | ☐ |
| 12 | AdMob 광고 단위 생성 | ☐ |
| 13 | 카카오 Share SDK 키 | ☐ |
| 14 | 모니터링 웹훅 + Crontab | ☐ |
| 15 | Android AAB → Google Play 업로드 | ☐ |
| 16 | iOS IPA → App Store 업로드 | ☐ |
| 17 | 웹 → 앱 Smart Banner 연동 | ☐ |

---

## 예상 소요 시간

| 단계 | 소요 | 비고 |
|------|------|------|
| Step 1~3 서버+백엔드 | 반나절 | 서버가 있다면 1시간 |
| Step 4 Vercel 배포 | 30분 | GitHub 연동 시 자동 |
| Step 5 SEO+분석 | 1시간 | 계정 생성 포함 |
| Step 6 수익화 | 1시간 | AdSense 승인은 2~4주 |
| Step 7 모니터링 | 30분 | |
| Step 8 앱스토어 | 1~2일 | 심사 대기 포함 |
| **총계** | **2~3일** | AdSense 승인 제외 |
