from decimal import Decimal

import httpx
import pytest

from scripts.conferir_amostra import Caso, Leitura, Linha, ModoMockAtivo, conferir

pytestmark = pytest.mark.anyio

RIO_DO_SUL = Caso("4214805", "Rio do Sul", "SC", "2024-01")
BLUMENAU = Caso("4202404", "Blumenau", "SC", "2024-02")
MANAUS = Caso("1302603", "Manaus", "AM", "2023-03")
REGISTROS_PORTAL = {
    ("4214805", "202401"): [{"valor": 1043055.00, "quantidadeBeneficiados": 1525}],
    ("4202404", "202402"): [{"valor": 4500000.10, "quantidadeBeneficiados": 7033}],
}
INDICADORES_API = {
    "/api/v1/municipios/4214805/indicadores": (1043055.0, 1525.0, 683.97),
    "/api/v1/municipios/4202404/indicadores": (4500000.2, 7033.0, 639.84),
    "/api/v1/municipios/1302603/indicadores": (900.0, 3.0, 300.0),
}


def criar_portal(requisicoes: list[httpx.Request]) -> httpx.AsyncClient:
    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        chave = (requisicao.url.params["codigoIbge"], requisicao.url.params["mesAno"])
        if chave not in REGISTROS_PORTAL:
            return httpx.Response(503)
        return httpx.Response(200, json=REGISTROS_PORTAL[chave])

    return httpx.AsyncClient(base_url="https://portal.teste/api-de-dados", transport=httpx.MockTransport(responder))


def criar_api(requisicoes: list[httpx.Request], modo_mock: bool = False) -> httpx.AsyncClient:
    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        if requisicao.url.path == "/api/v1/diagnostico/consumo":
            return httpx.Response(200, json={"modo_mock": modo_mock})
        valor_total, beneficiarios, valor_medio = INDICADORES_API[requisicao.url.path]
        return httpx.Response(
            200,
            json={
                "indicadores": {
                    "status_dado": "disponivel",
                    "valor_total": valor_total,
                    "beneficiarios_media_mensal": beneficiarios,
                    "valor_medio_por_beneficiario": valor_medio,
                }
            },
        )

    return httpx.AsyncClient(base_url="http://api.teste", transport=httpx.MockTransport(responder))


async def test_confere_cada_caso_no_portal_e_na_api_interna():
    requisicoes_portal: list[httpx.Request] = []
    requisicoes_api: list[httpx.Request] = []
    async with criar_portal(requisicoes_portal) as portal, criar_api(requisicoes_api) as api:
        linhas = await conferir(portal, api, "chave-secreta", [RIO_DO_SUL, BLUMENAU, MANAUS])

    rio_do_sul = Leitura("disponivel", Decimal("1043055.0"), Decimal(1525), Decimal("683.97"))
    assert linhas == [
        Linha(RIO_DO_SUL, rio_do_sul, rio_do_sul, "ok"),
        Linha(
            BLUMENAU,
            Leitura("disponivel", Decimal("4500000.1"), Decimal(7033), Decimal("639.84")),
            Leitura("disponivel", Decimal("4500000.2"), Decimal(7033), Decimal("639.84")),
            "divergente",
        ),
        Linha(MANAUS, Leitura("falha"), Leitura("disponivel", Decimal(900), Decimal(3), Decimal(300)), "nao_conferido"),
    ]
    primeira = requisicoes_portal[0]
    assert primeira.url.path == "/api-de-dados/novo-bolsa-familia-por-municipio"
    assert dict(primeira.url.params) == {"mesAno": "202401", "codigoIbge": "4214805", "pagina": "1"}
    assert primeira.headers["chave-api-dados"] == "chave-secreta"
    consulta_api = next(item for item in requisicoes_api if item.url.path.endswith("/4214805/indicadores"))
    assert dict(consulta_api.url.params) == {"ano": "2024", "mes_inicio": "1"}


async def test_resposta_fora_do_formato_vira_falha_sem_interromper_a_conferencia():
    def responder_html(requisicao: httpx.Request) -> httpx.Response:
        if requisicao.url.path == "/api/v1/diagnostico/consumo":
            return httpx.Response(200, json={"modo_mock": False})
        return httpx.Response(200 if "portal" in requisicao.url.host else 502, text="<html>erro</html>")

    transporte = httpx.MockTransport(responder_html)
    async with (
        httpx.AsyncClient(base_url="https://portal.teste/api-de-dados", transport=transporte) as portal,
        httpx.AsyncClient(base_url="http://api.teste", transport=transporte) as api,
    ):
        linhas = await conferir(portal, api, "chave-secreta", [RIO_DO_SUL])

    assert linhas == [Linha(RIO_DO_SUL, Leitura("falha"), Leitura("falha"), "nao_conferido")]


async def test_api_no_modo_mock_nao_serve_de_evidencia():
    requisicoes_portal: list[httpx.Request] = []
    async with criar_portal(requisicoes_portal) as portal, criar_api([], modo_mock=True) as api:
        with pytest.raises(ModoMockAtivo):
            await conferir(portal, api, "chave-secreta", [RIO_DO_SUL])

    assert requisicoes_portal == []
