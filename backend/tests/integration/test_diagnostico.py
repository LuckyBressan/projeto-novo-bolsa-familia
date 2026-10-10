import pytest
from fastapi.testclient import TestClient

from app.api.dependencias import get_fonte_dados
from app.cache.memory import CacheMemoria
from app.core.rate_limit import Limitador
from app.main import app
from app.services.fonte_dados import FonteDados


class ClienteVazio:
    async def buscar(self, codigo_ibge: str, mes: str):
        return []


@pytest.fixture
def fonte() -> FonteDados:
    fonte = FonteDados(ClienteVazio(), CacheMemoria(ttl_segundos=3600), Limitador(limite_por_minuto=150))
    app.dependency_overrides[get_fonte_dados] = lambda: fonte
    yield fonte
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_consumo_reflete_chamadas_reais_e_cache(fonte):
    await fonte.buscar("4214805", "2024-01")
    await fonte.buscar("4214805", "2024-01")

    with TestClient(app) as cliente:
        corpo = cliente.get("/api/v1/diagnostico/consumo").json()

    assert corpo["chamadas_ultimo_minuto"] == 1
    assert corpo["chamadas_desde_inicio"] == 1
    assert corpo["chamadas_bloqueadas_pelo_limitador"] == 0
    assert corpo["limite_rpm_configurado"] == 150
    assert corpo["cache"] == {"itens": 1, "hits": 1, "misses": 1, "ttl_segundos": 3600}
    assert isinstance(corpo["iniciado_em"], str)
