import argparse
import asyncio
import csv
import io
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import httpx

CENTAVO = Decimal("0.01")
SEPARADOR = ";"
COLUNAS_CASO = ("codigo_ibge", "municipio", "uf", "mes")
COLUNAS_LEITURA = ("situacao", "valor_total", "beneficiarios", "valor_medio")
PORTAL_URL_PADRAO = "https://api.portaldatransparencia.gov.br/api-de-dados"
VARIAVEL_CHAVE = "PORTAL_TRANSPARENCIA_API_KEY"
ENDPOINT_PORTAL = "/novo-bolsa-familia-por-municipio"
CABECALHO_CHAVE = "chave-api-dados"


@dataclass(frozen=True)
class Leitura:
    situacao: str
    valor_total: Decimal | None = None
    beneficiarios: Decimal | None = None
    valor_medio: Decimal | None = None


def ler_portal(registros: list[dict]) -> Leitura:
    if not registros:
        return Leitura("sem_dados")
    valor_total = sum((Decimal(str(registro["valor"])) for registro in registros), Decimal(0))
    beneficiarios = Decimal(sum(int(registro["quantidadeBeneficiados"]) for registro in registros))
    valor_medio = (valor_total / beneficiarios).quantize(CENTAVO, rounding=ROUND_HALF_UP) if beneficiarios else None
    return Leitura("disponivel", valor_total, beneficiarios, valor_medio)


def ler_api(http_status: int, corpo: dict) -> Leitura:
    if http_status != 200:
        return Leitura("falha")
    indicadores = corpo["indicadores"]
    if indicadores["status_dado"] == "sem_dados":
        return Leitura("sem_dados")
    if indicadores["status_dado"] != "disponivel":
        return Leitura("falha")
    return Leitura(
        "disponivel",
        indicadores["valor_total"],
        indicadores["beneficiarios_media_mensal"],
        indicadores["valor_medio_por_beneficiario"],
    )


def comparar(portal: Leitura, api: Leitura) -> str:
    if "falha" in (portal.situacao, api.situacao):
        return "nao_conferido"
    return "ok" if portal == api else "divergente"


@dataclass(frozen=True)
class Caso:
    codigo_ibge: str
    municipio: str
    uf: str
    mes: str


@dataclass(frozen=True)
class Linha:
    caso: Caso
    portal: Leitura
    api: Leitura
    resultado: str


class ModoMockAtivo(Exception):
    pass


async def conferir(portal: httpx.AsyncClient, api: httpx.AsyncClient, chave: str, casos: list[Caso]) -> list[Linha]:
    consumo = await api.get("/api/v1/diagnostico/consumo")
    consumo.raise_for_status()
    if consumo.json()["modo_mock"]:
        raise ModoMockAtivo()
    linhas: list[Linha] = []
    for caso in casos:
        leitura_portal = await _consultar_portal(portal, chave, caso)
        leitura_api = await _consultar_api(api, caso)
        linhas.append(Linha(caso, leitura_portal, leitura_api, comparar(leitura_portal, leitura_api)))
    return linhas


async def _consultar_portal(portal: httpx.AsyncClient, chave: str, caso: Caso) -> Leitura:
    try:
        resposta = await portal.get(
            ENDPOINT_PORTAL,
            params={"mesAno": caso.mes.replace("-", ""), "codigoIbge": caso.codigo_ibge, "pagina": 1},
            headers={CABECALHO_CHAVE: chave},
        )
    except httpx.TransportError:
        return Leitura("falha")
    if resposta.status_code != 200:
        return Leitura("falha")
    try:
        return ler_portal(_decodificar(resposta))
    except (ValueError, KeyError, TypeError):
        return Leitura("falha")


async def _consultar_api(api: httpx.AsyncClient, caso: Caso) -> Leitura:
    ano, mes = caso.mes.split("-")
    try:
        resposta = await api.get(
            f"/api/v1/municipios/{caso.codigo_ibge}/indicadores",
            params={"ano": int(ano), "mes_inicio": int(mes)},
        )
    except httpx.TransportError:
        return Leitura("falha")
    try:
        return ler_api(resposta.status_code, _decodificar(resposta))
    except (ValueError, KeyError, TypeError):
        return Leitura("falha")


def _decodificar(resposta: httpx.Response):
    return json.loads(resposta.content, parse_float=Decimal)


def ler_casos(planilha: str) -> list[Caso]:
    leitor = csv.DictReader(io.StringIO(planilha), delimiter=SEPARADOR)
    return [Caso(linha["codigo_ibge"], linha["municipio"], linha["uf"], linha["mes"]) for linha in leitor]


def montar_planilha(linhas: list[Linha]) -> str:
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=SEPARADOR, lineterminator="\n")
    escritor.writerow(
        [
            *COLUNAS_CASO,
            *(f"portal_{coluna}" for coluna in COLUNAS_LEITURA),
            *(f"api_{coluna}" for coluna in COLUNAS_LEITURA),
            "resultado",
        ]
    )
    for linha in linhas:
        caso = linha.caso
        escritor.writerow(
            [
                caso.codigo_ibge,
                caso.municipio,
                caso.uf,
                caso.mes,
                *_celulas(linha.portal),
                *_celulas(linha.api),
                linha.resultado,
            ]
        )
    return saida.getvalue()


def _celulas(leitura: Leitura) -> list[str]:
    return [
        leitura.situacao,
        _formatar(leitura.valor_total, casas=2),
        _formatar(leitura.beneficiarios, casas=0),
        _formatar(leitura.valor_medio, casas=2),
    ]


def _formatar(valor: Decimal | None, casas: int) -> str:
    return "" if valor is None else f"{valor:.{casas}f}".replace(".", ",")


def _ler_argumentos() -> argparse.Namespace:
    leitor = argparse.ArgumentParser(
        description="Confere a amostra de homologação: Portal da Transparência direto contra a API interna, mês a mês."
    )
    leitor.add_argument("--base-url", default="http://localhost:8000", help="Endereço da API (padrão: %(default)s)")
    leitor.add_argument(
        "--portal-url",
        default=os.environ.get("PORTAL_API_BASE_URL", PORTAL_URL_PADRAO),
        help="Endereço da API do Portal (padrão: %(default)s)",
    )
    leitor.add_argument(
        "--amostra",
        type=Path,
        default=Path(__file__).with_name("amostra_homologacao.csv"),
        help="Planilha com os casos: codigo_ibge;municipio;uf;mes (padrão: %(default)s)",
    )
    leitor.add_argument(
        "--saida",
        type=Path,
        default=Path("evidencias/amostra-homologacao.csv"),
        help="Planilha preenchida com os valores das duas fontes (padrão: %(default)s)",
    )
    leitor.add_argument("--timeout", type=float, default=120, help="Segundos de espera por resposta")
    return leitor.parse_args()


async def _rodar(argumentos: argparse.Namespace, chave: str, casos: list[Caso]) -> list[Linha]:
    async with (
        httpx.AsyncClient(base_url=argumentos.portal_url, timeout=argumentos.timeout) as portal,
        httpx.AsyncClient(base_url=argumentos.base_url, timeout=argumentos.timeout) as api,
    ):
        return await conferir(portal, api, chave, casos)


def main() -> None:
    argumentos = _ler_argumentos()
    chave = os.environ.get(VARIAVEL_CHAVE)
    if not chave:
        sys.exit(f"Defina {VARIAVEL_CHAVE} para consultar o Portal.")
    casos = ler_casos(argumentos.amostra.read_text(encoding="utf-8-sig"))
    try:
        linhas = asyncio.run(_rodar(argumentos, chave, casos))
    except ModoMockAtivo:
        sys.exit("A API está com MODO_MOCK=true: números do mock não valem como evidência de homologação.")
    argumentos.saida.parent.mkdir(parents=True, exist_ok=True)
    argumentos.saida.write_text(montar_planilha(linhas), encoding="utf-8-sig", newline="\n")
    contagem = Counter(linha.resultado for linha in linhas)
    for linha in linhas:
        if linha.resultado != "ok":
            print(f"{linha.resultado}: {linha.caso.municipio}/{linha.caso.uf} {linha.caso.mes}")
    print(
        f"Casos: {len(linhas)} | ok: {contagem['ok']} | divergentes: {contagem['divergente']}"
        f" | não conferidos: {contagem['nao_conferido']}"
    )
    print(f"Planilha gravada em {argumentos.saida}")
    sys.exit(0 if contagem["ok"] == len(linhas) else 1)


if __name__ == "__main__":
    main()
