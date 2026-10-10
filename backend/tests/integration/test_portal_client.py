from decimal import Decimal

import httpx
import pytest

from app.core.errors import FonteIndisponivel, LimiteFonteExcedido, RespostaFonteInvalida
from app.integrations.portal_transparencia import PortalClient, RegistroBeneficio

pytestmark = pytest.mark.anyio

BASE_URL = "https://portal.teste/api-de-dados"
REGISTRO_PORTAL = {
    "id": 101708076,
    "dataReferencia": "2024-01-01",
    "municipio": {
        "codigoIBGE": "4214805",
        "nomeIBGE": "RIO DO SUL",
        "uf": {"sigla": "SC", "nome": "SANTA CATARINA"},
    },
    "tipo": {"descricao": "Novo Bolsa Família"},
    "valor": 1015943.27,
    "quantidadeBeneficiados": 1574,
}


def criar_cliente(responder, relogio=None) -> PortalClient:
    http = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(responder))
    if relogio is None:
        return PortalClient(http, chave="chave-secreta")
    return PortalClient(http, chave="chave-secreta", dormir=relogio.dormir)


async def test_resposta_valida_vira_registro_interno():
    requisicoes: list[httpx.Request] = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(200, json=[REGISTRO_PORTAL])

    registros = await criar_cliente(responder).buscar("4214805", "2024-01")

    assert registros == [
        RegistroBeneficio(
            codigo_ibge="4214805",
            municipio_nome="RIO DO SUL",
            uf="SC",
            mes="2024-01",
            valor=Decimal("1015943.27"),
            quantidade_beneficiados=1574,
            tipo_beneficio="Novo Bolsa Família",
            id_fonte=101708076,
        )
    ]
    requisicao = requisicoes[0]
    assert requisicao.url.path == "/api-de-dados/novo-bolsa-familia-por-municipio"
    assert dict(requisicao.url.params) == {"mesAno": "202401", "codigoIbge": "4214805", "pagina": "1"}
    assert requisicao.headers["chave-api-dados"] == "chave-secreta"


def falhar_503(requisicao: httpx.Request) -> httpx.Response:
    return httpx.Response(503)


def falhar_timeout(requisicao: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("timeout", request=requisicao)


def falhar_conexao(requisicao: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("sem conexão", request=requisicao)


@pytest.mark.parametrize("falha", [falhar_503, falhar_timeout, falhar_conexao])
async def test_falha_temporaria_tenta_mais_uma_vez_e_depois_indica_fonte_indisponivel(relogio, falha):
    tentativas = 0

    def responder(requisicao: httpx.Request) -> httpx.Response:
        nonlocal tentativas
        tentativas += 1
        return falha(requisicao)

    with pytest.raises(FonteIndisponivel):
        await criar_cliente(responder, relogio).buscar("4214805", "2024-01")

    assert tentativas == 2
    assert relogio.esperas == [1]


@pytest.mark.parametrize(("cabecalhos", "espera"), [({"Retry-After": "7"}, 7), ({}, 5)])
async def test_limite_excedido_espera_e_tenta_mais_uma_vez(relogio, cabecalhos, espera):
    tentativas = 0

    def responder(requisicao: httpx.Request) -> httpx.Response:
        nonlocal tentativas
        tentativas += 1
        return httpx.Response(429, headers=cabecalhos)

    with pytest.raises(LimiteFonteExcedido):
        await criar_cliente(responder, relogio).buscar("4214805", "2024-01")

    assert tentativas == 2
    assert relogio.esperas == [espera]


@pytest.mark.parametrize("status", [400, 401, 403])
async def test_erro_parametro_ou_credencial_nao_repete_chamada(relogio, status):
    tentativas = 0

    def responder(requisicao: httpx.Request) -> httpx.Response:
        nonlocal tentativas
        tentativas += 1
        return httpx.Response(status)

    with pytest.raises(FonteIndisponivel):
        await criar_cliente(responder, relogio).buscar("4214805", "2024-01")

    assert tentativas == 1
    assert relogio.esperas == []


@pytest.mark.parametrize(
    "conteudo",
    [b"<html>manutencao</html>", b'{"erro": "inesperado"}', b'[{"id": 1, "valor": 10.5}]'],
    ids=["nao-json", "objeto-em-vez-de-lista", "registro-sem-campos"],
)
async def test_resposta_fora_formato_indica_resposta_invalida_sem_repetir(relogio, conteudo):
    tentativas = 0

    def responder(requisicao: httpx.Request) -> httpx.Response:
        nonlocal tentativas
        tentativas += 1
        return httpx.Response(200, content=conteudo)

    with pytest.raises(RespostaFonteInvalida):
        await criar_cliente(responder, relogio).buscar("4214805", "2024-01")

    assert tentativas == 1


async def test_mais_de_um_registro_municipio_mes_gera_aviso_d02(caplog):
    def responder(requisicao: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[REGISTRO_PORTAL, {**REGISTRO_PORTAL, "id": 101708077}])

    with caplog.at_level("WARNING"):
        registros = await criar_cliente(responder).buscar("4214805", "2024-01")

    assert len(registros) == 2
    assert "D02" in caplog.text
    assert "chave-secreta" not in caplog.text
