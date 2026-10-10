import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from decimal import Decimal

import httpx

from app.core.errors import FonteIndisponivel, LimiteFonteExcedido, RespostaFonteInvalida

ENDPOINT = "/novo-bolsa-familia-por-municipio"
ESPERA_FALHA_TEMPORARIA_SEGUNDOS = 1
ESPERA_LIMITE_PADRAO_SEGUNDOS = 5

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegistroBeneficio:
    codigo_ibge: str
    municipio_nome: str | None
    uf: str | None
    mes: str
    valor: Decimal
    quantidade_beneficiados: int
    tipo_beneficio: str | None
    id_fonte: int | None


def converter_registro(item: dict) -> RegistroBeneficio:
    municipio = item["municipio"]
    return RegistroBeneficio(
        codigo_ibge=str(municipio["codigoIBGE"]),
        municipio_nome=municipio.get("nomeIBGE"),
        uf=(municipio.get("uf") or {}).get("sigla"),
        mes=item["dataReferencia"][:7],
        valor=Decimal(str(item["valor"])),
        quantidade_beneficiados=int(item["quantidadeBeneficiados"]),
        tipo_beneficio=(item.get("tipo") or {}).get("descricao"),
        id_fonte=item.get("id"),
    )


class PortalClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        chave: str,
        max_novas_tentativas: int = 1,
        dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        self._http = http
        self._chave = chave
        self._max_novas_tentativas = max_novas_tentativas
        self._dormir = dormir

    async def buscar(self, codigo_ibge: str, mes: str) -> list[RegistroBeneficio]:
        resposta = await self._requisitar(codigo_ibge, mes)
        if resposta.status_code in (401, 403):
            logger.error("Portal recusou a chave (HTTP %s); verifique PORTAL_TRANSPARENCIA_API_KEY", resposta.status_code)
            raise FonteIndisponivel()
        if resposta.status_code >= 400:
            logger.error("Portal rejeitou a consulta (HTTP %s) codigoIbge=%s mes=%s", resposta.status_code, codigo_ibge, mes)
            raise FonteIndisponivel()
        try:
            itens = json.loads(resposta.content, parse_float=Decimal)
            if not isinstance(itens, list):
                raise TypeError("a resposta não é uma lista")
            registros = [converter_registro(item) for item in itens]
        except (ValueError, TypeError, KeyError, AttributeError) as erro:
            logger.error(
                "Resposta do Portal fora do formato esperado (%s) codigoIbge=%s mes=%s",
                type(erro).__name__, codigo_ibge, mes,
            )
            raise RespostaFonteInvalida() from erro
        if len(registros) > 1:
            logger.warning(
                "Portal devolveu %s registros para codigoIbge=%s mes=%s; serão somados (decisão D02)",
                len(registros), codigo_ibge, mes,
            )
        return registros

    async def _requisitar(self, codigo_ibge: str, mes: str) -> httpx.Response:
        for tentativa in range(self._max_novas_tentativas + 1):
            try:
                resposta = await self._http.get(
                    ENDPOINT,
                    params={"mesAno": mes.replace("-", ""), "codigoIbge": codigo_ibge, "pagina": 1},
                    headers={"chave-api-dados": self._chave},
                )
            except httpx.TransportError as erro:
                motivo, espera, erro_final = type(erro).__name__, ESPERA_FALHA_TEMPORARIA_SEGUNDOS, FonteIndisponivel
            else:
                if resposta.status_code == 429:
                    motivo, espera, erro_final = "HTTP 429", _espera_retry_after(resposta), LimiteFonteExcedido
                elif resposta.status_code >= 500:
                    motivo, espera, erro_final = (
                        f"HTTP {resposta.status_code}",
                        ESPERA_FALHA_TEMPORARIA_SEGUNDOS,
                        FonteIndisponivel,
                    )
                else:
                    return resposta
            logger.warning(
                "Falha temporária no Portal (%s) codigoIbge=%s mes=%s tentativa=%s",
                motivo, codigo_ibge, mes, tentativa + 1,
            )
            if tentativa < self._max_novas_tentativas:
                await self._dormir(espera)
        raise erro_final()


def _espera_retry_after(resposta: httpx.Response) -> float:
    valor = resposta.headers.get("Retry-After", "")
    return float(valor) if valor.isdigit() else ESPERA_LIMITE_PADRAO_SEGUNDOS
