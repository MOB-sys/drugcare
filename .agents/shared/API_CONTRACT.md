# 📄 약먹어 — API 계약서

> 프론트엔드-백엔드 간 API 인터페이스 정의

## 공통 규칙
- Base URL: `/api/v1`
- 응답 포맷: `{ success, data, error, meta }`
- 인증: 디바이스 기반 (MVP, 회원가입 없음)
- 페이지네이션: `?page=1&limit=20`

---

## 1. 의약품 검색

### GET /api/v1/drugs/search
- **설명:** 의약품명으로 검색
- **Query Params:** `q` (검색어), `page`, `limit`
- **응답 200:**
```json
{
  "success": true,
  "data": {
    "items": [
      { "id": 1, "item_name": "타이레놀정", "entp_name": "한국존슨앤드존슨", "class_name": "해열진통소염제" }
    ],
    "total": 150,
    "page": 1
  }
}
```

## 2. 영양제 검색

### GET /api/v1/supplements/search
- **설명:** 영양제명/성분명으로 검색
- **Query Params:** `q`, `page`, `limit`

## 3. 상호작용 체크 (핵심 API)

### POST /api/v1/interactions/check
- **설명:** 2개 이상 약품/영양제 간 상호작용 체크
- **요청 Body:**
```json
{
  "items": [
    { "type": "drug", "id": 123 },
    { "type": "supplement", "id": 456 },
    { "type": "drug", "id": 789 }
  ]
}
```
- **응답 200:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "item_a": { "type": "drug", "id": 123, "name": "아스피린" },
        "item_b": { "type": "supplement", "id": 456, "name": "오메가3" },
        "severity": "caution",
        "description": "함께 복용 시 출혈 위험이 증가할 수 있습니다.",
        "source": "DrugBank",
        "recommendation": "의사/약사와 상담 후 복용하세요."
      }
    ],
    "overall_severity": "caution",
    "disclaimer": "이 정보는 의사/약사의 전문적 판단을 대체하지 않습니다."
  }
}
```

## 4. 복약함

### GET /api/v1/cabinet
- **설명:** 내 복약함 목록 조회
- **Header:** `X-Device-ID`

### POST /api/v1/cabinet
- **설명:** 복약함에 약/영양제 추가
- **Header:** `X-Device-ID`
- **Body:** `{ "item_type": "drug", "item_id": 123, "dosage": "1정", "schedule": {"times": ["09:00","21:00"], "days": [0,1,2,3,4,5,6]} }`

### DELETE /api/v1/cabinet/:id
- **설명:** 복약함에서 제거

## 5. 리마인더

### GET /api/v1/reminders
### POST /api/v1/reminders
### PUT /api/v1/reminders/:id
### DELETE /api/v1/reminders/:id

## 6. AI 설명 생성

### POST /api/v1/ai/explain
- **설명:** 상호작용 결과에 대한 쉬운 설명 생성 (GPT-4o)
- **Body:** `{ "interaction_id": 1, "user_context": "60대 남성, 고혈압 약 복용 중" }`
- **응답:** `{ "explanation": "쉬운 한국어 설명..." }`
