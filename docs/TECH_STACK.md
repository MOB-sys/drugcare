# 약먹어 (YakMeogeo) 기술스택 설명서

> **작성일:** 2026-02-25 | **버전:** 1.0.0 | **목적:** 플랫폼 전략 수립을 위한 현황 파악

---

## 1. 프로젝트 현황 요약

| 항목 | 상태 |
|------|------|
| **스프린트** | Sprint 6 완료 (전체 6개 스프린트) |
| **백엔드 API** | 15개 엔드포인트, 209개 테스트 통과 |
| **프론트엔드 UI** | 9개 화면, 131개 테스트 통과 |
| **데이터 파이프라인** | 식약처 3종 API 수집기 + 검증기 완비 |
| **인프라** | Docker + Nginx SSL + CI/CD 구성 완료 |
| **플랫폼 빌드** | 미생성 (android/, ios/, web/ 디렉토리 없음) |

---

## 2. 백엔드 기술스택

### 2.1 핵심 프레임워크

| 기술 | 버전 | 역할 |
|------|------|------|
| **Python** | >= 3.11 | 런타임 |
| **FastAPI** | >= 0.115.0 | 웹 프레임워크 (ASGI, 자동 Swagger 문서) |
| **Uvicorn** | >= 0.30.0 | ASGI 서버 |
| **Pydantic** | >= 2.7.0 | 요청/응답 검증 + 직렬화 |
| **pydantic-settings** | >= 2.3.0 | 환경변수 설정 로딩 (.env) |

### 2.2 데이터베이스

| 기술 | 버전 | 역할 |
|------|------|------|
| **PostgreSQL** | 16 (Alpine) | 메인 RDBMS (JSONB, GIN 인덱스 활용) |
| **SQLAlchemy** | >= 2.0.30 (asyncio) | 비동기 ORM |
| **asyncpg** | >= 0.29.0 | PostgreSQL 비동기 드라이버 |
| **Alembic** | >= 1.13.0 | DB 마이그레이션 (현재 v002) |
| **Redis** | 7 (Alpine) | 캐시 + 레이트리밋 카운터 |

### 2.3 DB 스키마 (7개 테이블)

| 테이블 | 주요 컬럼 | 용도 |
|--------|----------|------|
| `drugs` | item_seq, item_name, ingredients(JSONB), 효능/용법/주의사항 | 의약품 마스터 |
| `supplements` | product_name, ingredients(JSONB), functionality | 영양제 마스터 |
| `interactions` | item_a/b (type+id+name), severity, description, source | 상호작용 데이터 |
| `user_cabinets` | device_id, item_type, item_id, nickname | 복약함 (디바이스별) |
| `reminders` | device_id, cabinet_item_id, reminder_time, days_of_week | 복약 리마인더 |
| `feedbacks` | device_id, category, content, app_version | 베타 피드백 |
| `app_metrics` | device_id, event_type, event_data | 앱 사용 메트릭스 |

### 2.4 API 엔드포인트 (15개)

| 그룹 | Method | Path | 설명 |
|------|--------|------|------|
| **Health** | GET | `/api/v1/health` | DB + Redis 연결 상태 |
| **Drugs** | GET | `/api/v1/drugs/search` | 의약품 검색 (ILIKE + Redis 캐시 24h) |
| | GET | `/api/v1/drugs/{id}` | 의약품 상세 (캐시 3일) |
| **Supplements** | GET | `/api/v1/supplements/search` | 영양제 검색 (캐시 24h) |
| | GET | `/api/v1/supplements/{id}` | 영양제 상세 (캐시 3일) |
| **Interactions** | POST | `/api/v1/interactions/check` | 상호작용 체크 (캐시 7일, AI 설명 30일) |
| **Cabinet** | POST | `/api/v1/cabinet` | 복약함 아이템 추가 |
| | GET | `/api/v1/cabinet` | 복약함 목록 조회 |
| | DELETE | `/api/v1/cabinet/{id}` | 복약함 아이템 삭제 |
| **Reminders** | POST | `/api/v1/reminders` | 리마인더 생성 |
| | GET | `/api/v1/reminders` | 리마인더 목록 |
| | PATCH | `/api/v1/reminders/{id}` | 리마인더 수정 |
| | DELETE | `/api/v1/reminders/{id}` | 리마인더 삭제 |
| **Feedback** | POST | `/api/v1/feedback` | 피드백 제출 |
| **Metrics** | POST | `/api/v1/metrics/event` | 이벤트 기록 |

### 2.5 미들웨어 (6개, 실행순서)

| 순서 | 미들웨어 | 기능 |
|------|---------|------|
| 1 | ErrorHandler | 미처리 예외 → ApiResponse 표준 포맷 변환 |
| 2 | RequestLogger | 요청별 UUID, 구조화 로깅 (method/path/status/duration) |
| 3 | SecurityHeaders | nosniff, DENY, XSS Protection, HSTS (프로덕션) |
| 4 | RateLimiter | Redis 슬라이딩 윈도우 (GET 60/분, 변경 30/분) |
| 5 | DeviceAuth | X-Device-ID 헤더 필수 검증 |
| 6 | CORS | 개발: *, 프로덕션: yakmeogeo.com only |

### 2.6 AI 서비스

| 항목 | 상세 |
|------|------|
| **API** | OpenAI GPT-4o (AsyncOpenAI) |
| **용도** | 상호작용 결과에 대한 자연어 쉬운 설명 생성 |
| **설정** | temperature=0.3, max_tokens=500 |
| **동시성** | asyncio.Semaphore(3) — 최대 3개 병렬 호출 |
| **캐시** | Redis TTL 30일 |
| **규칙** | 한국어 3~4문장, 가능성 표현, "의사/약사와 상담하세요" 마무리 필수 |

### 2.7 Redis 캐시 TTL 정책

| 대상 | TTL |
|------|-----|
| 약물/영양제 검색 | 24시간 |
| 약물/영양제 상세 | 3일 |
| 상호작용 체크 | 7일 |
| AI 설명 | 30일 |

---

## 3. 프론트엔드 기술스택

### 3.1 핵심 프레임워크

| 기술 | 버전 | 역할 |
|------|------|------|
| **Flutter** | >= 3.35.0 | UI 프레임워크 |
| **Dart** | >= 3.9.0 < 4.0.0 | 언어 (pubspec.lock 기준 실질 최소) |
| **flutter_riverpod** | ^2.4.9 | 상태관리 |
| **go_router** | ^13.1.0 | 선언형 라우팅 |
| **dio** | ^5.4.0 | HTTP 클라이언트 |

### 3.2 전체 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| flutter_riverpod | ^2.4.9 | 상태관리 (StateNotifier + FutureProvider) |
| go_router | ^13.1.0 | 라우팅 (StatefulShellRoute 바텀 네비) |
| dio | ^5.4.0 | HTTP 클라이언트 (인터셉터, X-Device-ID 자동 주입) |
| google_mobile_ads | ^5.0.0 | AdMob 광고 SDK (배너/전면/네이티브) |
| uuid | ^4.3.3 | 디바이스 UUID 생성 |
| shared_preferences | ^2.2.2 | 로컬 키-값 저장소 (디바이스 ID 영속화) |
| intl | ^0.19.0 | 날짜 포맷 (한국어) |
| flutter_local_notifications | ^17.2.4 | 로컬 푸시 알림 (주간 반복) |
| timezone | ^0.9.4 | Asia/Seoul 타임존 처리 |
| mocktail | ^1.0.3 | 테스트 모킹 (dev) |
| flutter_lints | ^3.0.1 | 정적 분석 린트 (dev) |

### 3.3 화면 구성 (9개)

| 화면 | 타입 | 라우트 | 네비게이션 |
|------|------|--------|----------|
| **HomeScreen** | ConsumerWidget | `/home` | 바텀탭 0 |
| **CabinetScreen** | ConsumerWidget | `/cabinet` | 바텀탭 1 |
| **ReminderScreen** | ConsumerWidget | `/reminder` | 바텀탭 2 |
| **SettingsScreen** | StatelessWidget | `/settings` | 바텀탭 3 |
| **SearchScreen** | ConsumerStatefulWidget | `/search` | 풀스크린 |
| **ResultScreen** | ConsumerStatefulWidget | `/result` | 풀스크린 |
| **ReminderFormScreen** | ConsumerStatefulWidget | `/reminder/form` | 풀스크린 |
| **LegalScreen** | StatelessWidget | `/settings/legal?type=` | 풀스크린 |
| **FeedbackScreen** | ConsumerStatefulWidget | `/settings/feedback` | 풀스크린 |

### 3.4 상태관리 (Riverpod Provider 11개)

| Provider | 타입 | 상태 |
|----------|------|------|
| sharedPreferencesProvider | Provider | SharedPreferences 인스턴스 |
| deviceIdProvider | Provider | UUID 디바이스 ID |
| dioProvider | Provider | Dio HTTP 클라이언트 |
| appRouterProvider | Provider | GoRouter 인스턴스 |
| drugServiceProvider | Provider | DrugService |
| supplementServiceProvider | Provider | SupplementService |
| interactionServiceProvider | Provider | InteractionService |
| cabinetServiceProvider | Provider | CabinetService |
| reminderServiceProvider | Provider | ReminderService |
| feedbackServiceProvider | Provider | FeedbackService |
| **homeCabinetSummaryProvider** | FutureProvider | 홈 복약함 요약 |
| **searchProvider** | StateNotifierProvider | 검색 상태 (쿼리, 필터, 결과, 선택, 페이지) |
| **interactionResultProvider** | FutureProvider.family | 상호작용 체크 결과 |
| **cabinetProvider** | StateNotifierProvider | 복약함 CRUD |
| **reminderProvider** | StateNotifierProvider | 리마인더 CRUD + 알림 스케줄 |

### 3.5 모델 클래스 (16개)

| 그룹 | 모델 | 주요 필드 |
|------|------|----------|
| **공통** | ItemType (enum) | drug, supplement |
| | Severity (enum) | danger, warning, caution, info + color/icon/label |
| | PaginatedResult\<T\> | items, total, page, pageSize, totalPages |
| | IngredientInfo | name, amount?, unit? |
| **검색** | DrugSearchItem | id, itemSeq, itemName, entpName, itemImage |
| | SupplementSearchItem | id, productName, company, mainIngredient |
| | DrugDetail | 18개 필드 (효능/용법/주의사항 포함) |
| | SupplementDetail | 11개 필드 (기능성/주의사항 포함) |
| | SelectedSearchItem | itemType, itemId, name |
| **결과** | InteractionItem | itemType, itemId |
| | InteractionCheckResponse | totalChecked, interactionsFound, hasDanger, results[] |
| | InteractionResult | itemA/B Name, severity, description, aiExplanation 등 10개 |
| **복약함** | CabinetItem | id, deviceId, itemType, itemId, itemName, nickname |
| | CabinetItemCreate | itemType, itemId, nickname? |
| **리마인더** | Reminder | id, cabinetItemId, reminderTime, daysOfWeek[], isActive, memo |
| | ReminderCreate / ReminderUpdate | 생성/수정용 DTO |

### 3.6 광고 SDK 구성

| 유형 | 위젯/매니저 | 노출 위치 | 비고 |
|------|-----------|----------|------|
| **배너** (320x50) | AdBannerWidget | 결과 화면 하단 | 로드 실패 시 숨김 |
| **네이티브** (90~120px) | NativeAdWidget | 홈 화면 건강팁 아래 | factoryId: 'listTile' |
| **전면** | InterstitialAdManager | 결과 화면 진입 시 | 3분 간격 제한, 자동 프리로드 |

현재 **Google 공식 테스트 광고 ID** 사용 중 (프로덕션 ID 미설정).

### 3.7 알림 시스템

| 항목 | 상세 |
|------|------|
| **패턴** | 싱글톤 (NotificationService.instance) |
| **플러그인** | flutter_local_notifications ^17.2.4 |
| **타임존** | Asia/Seoul (timezone 패키지) |
| **알림 ID** | reminder.id * 10 + dayOfWeek (요일별 고유) |
| **Android 채널** | yakmeogeo_reminder (importance: High) |
| **iOS** | alert + badge + sound 권한 요청 |
| **반복** | matchDateTimeComponents: dayOfWeekAndTime (주간 반복) |

### 3.8 디자인 시스템

| 항목 | 상세 |
|------|------|
| **테마** | Material 3 라이트 테마 |
| **브랜드 색상** | #00BFA5 (민트/청록) |
| **신호등 시스템** | danger(빨강) / warning(주황) / caution(노랑) / info(파랑) / safe(녹색) |
| **카드** | 흰색, elevation 1, borderRadius 12 |
| **버튼** | primary 배경, borderRadius 12, 높이 48 |
| **네비게이션** | Material 3 NavigationBar, 4개 탭, 높이 64 |

### 3.9 아키텍처 패턴

```
lib/
├── core/          # 앱 전역 설정 (DI, 라우팅, 테마, 상수, 유틸)
├── features/      # Feature-first 모듈 구조
│   └── {feature}/
│       ├── screens/     # 화면 위젯
│       ├── providers/   # Riverpod 상태관리
│       ├── models/      # 데이터 모델
│       └── widgets/     # 기능별 위젯
└── shared/        # 공유 자원
    ├── models/    # 공통 모델 (enum, 페이지네이션)
    ├── services/  # API 서비스 + 알림
    └── widgets/   # 공통 위젯 (로딩, 에러, 광고, 면책조항)
```

---

## 4. 인프라 & DevOps

### 4.1 Docker 구성

| 환경 | 파일 | 서비스 |
|------|------|--------|
| **개발** | docker-compose.yml | postgres:16 + redis:7 + backend |
| **프로덕션** | docker-compose.prod.yml | postgres:16 + redis:7 + backend + nginx:1.25 + certbot |

- **Dockerfile**: 멀티스테이지 빌드, python:3.11-slim, 비root 사용자(appuser)
- **헬스체크**: curl /api/v1/health (30초 간격, 3회 재시도)

### 4.2 Nginx (프로덕션)

| 항목 | 설정 |
|------|------|
| **도메인** | yakmeogeo.com, www.yakmeogeo.com |
| **SSL** | Let's Encrypt (Certbot 자동 갱신 12h) |
| **TLS** | v1.2 + v1.3, ECDHE 암호 스위트 |
| **보안 헤더** | HSTS, X-Frame-Options, X-Content-Type-Options |
| **API 프록시** | /api/ → backend:8000 |
| **레이트리밋** | 30r/s, burst=20 |
| **정적 자산** | 30일 캐시, Cache-Control: public, immutable |
| **Gzip** | JSON, text, JS, CSS (min 256 bytes) |

### 4.3 CI/CD (GitHub Actions)

| Job | 내용 |
|-----|------|
| Backend Lint | Ruff + Mypy |
| Backend Test | PostgreSQL 16 + Redis 7 + pytest (커버리지 70%) |
| Frontend Analyze | flutter analyze |
| Frontend Test | flutter test |

### 4.4 운영 스크립트

| 스크립트 | 주기 | 기능 |
|---------|------|------|
| health-check.sh | 30분 | API + Docker + 디스크 점검, Slack/Discord 알림 |
| qa-monitor.sh | 6시간 | 6개 핵심 API E2E 스모크 테스트 |
| daily-report.sh | 매일 09:00 | Markdown 일일 보고서 (상태/리소스/에러) |
| deploy.sh | 수동 | 빌드 → 마이그레이션 → 시작 → 헬스체크 |

---

## 5. 데이터 파이프라인

### 5.1 수집기 (3종)

| 수집기 | API 소스 | 대상 테이블 | 방식 |
|--------|---------|-----------|------|
| EDrugCollector | 식약처 e약은요 | drugs | 전량 수집, upsert, 100건/요청, 0.2초 딜레이 |
| DrugPermissionCollector | 식약처 허가정보 | drugs.ingredients | 기존 drugs 보강 (성분 JSONB) |
| DURInteractionCollector | 식약처 DUR 병용금기 | interactions | severity=danger, 양방향 매칭 |

### 5.2 파서 (2종)

| 파서 | 기능 |
|------|------|
| edrug_parser | HTML 태그 제거, 공백 정규화, 원료성분 → JSONB 변환, API 키 매핑 |
| dur_parser | DUR 키 정규화, 상호작용 설명 생성, source_id=DUR_{seq_a}_{seq_b} |

### 5.3 검증기 (2종)

| 검증기 | 검증 항목 |
|--------|---------|
| drug_validator | 필수 필드, item_seq 형식, item_name 길이, etc_otc_code 유효값 |
| interaction_validator | 필수 8개 필드, item_type, severity, source, evidence_level 통제 어휘, 자기참조 방지 |

---

## 6. 인증 방식

| 항목 | 상세 |
|------|------|
| **방식** | 디바이스 UUID 기반 (회원가입 없음) |
| **생성** | 앱 최초 실행 시 uuid v4 생성 |
| **저장** | SharedPreferences (로컬 영속화) |
| **전송** | HTTP 헤더 `X-Device-ID` (Dio 인터셉터 자동 주입) |
| **서버 검증** | DeviceAuthMiddleware — 헤더 없으면 401 |
| **장점** | 진입장벽 제로, 건강정보 서버 미전송 (개인정보 최소화) |

---

## 7. 테스트 현황

| 영역 | 테스트 수 | 도구 |
|------|----------|------|
| **백엔드 전체** | 209개 | pytest + pytest-asyncio + httpx AsyncClient |
| — 라우터 테스트 | 41개 | httpx → ASGI 직접 테스트 |
| — 서비스 테스트 | 49개 | AsyncMock + MagicMock |
| — 단위 테스트 | 56개 | 미들웨어, 캐시, 설정, 응답 헬퍼 |
| — 데이터 테스트 | 수집기/파서 | Mock HTTP 응답 |
| **프론트엔드 전체** | 131개 | flutter_test + mocktail |
| — 단위 테스트 | 12개 파일 | 모델, 서비스, 유틸리티 |
| — 위젯 테스트 | 11개 파일 | 화면, 공통 위젯 |
| **합계** | **340개** | |

---

## 8. 플랫폼 빌드 현황

### 현재 상태

```
src/frontend/
├── lib/           ✅ 63개 Dart 소스 파일
├── test/          ✅ 23개 테스트 파일
├── pubspec.yaml   ✅ 의존성 정의 완료
├── android/       ❌ 미생성
├── ios/           ❌ 미생성
└── web/           ❌ 미생성
```

### 플랫폼별 네이티브 의존성 영향도

| 패키지 | Android | iOS | Web |
|--------|---------|-----|-----|
| flutter_riverpod | O | O | O |
| go_router | O | O | O |
| dio | O | O | O |
| shared_preferences | O | O | O |
| intl | O | O | O |
| **google_mobile_ads** | O | O | **X** (미지원) |
| **flutter_local_notifications** | O | O | **제한적** (Web Push 별도) |
| **timezone** | O | O | O |
| **uuid** | O | O | O |
| **dart:io Platform** | O | O | **X** (조건부 import 필요) |

### 플랫폼 생성 시 필요 작업

| 플랫폼 | 추가 설정 |
|--------|----------|
| **Android** | AndroidManifest.xml (인터넷/알림 권한), AdMob App ID, 알림 채널, minSdkVersion 조정 |
| **iOS** | Info.plist (알림 권한, ATT 설명), AdMob App ID, Podfile CocoaPods 설정 |
| **Web** | google_mobile_ads 미지원 → 광고 위젯 조건부 렌더링, dart:io → dart:html 분기, 알림 → Web Push API 대체 |

---

## 9. 보안 구현 현황

| 항목 | 구현 상태 |
|------|----------|
| HTTPS/SSL | Nginx + Let's Encrypt (프로덕션) |
| CORS | 프로덕션: yakmeogeo.com only |
| 레이트리밋 | Redis 슬라이딩 윈도우 (GET 60/분, 변경 30/분) |
| 보안 헤더 | nosniff, DENY, XSS Protection, HSTS |
| 요청 로깅 | 요청별 UUID + 구조화 로그 |
| 에러 처리 | 글로벌 예외 핸들러 (스택 트레이스 미노출) |
| DB 크리덴셜 | 환경변수 필수 (.env), 코드 내 하드코딩 없음 |
| 디바이스 인증 | X-Device-ID 헤더 필수 |
| 입력 크기 제한 | Nginx 10MB, 상호작용 체크 최대 20개 아이템 |

---

## 10. 법적 요건 구현

| 항목 | 구현 상태 |
|------|----------|
| 면책조항 | 모든 결과 화면에 DisclaimerBanner 표시 |
| 이용약관 | LegalScreen (type=terms) |
| 개인정보 처리방침 | LegalScreen (type=privacy) |
| 건강정보 보호 | 디바이스 우선 저장, 서버 전송 최소화 |
| 건강기능식품 규제 | 질병 치료 효능 표현 금지 |
