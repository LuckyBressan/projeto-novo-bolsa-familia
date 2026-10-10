import time
from collections.abc import Callable, Hashable
from typing import Any


class CacheMemoria:
    def __init__(self, ttl_segundos: float, relogio: Callable[[], float] = time.monotonic):
        self.ttl_segundos = ttl_segundos
        self.hits = 0
        self.misses = 0
        self._relogio = relogio
        self._itens: dict[Hashable, tuple[float, Any]] = {}

    @property
    def itens(self) -> int:
        self._remover_expirados()
        return len(self._itens)

    def obter(self, chave: Hashable) -> Any | None:
        item = self._itens.get(chave)
        if item is None or self._relogio() >= item[0]:
            self._itens.pop(chave, None)
            self.misses += 1
            return None
        self.hits += 1
        return item[1]

    def guardar(self, chave: Hashable, valor: Any) -> None:
        self._itens[chave] = (self._relogio() + self.ttl_segundos, valor)

    def _remover_expirados(self) -> None:
        agora = self._relogio()
        for chave in [chave for chave, (expira_em, _) in self._itens.items() if agora >= expira_em]:
            del self._itens[chave]
