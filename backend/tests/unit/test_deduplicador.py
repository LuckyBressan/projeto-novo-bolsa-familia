import asyncio

import pytest

from app.core.rate_limit import Deduplicador

pytestmark = pytest.mark.anyio


async def test_chamadas_iguais_simultaneas_compartilham_uma_execucao():
    deduplicador = Deduplicador()
    liberar = asyncio.Event()
    execucoes = 0

    async def consultar():
        nonlocal execucoes
        execucoes += 1
        await liberar.wait()
        return ["registro"]

    tarefas = [asyncio.create_task(deduplicador.executar(("4214805", "2024-01"), consultar)) for _ in range(3)]
    await asyncio.sleep(0)
    liberar.set()

    assert await asyncio.gather(*tarefas) == [["registro"]] * 3
    assert execucoes == 1
