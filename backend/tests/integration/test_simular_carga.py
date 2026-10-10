import asyncio

import httpx
import pytest

from app.main import app
from scripts.simular_carga import Consulta, Resultado, executar, resumir, simular

pytestmark = pytest.mark.anyio

CONSULTAS = [
    Consulta("indicadores", "/api/v1/municipios/4214805/indicadores?ano=2024&mes_inicio=1&mes_fim=1"),
    Consulta("indicadores", "/api/v1/municipios/4209102/indicadores?ano=2024&mes_inicio=12&mes_fim=12"),
    Consulta("evolucao", "/api/v1/evolucao-mensal?codigo_ibge_a=4214805&codigo_ibge_b=4202404&ano=2024&mes_inicio=1&mes_fim=3"),
    Consulta("capitais", "/api/v1/capitais/comparacao?codigo_ibge_referencia=4214805&ano=2024&mes_inicio=1&mes_fim=1"),
]


class ApiFalsa:
    def __init__(self):
        self.simultaneas = 0
        self.pico_simultaneas = 0
        self.chamadas_portal = 0

    async def responder(self, requisicao: httpx.Request) -> httpx.Response:
        if requisicao.url.path == "/api/v1/diagnostico/consumo":
            return httpx.Response(
                200, json={"limite_rpm_configurado": 150, "chamadas_ultimo_minuto": self.chamadas_portal}
            )
        self.simultaneas += 1
        self.pico_simultaneas = max(self.pico_simultaneas, self.simultaneas)
        await asyncio.sleep(0.01)
        self.simultaneas -= 1
        self.chamadas_portal += 1
        if "4209102" in requisicao.url.path:
            return httpx.Response(503, json={"erro": {"codigo": "FONTE_INDISPONIVEL", "mensagem": "indisponível"}})
        if requisicao.url.path.endswith("/evolucao-mensal"):
            raise httpx.ReadTimeout("timeout", request=requisicao)
        return httpx.Response(200, json={})


async def test_executa_consultas_em_paralelo_limitado_e_amostra_o_consumo():
    api = ApiFalsa()
    async with httpx.AsyncClient(base_url="http://api.teste", transport=httpx.MockTransport(api.responder)) as cliente:
        execucao = await executar(cliente, CONSULTAS, paralelas=2, intervalo_amostra=0.001)

    assert [(item.consulta, item.http_status, item.codigo_erro) for item in execucao.resultados] == [
        (CONSULTAS[0], 200, None),
        (CONSULTAS[1], 503, "FONTE_INDISPONIVEL"),
        (CONSULTAS[2], None, None),
        (CONSULTAS[3], 200, None),
    ]
    assert all(isinstance(item, Resultado) and item.segundos >= 0.01 for item in execucao.resultados)
    assert api.pico_simultaneas == 2
    assert execucao.limite_rpm == 150
    assert execucao.amostras[0] == 0
    assert execucao.amostras[-1] == 4
    assert execucao.amostras == sorted(execucao.amostras)


async def test_simulacao_contra_a_api_no_modo_mock_fica_dentro_do_limite():
    async with app.router.lifespan_context(app):
        transporte = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(base_url="http://api.teste", transport=transporte) as cliente:
            execucao = await simular(cliente, quantidade=8, paralelas=4, semente=1)

    resumo = resumir(execucao.resultados, execucao.amostras, execucao.limite_rpm)
    assert resumo.consultas == 8
    assert set(resumo.respostas) <= {"200", "503"}
    assert resumo.respostas["200"] >= 6
    assert 0 < resumo.pico_chamadas_minuto <= resumo.limite_rpm == 150
    assert resumo.aprovado
    assert execucao.consumo_final["chamadas_desde_inicio"] == resumo.pico_chamadas_minuto
