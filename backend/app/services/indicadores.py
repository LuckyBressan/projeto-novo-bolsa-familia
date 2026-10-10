import asyncio
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from app.core.errors import ErroApi, ErroFonte
from app.integrations.portal_transparencia import RegistroBeneficio

CENTAVO = Decimal("0.01")


@dataclass(frozen=True)
class TotaisMes:
    valor: Decimal
    beneficiarios: int


@dataclass(frozen=True)
class ResultadoMes:
    mes: str
    totais: TotaisMes | None = None
    erro: ErroApi | None = None


@dataclass(frozen=True)
class Indicadores:
    status_dado: str
    meses_solicitados: int
    meses_com_dados: int | None
    valor_total: Decimal | None
    beneficiarios_media_mensal: Decimal | None
    valor_medio_por_beneficiario: Decimal | None


def consolidar_mes(registros: list[RegistroBeneficio]) -> TotaisMes | None:
    if not registros:
        return None
    return TotaisMes(
        valor=sum((registro.valor for registro in registros), Decimal(0)),
        beneficiarios=sum(registro.quantidade_beneficiados for registro in registros),
    )


class FonteRegistros(Protocol):
    async def buscar(self, codigo_ibge: str, mes: str) -> list[RegistroBeneficio]: ...


async def consultar_meses(fonte: FonteRegistros, codigo_ibge: str, meses: list[str]) -> list[ResultadoMes]:
    return list(await asyncio.gather(*(_consultar_mes(fonte, codigo_ibge, mes) for mes in meses)))


async def _consultar_mes(fonte: FonteRegistros, codigo_ibge: str, mes: str) -> ResultadoMes:
    try:
        registros = await fonte.buscar(codigo_ibge, mes)
    except ErroFonte as erro:
        return ResultadoMes(mes, erro=erro)
    return ResultadoMes(mes, totais=consolidar_mes(registros))


def arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def calcular_indicadores(resultados: list[ResultadoMes]) -> Indicadores:
    if any(resultado.erro is not None for resultado in resultados):
        return Indicadores("fonte_indisponivel", len(resultados), None, None, None, None)
    totais = [resultado.totais for resultado in resultados if resultado.totais is not None]
    if not totais:
        return Indicadores("sem_dados", len(resultados), 0, None, None, None)
    soma_valor = sum((total.valor for total in totais), Decimal(0))
    soma_beneficiarios = sum(total.beneficiarios for total in totais)
    return Indicadores(
        status_dado="disponivel" if len(totais) == len(resultados) else "parcial",
        meses_solicitados=len(resultados),
        meses_com_dados=len(totais),
        valor_total=arredondar(soma_valor),
        beneficiarios_media_mensal=arredondar(Decimal(soma_beneficiarios) / len(totais)),
        valor_medio_por_beneficiario=arredondar(soma_valor / soma_beneficiarios) if soma_beneficiarios else None,
    )


def primeira_falha(resultados: list[ResultadoMes]) -> ErroApi | None:
    return next((resultado.erro for resultado in resultados if resultado.erro is not None), None)


def falha_todas_entradas(entradas: list[list[ResultadoMes]]) -> ErroApi | None:
    falhas = [primeira_falha(resultados) for resultados in entradas]
    return falhas[0] if falhas and all(falha is not None for falha in falhas) else None


@dataclass(frozen=True)
class ItemSerie:
    mes: str
    status_dado: str
    valor_total: Decimal | None
    beneficiarios: int | None
    valor_medio_por_beneficiario: Decimal | None
    variacao_beneficiarios_absoluta: int | None


def calcular_serie(resultados: list[ResultadoMes]) -> list[ItemSerie]:
    serie: list[ItemSerie] = []
    anterior: int | None = None
    for resultado in resultados:
        totais = resultado.totais
        if totais is None:
            status = "fonte_indisponivel" if resultado.erro is not None else "sem_dados"
            serie.append(ItemSerie(resultado.mes, status, None, None, None, None))
            anterior = None
            continue
        serie.append(
            ItemSerie(
                mes=resultado.mes,
                status_dado="disponivel",
                valor_total=arredondar(totais.valor),
                beneficiarios=totais.beneficiarios,
                valor_medio_por_beneficiario=(
                    arredondar(totais.valor / totais.beneficiarios) if totais.beneficiarios else None
                ),
                variacao_beneficiarios_absoluta=totais.beneficiarios - anterior if anterior is not None else None,
            )
        )
        anterior = totais.beneficiarios
    return serie


def falha_todos_meses(entradas: list[list[ResultadoMes]]) -> ErroApi | None:
    resultados = [resultado for entrada in entradas for resultado in entrada]
    if resultados and all(resultado.erro is not None for resultado in resultados):
        return resultados[0].erro
    return None
