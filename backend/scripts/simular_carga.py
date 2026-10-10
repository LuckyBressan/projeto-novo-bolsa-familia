import argparse
import asyncio
import json
import random
import sys
import time
from collections import Counter
from contextlib import suppress
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import median
from urllib.parse import urlencode

import httpx

PREFIXO = "/api/v1"
ROTA_CONSUMO = f"{PREFIXO}/diagnostico/consumo"
CODIGO_LIMITE_EXCEDIDO = "LIMITE_FONTE_EXCEDIDO"
SEM_RESPOSTA = "sem resposta"
CONEXOES_AMOSTRAGEM = 2
TIPOS = (
    "indicadores",
    "comparacao",
    "indicadores",
    "evolucao",
    "indicadores",
    "comparacao",
    "evolucao",
    "capitais",
)


@dataclass(frozen=True)
class Consulta:
    tipo: str
    caminho: str


def gerar_consultas(
    quantidade: int,
    codigos: list[str],
    meses_ano: dict[int, list[int]],
    semente: int,
    max_meses: int = 3,
) -> list[Consulta]:
    sorteio = random.Random(semente)
    return [
        _montar_consulta(TIPOS[indice % len(TIPOS)], codigos, _sortear_periodo(meses_ano, max_meses, sorteio), sorteio)
        for indice in range(quantidade)
    ]


def _sortear_periodo(meses_ano: dict[int, list[int]], max_meses: int, sorteio: random.Random) -> dict[str, int]:
    ano = sorteio.choice(sorted(meses_ano))
    mes_inicio = sorteio.choice(meses_ano[ano])
    mes_fim = min(mes_inicio + sorteio.randrange(max_meses), meses_ano[ano][-1])
    return {"ano": ano, "mes_inicio": mes_inicio, "mes_fim": mes_fim}


def _montar_consulta(tipo: str, codigos: list[str], periodo: dict[str, int], sorteio: random.Random) -> Consulta:
    if tipo == "indicadores":
        return Consulta(tipo, f"{PREFIXO}/municipios/{sorteio.choice(codigos)}/indicadores?{urlencode(periodo)}")
    if tipo == "capitais":
        parametros = {"codigo_ibge_referencia": sorteio.choice(codigos), **periodo}
        return Consulta(tipo, f"{PREFIXO}/capitais/comparacao?{urlencode(parametros)}")
    cidade_a, cidade_b = sorteio.sample(codigos, 2)
    parametros = {"codigo_ibge_a": cidade_a, "codigo_ibge_b": cidade_b, **periodo}
    rota = "comparacoes/municipios" if tipo == "comparacao" else "evolucao-mensal"
    return Consulta(tipo, f"{PREFIXO}/{rota}?{urlencode(parametros)}")


@dataclass(frozen=True)
class Resultado:
    consulta: Consulta
    http_status: int | None
    codigo_erro: str | None
    segundos: float


@dataclass(frozen=True)
class Resumo:
    consultas: int
    respostas: dict[str, int]
    erros_limite: int
    tempo_mediano: float
    tempo_maximo: float
    pico_chamadas_minuto: int
    limite_rpm: int
    aprovado: bool


def resumir(resultados: list[Resultado], amostras: list[int], limite_rpm: int) -> Resumo:
    respostas = Counter(
        str(resultado.http_status) if resultado.http_status is not None else SEM_RESPOSTA for resultado in resultados
    )
    erros_limite = sum(
        1
        for resultado in resultados
        if resultado.http_status == 429 or resultado.codigo_erro == CODIGO_LIMITE_EXCEDIDO
    )
    tempos = [resultado.segundos for resultado in resultados]
    pico = max(amostras, default=0)
    return Resumo(
        consultas=len(resultados),
        respostas=dict(sorted(respostas.items())),
        erros_limite=erros_limite,
        tempo_mediano=median(tempos),
        tempo_maximo=max(tempos),
        pico_chamadas_minuto=pico,
        limite_rpm=limite_rpm,
        aprovado=pico <= limite_rpm and erros_limite == 0,
    )


@dataclass(frozen=True)
class Execucao:
    resultados: list[Resultado]
    amostras: list[int]
    limite_rpm: int
    consumo_final: dict


async def executar(
    cliente: httpx.AsyncClient,
    consultas: list[Consulta],
    paralelas: int,
    intervalo_amostra: float = 1.0,
) -> Execucao:
    consumo_inicial = await _ler(cliente, ROTA_CONSUMO)
    amostras = [consumo_inicial["chamadas_ultimo_minuto"]]
    vagas = asyncio.Semaphore(paralelas)

    async def amostrar() -> None:
        while True:
            await asyncio.sleep(intervalo_amostra)
            amostras.append((await _ler(cliente, ROTA_CONSUMO))["chamadas_ultimo_minuto"])

    amostragem = asyncio.create_task(amostrar())
    try:
        resultados = await asyncio.gather(*(_consultar(cliente, consulta, vagas) for consulta in consultas))
    finally:
        amostragem.cancel()
        with suppress(asyncio.CancelledError):
            await amostragem
    consumo_final = await _ler(cliente, ROTA_CONSUMO)
    amostras.append(consumo_final["chamadas_ultimo_minuto"])
    return Execucao(list(resultados), amostras, consumo_inicial["limite_rpm_configurado"], consumo_final)


async def _ler(cliente: httpx.AsyncClient, caminho: str, parametros: dict | None = None) -> dict:
    resposta = await cliente.get(caminho, params=parametros)
    resposta.raise_for_status()
    return resposta.json()


async def _consultar(cliente: httpx.AsyncClient, consulta: Consulta, vagas: asyncio.Semaphore) -> Resultado:
    async with vagas:
        inicio = time.perf_counter()
        try:
            resposta = await cliente.get(consulta.caminho)
        except httpx.TransportError:
            return Resultado(consulta, None, None, time.perf_counter() - inicio)
        return Resultado(consulta, resposta.status_code, _codigo_erro(resposta), time.perf_counter() - inicio)


def _codigo_erro(resposta: httpx.Response) -> str | None:
    if resposta.is_success:
        return None
    try:
        return resposta.json()["erro"]["codigo"]
    except (ValueError, KeyError, TypeError):
        return None


async def simular(cliente: httpx.AsyncClient, quantidade: int, paralelas: int, semente: int) -> Execucao:
    periodos = await _ler(cliente, f"{PREFIXO}/periodos")
    estados = await _ler(cliente, f"{PREFIXO}/estados")
    codigos: list[str] = []
    for estado in estados["items"]:
        municipios = await _ler(cliente, f"{PREFIXO}/municipios", {"uf": estado["uf"]})
        codigos.extend(municipio["codigo_ibge"] for municipio in municipios["items"])
    meses_ano = {item["ano"]: item["meses"] for item in periodos["anos"]}
    consultas = gerar_consultas(quantidade, codigos, meses_ano, semente, periodos["max_meses_intervalo"])
    return await executar(cliente, consultas, paralelas)


def montar_relatorio(execucao: Execucao) -> dict:
    resumo = asdict(resumir(execucao.resultados, execucao.amostras, execucao.limite_rpm))
    resumo["tempo_mediano"] = round(resumo["tempo_mediano"], 3)
    resumo["tempo_maximo"] = round(resumo["tempo_maximo"], 3)
    return {
        "resumo": resumo,
        "amostras_chamadas_minuto": execucao.amostras,
        "consumo_final": execucao.consumo_final,
        "consultas": [
            {
                "tipo": resultado.consulta.tipo,
                "caminho": resultado.consulta.caminho,
                "http_status": resultado.http_status,
                "codigo_erro": resultado.codigo_erro,
                "segundos": round(resultado.segundos, 3),
            }
            for resultado in execucao.resultados
        ],
    }


def _ler_argumentos() -> argparse.Namespace:
    leitor = argparse.ArgumentParser(
        description="Dispara consultas variadas em paralelo contra a API e confere o consumo do Portal (RNF01)."
    )
    leitor.add_argument("--base-url", default="http://localhost:8000", help="Endereço da API (padrão: %(default)s)")
    leitor.add_argument("--consultas", type=int, default=30, help="Quantidade de consultas (padrão: %(default)s)")
    leitor.add_argument("--paralelas", type=int, default=20, help="Consultas simultâneas (padrão: %(default)s)")
    leitor.add_argument("--semente", type=int, default=1, help="Semente do sorteio; a mesma repete as consultas")
    leitor.add_argument(
        "--timeout",
        type=float,
        default=300,
        help="Segundos de espera por resposta; o limitador pode segurar uma consulta por mais de 1 minuto",
    )
    leitor.add_argument("--saida", type=Path, help="Arquivo JSON para guardar o relatório como evidência")
    return leitor.parse_args()


async def _rodar(argumentos: argparse.Namespace) -> Execucao:
    limites = httpx.Limits(max_connections=argumentos.paralelas + CONEXOES_AMOSTRAGEM)
    async with httpx.AsyncClient(base_url=argumentos.base_url, timeout=argumentos.timeout, limits=limites) as cliente:
        return await simular(cliente, argumentos.consultas, argumentos.paralelas, argumentos.semente)


def _imprimir(base_url: str, relatorio: dict) -> None:
    resumo, consumo = relatorio["resumo"], relatorio["consumo_final"]
    respostas = ", ".join(f"{status} × {quantidade}" for status, quantidade in resumo["respostas"].items())
    print(f"Simulação de carga em {base_url} (modo {'mock' if consumo['modo_mock'] else 'real'})")
    print(f"Consultas: {resumo['consultas']} | respostas: {respostas}")
    print(f"Tempo de resposta: mediana {resumo['tempo_mediano']} s | máximo {resumo['tempo_maximo']} s")
    print(
        f"Chamadas ao Portal desde o início da API: {consumo['chamadas_desde_inicio']}"
        f" | seguradas pelo limitador: {consumo['chamadas_bloqueadas_pelo_limitador']}"
        f" | respostas do cache: {consumo['cache']['hits']}"
    )
    print(f"Pico de chamadas por minuto: {resumo['pico_chamadas_minuto']} (limite {resumo['limite_rpm']})")
    print(f"Erros de limite devolvidos ao usuário: {resumo['erros_limite']}")
    print(f"Resultado: {'APROVADO' if resumo['aprovado'] else 'REPROVADO'}")


def main() -> None:
    argumentos = _ler_argumentos()
    execucao = asyncio.run(_rodar(argumentos))
    relatorio = {
        "executado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "parametros": {
            "base_url": argumentos.base_url,
            "consultas": argumentos.consultas,
            "paralelas": argumentos.paralelas,
            "semente": argumentos.semente,
        },
        **montar_relatorio(execucao),
    }
    _imprimir(argumentos.base_url, relatorio)
    if argumentos.saida is not None:
        argumentos.saida.parent.mkdir(parents=True, exist_ok=True)
        argumentos.saida.write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    sys.exit(0 if relatorio["resumo"]["aprovado"] else 1)


if __name__ == "__main__":
    main()
