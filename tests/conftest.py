"""테스트 공통 픽스처 — httpx AsyncClient + 의존성 오버라이드 + Mock 팩토리."""

from collections.abc import AsyncGenerator
from datetime import datetime, time, timezone
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.main import app
from src.backend.models.interaction import ItemType, Severity


TEST_DEVICE_ID = "test-device-550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def device_id() -> str:
    """테스트용 디바이스 UUID를 반환한다."""
    return TEST_DEVICE_ID


@pytest.fixture
def auth_headers(device_id: str) -> dict[str, str]:
    """X-Device-ID 헤더가 포함된 dict를 반환한다.

    Args:
        device_id: 테스트용 디바이스 UUID.

    Returns:
        인증 헤더 dict.
    """
    return {"X-Device-ID": device_id}


# ---------------------------------------------------------------------------
# Mock ORM 객체 팩토리
# ---------------------------------------------------------------------------

def mock_drug(**overrides) -> MagicMock:
    """DrugSearchItem/DrugDetail 호환 mock Drug ORM 객체를 생성한다.

    Args:
        **overrides: 기본값 덮어쓰기.

    Returns:
        MagicMock Drug 인스턴스.
    """
    defaults = {
        "id": 1,
        "item_seq": "200001234",
        "item_name": "타이레놀정500밀리그램",
        "entp_name": "한국얀센",
        "etc_otc_code": "일반의약품",
        "class_no": "01140",
        "chart": "흰색 장방형 정제",
        "bar_code": "8806469012345",
        "material_name": "아세트아미노펜",
        "ingredients": [{"name": "아세트아미노펜", "amount": "500", "unit": "mg"}],
        "efcy_qesitm": "두통, 치통, 생리통 등",
        "use_method_qesitm": "1회 1~2정, 1일 3~4회",
        "atpn_warn_qesitm": "간장애 환자 주의",
        "atpn_qesitm": "복용 시 음주 금지",
        "intrc_qesitm": "와파린과 병용 시 주의",
        "se_qesitm": "구역, 구토",
        "deposit_method_qesitm": "실온 보관",
        "item_image": "https://example.com/tylenol.jpg",
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def mock_supplement(**overrides) -> MagicMock:
    """SupplementSearchItem/SupplementDetail 호환 mock Supplement ORM 객체를 생성한다.

    Args:
        **overrides: 기본값 덮어쓰기.

    Returns:
        MagicMock Supplement 인스턴스.
    """
    defaults = {
        "id": 1,
        "product_name": "종근당 비타민C 1000",
        "company": "종근당건강",
        "registration_no": "20040020012345",
        "main_ingredient": "비타민C",
        "ingredients": [{"name": "비타민C", "amount": "1000", "unit": "mg"}],
        "functionality": "항산화 작용",
        "precautions": "과량 섭취 시 설사 가능",
        "intake_method": "1일 1회, 1회 1정",
        "category": "비타민",
        "source": "자체구축",
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def mock_interaction(**overrides) -> MagicMock:
    """InteractionResult 호환 mock Interaction ORM 객체를 생성한다.

    Args:
        **overrides: 기본값 덮어쓰기.

    Returns:
        MagicMock Interaction 인스턴스.
    """
    defaults = {
        "id": 1,
        "item_a_type": ItemType.DRUG,
        "item_a_id": 1,
        "item_a_name": "타이레놀정500밀리그램",
        "item_b_type": ItemType.DRUG,
        "item_b_id": 2,
        "item_b_name": "아스피린정",
        "severity": Severity.WARNING,
        "description": "간독성 위험 증가",
        "mechanism": "아세트아미노펜과 아스피린의 간 대사 경쟁",
        "recommendation": "동시 복용 자제 권고",
        "source": "DUR",
        "source_id": "DUR-001",
        "evidence_level": "official",
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def mock_cabinet_item(**overrides) -> MagicMock:
    """CabinetItemResponse 호환 mock UserCabinet ORM 객체를 생성한다.

    Args:
        **overrides: 기본값 덮어쓰기.

    Returns:
        MagicMock UserCabinet 인스턴스.
    """
    defaults = {
        "id": 1,
        "device_id": TEST_DEVICE_ID,
        "item_type": "drug",
        "item_id": 1,
        "item_name": "타이레놀정500밀리그램",
        "nickname": None,
        "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def mock_reminder(**overrides) -> MagicMock:
    """ReminderResponse 호환 mock Reminder ORM 객체를 생성한다.

    Args:
        **overrides: 기본값 덮어쓰기.

    Returns:
        MagicMock Reminder 인스턴스.
    """
    defaults = {
        "id": 1,
        "device_id": TEST_DEVICE_ID,
        "cabinet_item_id": 1,
        "item_name": "타이레놀정500밀리그램",
        "reminder_time": time(9, 0),
        "days_of_week": [0, 1, 2, 3, 4],
        "is_active": True,
        "memo": "아침 식후",
        "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


# ---------------------------------------------------------------------------
# Mock Redis with get/set
# ---------------------------------------------------------------------------

def _create_mock_db_session() -> AsyncMock:
    """테스트용 모의 DB 세션을 생성한다.

    Returns:
        AsyncMock DB 세션.
    """
    mock_session = AsyncMock()
    # SELECT 1 결과를 모의한다
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_session.execute.return_value = mock_result
    return mock_session


def _create_mock_redis() -> AsyncMock:
    """테스트용 모의 Redis 클라이언트를 생성한다.

    get → None (캐시 미스), set → None.

    Returns:
        AsyncMock Redis 클라이언트.
    """
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = None
    mock_redis.set.return_value = None
    return mock_redis


# ---------------------------------------------------------------------------
# httpx AsyncClient 픽스처
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """httpx AsyncClient 픽스처 — 의존성 오버라이드 적용.

    DB와 Redis 의존성을 모의 객체로 교체한다.

    Yields:
        httpx.AsyncClient 인스턴스.
    """
    mock_db = _create_mock_db_session()
    mock_redis = _create_mock_redis()

    async def override_get_db() -> AsyncGenerator:
        """모의 DB 세션 의존성."""
        yield mock_db

    def override_get_redis() -> AsyncMock:
        """모의 Redis 클라이언트 의존성."""
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_db_error() -> AsyncGenerator[httpx.AsyncClient, None]:
    """DB 에러 상태의 httpx AsyncClient 픽스처.

    DB execute가 예외를 발생시키도록 설정된다.

    Yields:
        httpx.AsyncClient 인스턴스.
    """
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB connection failed")

    mock_redis = _create_mock_redis()

    async def override_get_db() -> AsyncGenerator:
        """에러 모의 DB 세션 의존성."""
        yield mock_db

    def override_get_redis() -> AsyncMock:
        """모의 Redis 클라이언트 의존성."""
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_redis_error() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Redis 에러 상태의 httpx AsyncClient 픽스처.

    Redis ping이 예외를 발생시키도록 설정된다.

    Yields:
        httpx.AsyncClient 인스턴스.
    """
    mock_db = _create_mock_db_session()

    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("Redis connection failed")

    async def override_get_db() -> AsyncGenerator:
        """모의 DB 세션 의존성."""
        yield mock_db

    def override_get_redis() -> AsyncMock:
        """에러 모의 Redis 클라이언트 의존성."""
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
