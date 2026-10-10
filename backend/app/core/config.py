from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    modo_mock: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
