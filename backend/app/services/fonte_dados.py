from datetime import datetime
from typing import Protocol

from app.cache.memory import CacheMemoria
from app.core.rate_limit import Deduplicador, Limitador
from app.integrations.portal_transparencia import RegistroBeneficio


class ClienteFonte(Protocol):
    async def buscar(self, codigo_ibge: str, mes: str) -> list[RegistroBeneficio]: ...


class FonteDados:
    def __init__(self, cliente: ClienteFonte, cache: CacheMemoria, limitador: Limitador):
        self.cliente = cliente
        self.cache = cache
        self.limitador = limitador
        self.iniciado_em = datetime.now().astimezone().replace(microsecond=0)
        self._deduplicador = Deduplicador()

    async def buscar(self, codigo_ibge: str, mes: str) -> list[RegistroBeneficio]:
        chave = (codigo_ibge, mes)
        registros = self.cache.obter(chave)
        if registros is not None:
            return registros
        return await self._deduplicador.executar(chave, lambda: self._consultar(codigo_ibge, mes))

    async def _consultar(self, codigo_ibge: str, mes: str) -> list[RegistroBeneficio]:
        await self.limitador.aguardar_vez()
        registros = await self.cliente.buscar(codigo_ibge, mes)
        self.cache.guardar((codigo_ibge, mes), registros)
        return registros
