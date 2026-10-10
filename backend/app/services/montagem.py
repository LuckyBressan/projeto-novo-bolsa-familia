import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import httpx

from app.cache.memory import CacheMemoria
from app.core.config import Settings
from app.core.rate_limit import Limitador
from app.integrations.mock_portal import MockPortalClient
from app.integrations.portal_transparencia import PortalClient
from app.services.fonte_dados import FonteDados

logger = logging.getLogger(__name__)


@asynccontextmanager
async def montar_fonte_dados(settings: Settings) -> AsyncIterator[FonteDados]:
    cache = CacheMemoria(ttl_segundos=settings.cache_ttl_seconds)
    limitador = Limitador(limite_por_minuto=settings.portal_limite_rpm)
    if settings.modo_mock:
        yield FonteDados(MockPortalClient(settings.mock_dir), cache, limitador)
        return
    if settings.portal_transparencia_api_key is None:
        logger.error("MODO_MOCK=false sem PORTAL_TRANSPARENCIA_API_KEY: as consultas ao Portal vão falhar")
    chave = settings.portal_transparencia_api_key.get_secret_value() if settings.portal_transparencia_api_key else ""
    async with httpx.AsyncClient(
        base_url=settings.portal_api_base_url,
        timeout=settings.portal_http_timeout_seconds,
    ) as http:
        cliente = PortalClient(http, chave=chave, max_novas_tentativas=settings.portal_max_retries)
        yield FonteDados(cliente, cache, limitador)
