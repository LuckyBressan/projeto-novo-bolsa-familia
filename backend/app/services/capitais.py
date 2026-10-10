import asyncio
from dataclasses import dataclass, replace

from app.services.catalogos import Municipio, chave_nome
from app.services.indicadores import (
    FonteRegistros,
    Indicadores,
    ItemSerie,
    calcular_indicadores,
    calcular_serie,
    consultar_meses,
    falha_todas_entradas,
)


@dataclass(frozen=True)
class EntradaRanking:
    municipio: Municipio
    indicadores: Indicadores
    serie: list[ItemSerie]
    posicao_ranking: int | None = None


def ranquear(entradas: list[EntradaRanking], metrica: str) -> list[EntradaRanking]:
    disponiveis = sorted(
        (entrada for entrada in entradas if entrada.indicadores.status_dado == "disponivel"),
        key=lambda entrada: (-getattr(entrada.indicadores, metrica), chave_nome(entrada.municipio.nome)),
    )
    demais = sorted(
        (entrada for entrada in entradas if entrada.indicadores.status_dado != "disponivel"),
        key=lambda entrada: chave_nome(entrada.municipio.nome),
    )
    return [replace(entrada, posicao_ranking=posicao) for posicao, entrada in enumerate(disponiveis, start=1)] + demais


def posicao_referencia(referencia: EntradaRanking, ranking: list[EntradaRanking], metrica: str) -> int | None:
    if referencia.indicadores.status_dado != "disponivel":
        return None
    valor = getattr(referencia.indicadores, metrica)
    return 1 + sum(
        1
        for entrada in ranking
        if entrada.posicao_ranking is not None
        and entrada.municipio.codigo_ibge != referencia.municipio.codigo_ibge
        and getattr(entrada.indicadores, metrica) > valor
    )


@dataclass(frozen=True)
class ComparacaoCapitais:
    referencia: EntradaRanking
    posicao_referencia: int | None
    capitais: list[EntradaRanking]


async def comparar_capitais(
    fonte: FonteRegistros,
    referencia: Municipio,
    capitais: list[Municipio],
    meses: list[str],
    metrica: str,
) -> ComparacaoCapitais:
    municipios = [referencia, *capitais]
    resultados = await asyncio.gather(*(consultar_meses(fonte, municipio.codigo_ibge, meses) for municipio in municipios))
    falha = falha_todas_entradas(list(resultados))
    if falha is not None:
        raise falha
    entradas = [
        EntradaRanking(municipio, calcular_indicadores(resultados_municipio), calcular_serie(resultados_municipio))
        for municipio, resultados_municipio in zip(municipios, resultados)
    ]
    ranking = ranquear(entradas[1:], metrica)
    return ComparacaoCapitais(
        referencia=entradas[0],
        posicao_referencia=posicao_referencia(entradas[0], ranking, metrica),
        capitais=ranking,
    )
