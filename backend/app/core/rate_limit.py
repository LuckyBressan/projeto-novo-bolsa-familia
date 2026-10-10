import asyncio
import time
from collections import deque
from collections.abc import Awaitable, Callable, Hashable
from typing import TypeVar

T = TypeVar("T")

JANELA_SEGUNDOS = 60


class Limitador:
    def __init__(
        self,
        limite_por_minuto: int,
        relogio: Callable[[], float] = time.monotonic,
        dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        self.limite_por_minuto = limite_por_minuto
        self.chamadas_desde_inicio = 0
        self.chamadas_bloqueadas = 0
        self._relogio = relogio
        self._dormir = dormir
        self._chamadas: deque[float] = deque()
        self._trava = asyncio.Lock()

    async def aguardar_vez(self) -> None:
        # Conta na chegada: quem fica na fila atrás de uma chamada em espera encontra a janela já aberta ao entrar.
        if self._janela_cheia():
            self.chamadas_bloqueadas += 1
        async with self._trava:
            while self._janela_cheia():
                await self._dormir(self._chamadas[0] + JANELA_SEGUNDOS - self._relogio())
            self._chamadas.append(self._relogio())
            self.chamadas_desde_inicio += 1

    def chamadas_ultimo_minuto(self) -> int:
        self._descartar_antigas()
        return len(self._chamadas)

    def _janela_cheia(self) -> bool:
        self._descartar_antigas()
        return len(self._chamadas) >= self.limite_por_minuto

    def _descartar_antigas(self) -> None:
        limite = self._relogio() - JANELA_SEGUNDOS
        while self._chamadas and self._chamadas[0] <= limite:
            self._chamadas.popleft()


class Deduplicador:
    def __init__(self):
        self._pendentes: dict[Hashable, asyncio.Task] = {}

    async def executar(self, chave: Hashable, consultar: Callable[[], Awaitable[T]]) -> T:
        tarefa = self._pendentes.get(chave)
        if tarefa is None:
            tarefa = asyncio.ensure_future(consultar())
            self._pendentes[chave] = tarefa
            tarefa.add_done_callback(lambda _: self._pendentes.pop(chave, None))
        # Se quem espera desistir (cliente desconectou), a consulta compartilhada segue para os demais.
        return await asyncio.shield(tarefa)
