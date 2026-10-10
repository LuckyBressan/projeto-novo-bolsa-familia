from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    modo_mock: bool = True
    mock_dir: Path = Path(__file__).resolve().parents[1] / "data" / "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
