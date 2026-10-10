import asyncio

import pytest

from app.core.rate_limit import Limitador

pytestmark = pytest.mark.anyio


async def test_acima_limite_espera_janela_abrir_e_conta_bloqueio(relogio):
    limitador = Limitador(limite_por_minuto=3, relogio=relogio, dormir=relogio.dormir)

    for _ in range(5):
        await limitador.aguardar_vez()

    assert relogio.esperas == [60]
    assert limitador.chamadas_bloqueadas == 1
    assert limitador.chamadas_desde_inicio == 5
    assert limitador.chamadas_ultimo_minuto() == 2


async def test_chamadas_simultaneas_que_esperam_a_janela_contam_todas_como_bloqueadas(relogio):
    async def dormir(segundos: float) -> None:
        await asyncio.sleep(0)
        await relogio.dormir(segundos)

    limitador = Limitador(limite_por_minuto=3, relogio=relogio, dormir=dormir)

    await asyncio.gather(*(limitador.aguardar_vez() for _ in range(6)))

    assert limitador.chamadas_bloqueadas == 3
    assert limitador.chamadas_desde_inicio == 6
