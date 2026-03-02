# 프로덕션 배포 체크리스트

## 1. 백엔드 (FastAPI)
- [ ] PostgreSQL 프로덕션 DB 생성 + 마이그레이션 실행
- [ ] Redis 서버 구성
- [ ] `.env` 프로덕션 환경변수 설정 (DB URL, Redis URL, OpenAI API Key)
- [ ] Docker 이미지 빌드 + 배포
- [ ] Nginx SSL 인증서 설정 (Let's Encrypt)
- [ ] CORS에 프로덕션 도메인 추가 (`pillright.com`)

## 2. 웹 (Next.js)
- [ ] Vercel 프로젝트 생성 + Git 연결
- [ ] 환경변수 설정:
  - `NEXT_PUBLIC_API_URL` = 프로덕션 API URL
  - `NEXT_PUBLIC_SITE_URL` = `https://pillright.com`
  - `NEXT_PUBLIC_GA_ID` = Google Analytics 4 측정 ID
  - `NEXT_PUBLIC_ADSENSE_ID` = AdSense 게시자 ID
  - `NEXT_PUBLIC_IOS_APP_ID` = App Store 앱 ID
  - `NEXT_PUBLIC_KAKAO_JS_KEY` = 카카오 JavaScript 앱 키
  - `NEXT_PUBLIC_NAVER_SITE_VERIFICATION` = 네이버 인증 코드
- [ ] 커스텀 도메인 연결 (`pillright.com`)
- [ ] Google Search Console 사이트 등록 + sitemap 제출
- [ ] 네이버 서치어드바이저 사이트 등록
- [ ] Google AdSense 승인 신청

## 3. Flutter 앱 (Android)
- [ ] 키스토어 생성: `keytool -genkey -v -keystore key.jks -keyalg RSA -keysize 2048 -validity 10000`
- [ ] `android/key.properties` 작성 (keyAlias, keyPassword, storeFile, storePassword)
- [ ] `src/frontend/.env.prod` 작성 (실제 AdMob ID 6개 + API URL)
- [ ] AdMob 앱 등록 + 광고 단위 생성 (배너, 전면, 네이티브)
- [ ] `gradle.properties`에 `ADMOB_ANDROID_APP_ID=ca-app-pub-XXXX~YYYY` 추가
- [ ] 빌드: `./scripts/build-flutter.sh prod android`
- [ ] Google Play Console에 AAB 업로드
- [ ] 스토어 등록 정보 작성 (스크린샷, 설명, 개인정보처리방침 URL)

## 4. Flutter 앱 (iOS)
- [ ] Apple Developer 계정 + App ID 등록
- [ ] `ios/Flutter/Production.xcconfig`에 실제 `ADMOB_APP_ID` 설정
- [ ] 빌드: `./scripts/build-flutter.sh prod ios`
- [ ] Xcode에서 Archive → App Store Connect 업로드
- [ ] App Store Connect에서 앱 정보 작성 + 심사 제출

## 5. 도메인 + DNS
- [ ] `pillright.com` 도메인 구매/확인
- [ ] A/CNAME 레코드 설정 (Vercel 웹)
- [ ] API 서브도메인 설정 (`api.pillright.com`)
- [ ] SSL 인증서 자동 갱신 확인

## 6. 모니터링
- [ ] Ops 셋업: `./scripts/ops/setup-ops.sh`
- [ ] `scripts/ops/.env.ops` 실제 값 설정
- [ ] Crontab 등록 (헬스체크 30분, QA 1시간, 리포트 매일)
- [ ] 알림 Webhook 설정 (Slack/Discord)

## 7. 법적 요건
- [ ] 개인정보처리방침 페이지 작성 (`/privacy`)
- [ ] 이용약관 페이지 작성 (`/terms`)
- [ ] 면책조항 모든 결과 페이지에 포함 확인
- [ ] 건강기능식품 광고 규정 준수 확인 (질병 치료 효능 표현 금지)
