"""애플리케이션 설정(Settings) 단위 테스트 — 기본값 및 프로퍼티 검증."""

from src.backend.core.config import Settings, get_settings


# ---------------------------------------------------------------------------
# Settings 기본값
# ---------------------------------------------------------------------------


def test_settings_default_app_env():
    """APP_ENV 기본값은 'development'이다."""
    s = Settings()
    assert s.APP_ENV == "development"


def test_settings_default_debug():
    """DEBUG 기본값은 True이다."""
    s = Settings()
    assert s.DEBUG is True


def test_settings_default_api_prefix():
    """API_V1_PREFIX 기본값은 '/api/v1'이다."""
    s = Settings()
    assert s.API_V1_PREFIX == "/api/v1"


# ---------------------------------------------------------------------------
# is_development 프로퍼티
# ---------------------------------------------------------------------------


def test_is_development_true():
    """APP_ENV가 'development'이면 is_development는 True이다."""
    s = Settings(APP_ENV="development")
    assert s.is_development is True


def test_is_development_false():
    """APP_ENV가 'production'이면 is_development는 False이다."""
    s = Settings(APP_ENV="production")
    assert s.is_development is False


# ---------------------------------------------------------------------------
# get_settings 싱글턴
# ---------------------------------------------------------------------------


def test_get_settings_returns_settings_instance():
    """get_settings()는 Settings 인스턴스를 반환한다."""
    result = get_settings()
    assert isinstance(result, Settings)


def test_get_settings_singleton():
    """get_settings()는 lru_cache로 동일 인스턴스를 반환한다."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
