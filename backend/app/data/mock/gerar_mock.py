"""
Gerador determinístico do mock de dados — Comparativo do Novo Bolsa Família.

Gera, a partir de valores FICTÍCIOS:
  mock/catalogos/   -> estados, capitais e municípios do mock
  mock/portal/      -> registros no formato da API do Portal (usados pelo MockPortalClient)
  mock/api-v1/      -> respostas de exemplo de cada endpoint da API interna (contrato)

As regras de cálculo deste arquivo são a referência executável do documento
05-modelo-dados-e-indicadores.md. O back-end, em MODO_MOCK=true, deve devolver
exatamente o conteúdo de mock/api-v1/ (exceto o campo correlacao_id).

Uso:  python -I gerar_mock.py        (a partir da pasta mock/)
Sem dependências externas. Rodar de novo produz os mesmos arquivos.
"""

from __future__ import annotations

import json
import random
import unicodedata
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parent

PERIODO_MIN = (2023, 3)
PERIODO_MAX = (2026, 8)
MAX_MESES_INTERVALO = 3
LIMITE_RPM = 150
FONTE_MOCK = "mock"
CENTAVO = Decimal("0.01")

# --------------------------------------------------------------------------
# Catálogos (códigos IBGE reais; dígito verificador conferido)
# --------------------------------------------------------------------------
ESTADOS = [
    ("11", "RO", "Rondônia"), ("12", "AC", "Acre"), ("13", "AM", "Amazonas"),
    ("14", "RR", "Roraima"), ("15", "PA", "Pará"), ("16", "AP", "Amapá"),
    ("17", "TO", "Tocantins"), ("21", "MA", "Maranhão"), ("22", "PI", "Piauí"),
    ("23", "CE", "Ceará"), ("24", "RN", "Rio Grande do Norte"), ("25", "PB", "Paraíba"),
    ("26", "PE", "Pernambuco"), ("27", "AL", "Alagoas"), ("28", "SE", "Sergipe"),
    ("29", "BA", "Bahia"), ("31", "MG", "Minas Gerais"), ("32", "ES", "Espírito Santo"),
    ("33", "RJ", "Rio de Janeiro"), ("35", "SP", "São Paulo"), ("41", "PR", "Paraná"),
    ("42", "SC", "Santa Catarina"), ("43", "RS", "Rio Grande do Sul"),
    ("50", "MS", "Mato Grosso do Sul"), ("51", "MT", "Mato Grosso"), ("52", "GO", "Goiás"),
    ("53", "DF", "Distrito Federal"),
]
NOME_UF = {uf: nome for _, uf, nome in ESTADOS}

# (codigo_ibge, nome, uf, capital?, beneficiarios_base_ficticio, valor_medio_base_ficticio)
MUNICIPIOS = [
    ("1100205", "Porto Velho", "RO", True, 50_000, 668),
    ("1200401", "Rio Branco", "AC", True, 45_000, 681),
    ("1302603", "Manaus", "AM", True, 230_000, 702),
    ("1400100", "Boa Vista", "RR", True, 40_000, 690),
    ("1501402", "Belém", "PA", True, 160_000, 695),
    ("1600303", "Macapá", "AP", True, 60_000, 699),
    ("1721000", "Palmas", "TO", True, 20_000, 662),
    ("2111300", "São Luís", "MA", True, 150_000, 688),
    ("2211001", "Teresina", "PI", True, 110_000, 676),
    ("2304400", "Fortaleza", "CE", True, 330_000, 684),
    ("2408102", "Natal", "RN", True, 90_000, 671),
    ("2507507", "João Pessoa", "PB", True, 95_000, 673),
    ("2611606", "Recife", "PE", True, 210_000, 679),
    ("2704302", "Maceió", "AL", True, 120_000, 683),
    ("2800308", "Aracaju", "SE", True, 65_000, 674),
    ("2927408", "Salvador", "BA", True, 380_000, 677),
    ("3106200", "Belo Horizonte", "MG", True, 180_000, 655),
    ("3205309", "Vitória", "ES", True, 20_000, 649),
    ("3304557", "Rio de Janeiro", "RJ", True, 600_000, 661),
    ("3550308", "São Paulo", "SP", True, 690_000, 663),
    ("4106902", "Curitiba", "PR", True, 75_000, 652),
    ("4205407", "Florianópolis", "SC", True, 18_000, 647),
    ("4314902", "Porto Alegre", "RS", True, 95_000, 654),
    ("5002704", "Campo Grande", "MS", True, 55_000, 659),
    ("5103403", "Cuiabá", "MT", True, 50_000, 664),
    ("5208707", "Goiânia", "GO", True, 90_000, 657),
    ("5300108", "Brasília", "DF", True, 200_000, 666),
    ("4214805", "Rio do Sul", "SC", False, 1_600, 641),
    ("4202404", "Blumenau", "SC", False, 6_000, 645),
    ("4209102", "Joinville", "SC", False, 11_000, 650),
    ("3509502", "Campinas", "SP", False, 50_000, 658),
    ("2910800", "Feira de Santana", "BA", False, 85_000, 680),
]
MUN = {m[0]: m for m in MUNICIPIOS}

# --------------------------------------------------------------------------
# Cenários especiais (documentados em 09-mock-de-dados.md)
# --------------------------------------------------------------------------
SEM_REGISTRO = {  # a fonte responde 200 com lista vazia
    ("1400100", "2024-01"), ("1400100", "2024-02"), ("1400100", "2024-03"),  # Boa Vista
    ("4202404", "2023-11"),                                                  # Blumenau
}
FALHA_FONTE = {  # a fonte responde HTTP 503
    ("4209102", "2024-12"),                                                  # Joinville
}


# --------------------------------------------------------------------------
# Utilidades de período
# --------------------------------------------------------------------------
def chave_nome(nome: str) -> str:
    """Ordem alfabética do português: ignora acentos e maiúsculas."""
    return unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().casefold()


def mes_str(ano: int, mes: int) -> str:
    return f"{ano:04d}-{mes:02d}"


def todos_os_meses() -> list[tuple[int, int]]:
    out, (a, m) = [], PERIODO_MIN
    while (a, m) <= PERIODO_MAX:
        out.append((a, m))
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out


def meses_do_intervalo(ano: int, mes_inicio: int, mes_fim: int) -> list[str]:
    return [mes_str(ano, m) for m in range(mes_inicio, mes_fim + 1)]


def obj_periodo(ano: int, mes_inicio: int, mes_fim: int) -> dict:
    return {"ano": ano, "mes_inicio": mes_inicio, "mes_fim": mes_fim,
            "meses": meses_do_intervalo(ano, mes_inicio, mes_fim)}


def obj_municipio(cod: str) -> dict:
    c, nome, uf, *_ = MUN[cod]
    return {"codigo_ibge": c, "nome": nome, "uf": uf}


def money(x: Decimal) -> float:
    return float(x.quantize(CENTAVO, rounding=ROUND_HALF_UP))


# --------------------------------------------------------------------------
# "Fonte" fictícia: registros por município e mês
# --------------------------------------------------------------------------
def gerar_registros_portal() -> list[dict]:
    registros, ident = [], 900_000_000
    for cod, nome, uf, _cap, benef_base, medio_base in MUNICIPIOS:
        rng = random.Random(int(cod))
        benef = benef_base
        for ano, mes in todos_os_meses():
            benef = max(1, round(benef * (1 + rng.uniform(-0.015, 0.012))))
            if (cod, mes_str(ano, mes)) in SEM_REGISTRO:
                continue
            medio = Decimal(str(medio_base)) * Decimal(str(round(1 + rng.uniform(-0.01, 0.01), 4)))
            valor = (Decimal(benef) * medio).quantize(CENTAVO, rounding=ROUND_HALF_UP)
            ident += 1
            registros.append({
                "id": ident,
                "dataReferencia": f"{ano:04d}-{mes:02d}-01",
                "municipio": {
                    "codigoIBGE": cod,
                    "nomeIBGE": nome.upper(),
                    "uf": {"sigla": uf, "nome": NOME_UF[uf].upper()},
                },
                "tipo": {"descricao": "Novo Bolsa Família"},
                "valor": float(valor),
                "quantidadeBeneficiados": benef,
            })
    return registros


REGISTROS = gerar_registros_portal()
INDICE = {(r["municipio"]["codigoIBGE"], r["dataReferencia"][:7]): r for r in REGISTROS}


def consultar_fonte(cod: str, mes: str) -> dict:
    """Simula o MockPortalClient: retorna status do mês e o registro normalizado."""
    if (cod, mes) in FALHA_FONTE:
        return {"status": "fonte_indisponivel"}
    r = INDICE.get((cod, mes))
    if r is None:
        return {"status": "sem_dados"}
    return {"status": "disponivel", "valor": Decimal(str(r["valor"])),
            "beneficiarios": r["quantidadeBeneficiados"]}


# --------------------------------------------------------------------------
# Regras de negócio (referência do documento 05)
# --------------------------------------------------------------------------
INDICADORES_NULOS = {"valor_total": None, "beneficiarios_media_mensal": None,
                     "valor_medio_por_beneficiario": None}


def calcular_indicadores(cod: str, meses: list[str]) -> dict:
    """Cards do período (Opção A). Beneficiários = média mensal dos meses com dados."""
    consultas = [consultar_fonte(cod, m) for m in meses]
    base = {"meses_solicitados": len(meses)}
    if any(c["status"] == "fonte_indisponivel" for c in consultas):
        return {"status_dado": "fonte_indisponivel", **base, "meses_com_dados": None, **INDICADORES_NULOS}
    validos = [c for c in consultas if c["status"] == "disponivel"]
    if not validos:
        return {"status_dado": "sem_dados", **base, "meses_com_dados": 0, **INDICADORES_NULOS}
    soma_valor = sum((c["valor"] for c in validos), Decimal(0))
    soma_benef = sum(c["beneficiarios"] for c in validos)
    media_benef = Decimal(soma_benef) / Decimal(len(validos))
    valor_medio = soma_valor / Decimal(soma_benef) if soma_benef > 0 else None
    return {
        "status_dado": "disponivel" if len(validos) == len(meses) else "parcial",
        **base,
        "meses_com_dados": len(validos),
        "valor_total": money(soma_valor),
        "beneficiarios_media_mensal": money(media_benef),
        "valor_medio_por_beneficiario": money(valor_medio) if valor_medio is not None else None,
    }


def calcular_serie(cod: str, meses: list[str]) -> list[dict]:
    serie, anterior = [], None
    for m in meses:
        c = consultar_fonte(cod, m)
        if c["status"] == "disponivel":
            b = c["beneficiarios"]
            item = {
                "mes": m, "status_dado": "disponivel",
                "valor_total": money(c["valor"]),
                "beneficiarios": b,
                "valor_medio_por_beneficiario": money(c["valor"] / Decimal(b)) if b > 0 else None,
                "variacao_beneficiarios_absoluta": (b - anterior) if anterior is not None else None,
            }
            anterior = b
        else:
            item = {"mes": m, "status_dado": c["status"], "valor_total": None, "beneficiarios": None,
                    "valor_medio_por_beneficiario": None, "variacao_beneficiarios_absoluta": None}
            anterior = None  # não calcular variação atravessando lacuna
        serie.append(item)
    return serie


METRICAS = ("valor_total", "beneficiarios_media_mensal", "valor_medio_por_beneficiario")


def comparar_capitais(ref: str, ano: int, mi: int, mf: int, ufs: list[str] | None, metrica: str) -> dict:
    meses = meses_do_intervalo(ano, mi, mf)
    caps = [m for m in MUNICIPIOS if m[3] and (ufs is None or m[2] in ufs)]
    entradas = []
    for cod, nome, *_ in caps:
        entradas.append({"municipio": obj_municipio(cod), "indicadores": calcular_indicadores(cod, meses),
                         "meses": calcular_serie(cod, meses), "posicao_ranking": None})
    ranqueaveis = sorted(
        (e for e in entradas if e["indicadores"]["status_dado"] == "disponivel"),
        key=lambda e: (-e["indicadores"][metrica], chave_nome(e["municipio"]["nome"])),
    )
    for i, e in enumerate(ranqueaveis, start=1):
        e["posicao_ranking"] = i
    nao_ranq = sorted((e for e in entradas if e["posicao_ranking"] is None), key=lambda e: chave_nome(e["municipio"]["nome"]))
    ind_ref = calcular_indicadores(ref, meses)
    pos_ref = None
    if ind_ref["status_dado"] == "disponivel":
        pos_ref = 1 + sum(1 for e in ranqueaveis
                          if e["municipio"]["codigo_ibge"] != ref and e["indicadores"][metrica] > ind_ref[metrica])
    return {
        "fonte": FONTE_MOCK,
        "periodo": obj_periodo(ano, mi, mf),
        "metrica_ranking": metrica,
        "filtro_capitais": ufs,
        "total_capitais": len(entradas),
        "referencia": {"municipio": obj_municipio(ref), "indicadores": ind_ref,
                       "meses": calcular_serie(ref, meses), "posicao_entre_capitais": pos_ref},
        "capitais": ranqueaveis + nao_ranq,
    }


# --------------------------------------------------------------------------
# Respostas da API interna
# --------------------------------------------------------------------------
def r_indicadores(cod, ano, mi, mf):
    return {"fonte": FONTE_MOCK, "municipio": obj_municipio(cod), "periodo": obj_periodo(ano, mi, mf),
            "indicadores": calcular_indicadores(cod, meses_do_intervalo(ano, mi, mf))}


def r_comparacao(a, b, ano, mi, mf):
    meses = meses_do_intervalo(ano, mi, mf)
    return {"fonte": FONTE_MOCK, "periodo": obj_periodo(ano, mi, mf),
            "municipios": [{"municipio": obj_municipio(c), "indicadores": calcular_indicadores(c, meses)}
                           for c in (a, b)]}


def r_evolucao(a, b, ano, mi, mf):
    meses = meses_do_intervalo(ano, mi, mf)
    return {"fonte": FONTE_MOCK, "periodo": obj_periodo(ano, mi, mf),
            "series": [{"municipio": obj_municipio(c), "meses": calcular_serie(c, meses)} for c in (a, b)]}


def erro(codigo, mensagem, detalhes=None):
    corpo = {"codigo": codigo, "mensagem": mensagem}
    if detalhes:
        corpo["detalhes"] = detalhes
    corpo["correlacao_id"] = "exemplo-0000"
    return {"erro": corpo}


def anos_disponiveis():
    anos = {}
    for a, m in todos_os_meses():
        anos.setdefault(a, []).append(m)
    return [{"ano": a, "meses": ms} for a, ms in anos.items()]


def montar_exemplos() -> list[tuple[str, int, str, dict]]:
    """(arquivo, http_status, rota de exemplo, corpo)"""
    q = "/api/v1"
    ex = [
        ("health.json", 200, f"{q}/health",
         {"status": "ok", "service": "backend", "modo_mock": True}),
        ("periodos.json", 200, f"{q}/periodos",
         {"periodo_min": mes_str(*PERIODO_MIN), "periodo_max": mes_str(*PERIODO_MAX),
          "max_meses_intervalo": MAX_MESES_INTERVALO, "anos": anos_disponiveis()}),
        ("estados.json", 200, f"{q}/estados",
         {"items": [{"codigo_uf": c, "uf": uf, "nome": n} for c, uf, n in sorted(ESTADOS, key=lambda e: chave_nome(e[2]))],
          "total": len(ESTADOS)}),
    ]
    sc = sorted((m for m in MUNICIPIOS if m[2] == "SC"), key=lambda m: chave_nome(m[1]))
    ex.append(("municipios_uf-SC.json", 200, f"{q}/municipios?uf=SC",
               {"items": [obj_municipio(m[0]) for m in sc], "total": len(sc)}))
    blu = [m for m in sc if m[1].lower().startswith("blu")]
    ex.append(("municipios_uf-SC_busca-blu.json", 200, f"{q}/municipios?uf=SC&busca=blu",
               {"items": [obj_municipio(m[0]) for m in blu], "total": len(blu)}))

    ex += [
        ("indicadores_4214805_2024-01a03.json", 200,
         f"{q}/municipios/4214805/indicadores?ano=2024&mes_inicio=1&mes_fim=3",
         r_indicadores("4214805", 2024, 1, 3)),
        ("indicadores_4214805_2024-02.json", 200,
         f"{q}/municipios/4214805/indicadores?ano=2024&mes_inicio=2&mes_fim=2",
         r_indicadores("4214805", 2024, 2, 2)),
        ("comparacao_4214805-x-4202404_2024-01a03.json", 200,
         f"{q}/comparacoes/municipios?codigo_ibge_a=4214805&codigo_ibge_b=4202404&ano=2024&mes_inicio=1&mes_fim=3",
         r_comparacao("4214805", "4202404", 2024, 1, 3)),
        ("comparacao_4202404-x-4209102_2023-10a12_parcial.json", 200,
         f"{q}/comparacoes/municipios?codigo_ibge_a=4202404&codigo_ibge_b=4209102&ano=2023&mes_inicio=10&mes_fim=12",
         r_comparacao("4202404", "4209102", 2023, 10, 12)),
        ("comparacao_4209102-x-4214805_2024-10a12_falha-fonte.json", 200,
         f"{q}/comparacoes/municipios?codigo_ibge_a=4209102&codigo_ibge_b=4214805&ano=2024&mes_inicio=10&mes_fim=12",
         r_comparacao("4209102", "4214805", 2024, 10, 12)),
        ("evolucao_4214805-x-4202404_2024-01a03.json", 200,
         f"{q}/evolucao-mensal?codigo_ibge_a=4214805&codigo_ibge_b=4202404&ano=2024&mes_inicio=1&mes_fim=3",
         r_evolucao("4214805", "4202404", 2024, 1, 3)),
        ("evolucao_4202404-x-4209102_2023-10a12_lacuna.json", 200,
         f"{q}/evolucao-mensal?codigo_ibge_a=4202404&codigo_ibge_b=4209102&ano=2023&mes_inicio=10&mes_fim=12",
         r_evolucao("4202404", "4209102", 2023, 10, 12)),
        ("capitais_ref-4214805_2024-01a03_todas.json", 200,
         f"{q}/capitais/comparacao?codigo_ibge_referencia=4214805&ano=2024&mes_inicio=1&mes_fim=3",
         comparar_capitais("4214805", 2024, 1, 3, None, "valor_total")),
        ("capitais_ref-4214805_2024-01a03_SC-PR-RS_valor-medio.json", 200,
         f"{q}/capitais/comparacao?codigo_ibge_referencia=4214805&ano=2024&mes_inicio=1&mes_fim=3"
         "&capitais=SC,PR,RS&metrica=valor_medio_por_beneficiario",
         comparar_capitais("4214805", 2024, 1, 3, ["SC", "PR", "RS"], "valor_medio_por_beneficiario")),
        ("diagnostico_consumo.json", 200, f"{q}/diagnostico/consumo",
         {"modo_mock": True, "limite_rpm_configurado": LIMITE_RPM, "chamadas_ultimo_minuto": 87,
          "chamadas_desde_inicio": 412, "chamadas_bloqueadas_pelo_limitador": 0,
          "cache": {"itens": 96, "hits": 655, "misses": 412, "ttl_segundos": 3600},
          "iniciado_em": "2026-10-09T08:00:00-03:00"}),
        # ---- erros
        ("erro_periodo-fora-do-intervalo.json", 422,
         f"{q}/municipios/4214805/indicadores?ano=2023&mes_inicio=1&mes_fim=2",
         erro("PERIODO_INVALIDO",
              f"O período deve estar entre {mes_str(*PERIODO_MIN)} e {mes_str(*PERIODO_MAX)}.",
              {"periodo_min": mes_str(*PERIODO_MIN), "periodo_max": mes_str(*PERIODO_MAX)})),
        ("erro_intervalo-maior-que-3-meses.json", 422,
         f"{q}/evolucao-mensal?codigo_ibge_a=4214805&codigo_ibge_b=4202404&ano=2024&mes_inicio=1&mes_fim=6",
         erro("PERIODO_INVALIDO", "O intervalo deve ter no máximo 3 meses, dentro do mesmo ano.",
              {"max_meses_intervalo": 3})),
        ("erro_municipio-invalido.json", 404,
         f"{q}/municipios/9999999/indicadores?ano=2024&mes_inicio=1&mes_fim=1",
         erro("MUNICIPIO_INVALIDO", "Município não encontrado no catálogo.", {"codigo_ibge": "9999999"})),
        ("erro_estado-invalido.json", 422, f"{q}/municipios?uf=XX",
         erro("ESTADO_INVALIDO", "UF inexistente.", {"uf": "XX"})),
        ("erro_fonte-indisponivel.json", 503,
         f"{q}/municipios/4209102/indicadores?ano=2024&mes_inicio=12&mes_fim=12",
         erro("FONTE_INDISPONIVEL", "Não foi possível consultar os dados oficiais neste momento.")),
    ]
    return ex


def escrever(caminho: Path, obj) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    escrever(BASE / "catalogos" / "estados.json",
             [{"codigo_uf": c, "uf": uf, "nome": n} for c, uf, n in ESTADOS])
    escrever(BASE / "catalogos" / "capitais.json",
             [obj_municipio(m[0]) for m in MUNICIPIOS if m[3]])
    escrever(BASE / "catalogos" / "municipios-mock.json",
             [{**obj_municipio(m[0]), "capital": m[3]} for m in MUNICIPIOS])
    escrever(BASE / "portal" / "novo-bolsa-familia-por-municipio.json", REGISTROS)
    escrever(BASE / "portal" / "cenarios.json", {
        "observacao": "Valores fictícios. Combinações sem registro retornam lista vazia; falhas retornam HTTP 503.",
        "sem_registro": [{"codigoIbge": c, "mes": m} for c, m in sorted(SEM_REGISTRO)],
        "falha_fonte_http_503": [{"codigoIbge": c, "mes": m} for c, m in sorted(FALHA_FONTE)],
    })
    rotas = []
    for arquivo, status, rota, corpo in montar_exemplos():
        escrever(BASE / "api-v1" / arquivo, corpo)
        rotas.append({"rota": rota, "http_status": status, "arquivo": arquivo})
    escrever(BASE / "api-v1" / "_rotas.json", rotas)
    print(f"{len(REGISTROS)} registros do portal; {len(rotas)} respostas de exemplo geradas.")


if __name__ == "__main__":
    main()
