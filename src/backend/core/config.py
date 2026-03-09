"""애플리케이션 설정 — pydantic-settings 기반 환경변수 로딩."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """전역 설정. .env 파일 또는 환경변수에서 자동 로딩."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database — .env 파일에서 실제 값을 설정하세요
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/dbname"
    DATABASE_URL_SYNC: str = "postgresql://user:password@localhost:5432/dbname"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # 공공데이터포털 API
    DATA_GO_KR_SERVICE_KEY: str = ""

    # OpenAI (Phase 2)
    OPENAI_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS_ORIGINS 환경변수를 파싱하여 origin 리스트로 반환한다."""
        if self.CORS_ORIGINS:
            return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return []

    @property
    def is_development(self) -> bool:
        """개발 환경 여부."""
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    """싱글턴 설정 인스턴스 반환."""
    return Settings()
