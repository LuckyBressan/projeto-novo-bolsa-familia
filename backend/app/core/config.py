from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: str = "INFO"
    modo_mock: bool = True
    mock_dir: Path = Path(__file__).resolve().parents[1] / "data" / "mock"
    portal_api_base_url: str = "https://api.portaldatransparencia.gov.br/api-de-dados"
    portal_transparencia_api_key: SecretStr | None = None
    portal_http_timeout_seconds: float = 10
    portal_max_retries: int = 1
    portal_limite_rpm: int = 150
    cache_ttl_seconds: int = 3600
    cors_origins: str = "http://localhost:5173"

    @property
    def lista_cors_origins(self) -> list[str]:
        return [origem.strip() for origem in self.cors_origins.split(",") if origem.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
