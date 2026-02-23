# 🏗️ 약먹어 — 기술 아키텍처

> Architect 에이전트가 상세화합니다. 아래는 초기 골격입니다.

## 시스템 구성도
```
[Flutter App (Dart)] ←→ [FastAPI Server (Python)] ←→ [PostgreSQL]
        ↕                        ↕                        ↕
[google_mobile_ads]        [Redis Cache]           [약물 데이터 DB]
        ↕                        ↕
   [Riverpod]            [OpenAI API (GPT-4o)]
```

## DB 스키마 (초안)

### drugs (의약품)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL PK | |
| item_seq | VARCHAR(20) | 식약처 품목기준코드 |
| item_name | VARCHAR(200) | 제품명 |
| entp_name | VARCHAR(200) | 제조사 |
| class_name | VARCHAR(200) | 약효분류 |
| etc_otc_name | VARCHAR(50) | 전문/일반 |
| ingredients | JSONB | 성분 목록 |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### supplements (영양제)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL PK | |
| product_name | VARCHAR(200) | 제품명 |
| brand | VARCHAR(200) | 브랜드 |
| ingredients | JSONB | 성분 목록 |
| daily_dose | JSONB | 일일 복용량 |
| created_at | TIMESTAMP | |

### interactions (상호작용)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL PK | |
| item_a_type | ENUM('drug','supplement','food') | |
| item_a_id | INTEGER | |
| item_b_type | ENUM('drug','supplement','food') | |
| item_b_id | INTEGER | |
| severity | ENUM('safe','caution','danger') | 위험도 |
| description | TEXT | 설명 |
| source | VARCHAR(100) | 출처 (DUR, DrugBank 등) |
| evidence_level | VARCHAR(50) | 근거 수준 |

### user_cabinets (복약함)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL PK | |
| device_id | VARCHAR(100) | 기기 식별자 (서버 미전송 원칙) |
| item_type | ENUM('drug','supplement') | |
| item_id | INTEGER | |
| dosage | VARCHAR(100) | 복용량 |
| schedule | JSONB | 복용 시간 |
| added_at | TIMESTAMP | |

### reminders (리마인더)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL PK | |
| device_id | VARCHAR(100) | |
| time | TIME | 알림 시간 |
| days | INTEGER[] | 요일 (0=일~6=토) |
| items | INTEGER[] | cabinet item ids |
| is_active | BOOLEAN | |

## API 엔드포인트 (초안)
[API_CONTRACT.md 참조]
