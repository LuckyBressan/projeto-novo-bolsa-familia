from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResposta

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResposta)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResposta:
    return HealthResposta(status="ok", service="backend", modo_mock=settings.modo_mock)
