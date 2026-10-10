import asyncio

import pytest

from app.cache.memory import CacheMemoria
from app.core.errors import FonteIndisponivel
from app.core.rate_limit import Limitador
from app.services.fonte_dados import FonteDados

pytestmark = pytest.mark.anyio


class ClienteFalso:
    def __init__(self, respostas=None):
        self.chamadas: list[tuple[str, str]] = []
        self._respostas = list(respostas or [])

    async def buscar(self, codigo_ibge: str, mes: str):
        self.chamadas.append((codigo_ibge, mes))
        await asyncio.sleep(0)
        resposta = self._respostas.pop(0) if self._respostas else []
        if isinstance(resposta, Exception):
            raise resposta
        return resposta


def criar_fonte(cliente, relogio) -> FonteDados:
    return FonteDados(
        cliente=cliente,
        cache=CacheMemoria(ttl_segundos=3600, relogio=relogio),
        limitador=Limitador(limite_por_minuto=150, relogio=relogio, dormir=relogio.dormir),
    )


async def test_consulta_repetida_usa_cache_sem_consumir_cota(relogio):
    cliente = ClienteFalso()
    fonte = criar_fonte(cliente, relogio)

    await fonte.buscar("4214805", "2024-01")
    await fonte.buscar("4214805", "2024-01")
    await fonte.buscar("4214805", "2024-02")

    assert cliente.chamadas == [("4214805", "2024-01"), ("4214805", "2024-02")]
    assert fonte.limitador.chamadas_desde_inicio == 2
    assert fonte.cache.hits == 1


async def test_consultas_iguais_simultaneas_geram_uma_chamada(relogio):
    cliente = ClienteFalso()
    fonte = criar_fonte(cliente, relogio)

    await asyncio.gather(*(fonte.buscar("4214805", "2024-01") for _ in range(3)))

    assert cliente.chamadas == [("4214805", "2024-01")]
    assert fonte.limitador.chamadas_desde_inicio == 1


async def test_falha_nao_vira_cache_e_proxima_consulta_tenta_de_novo(relogio):
    cliente = ClienteFalso(respostas=[FonteIndisponivel(), ["registro"]])
    fonte = criar_fonte(cliente, relogio)

    with pytest.raises(FonteIndisponivel):
        await fonte.buscar("4209102", "2024-12")

    assert await fonte.buscar("4209102", "2024-12") == ["registro"]
    assert len(cliente.chamadas) == 2
