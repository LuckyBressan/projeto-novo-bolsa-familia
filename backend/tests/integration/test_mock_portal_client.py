from decimal import Decimal
from pathlib import Path

import pytest

from app.core.errors import FonteIndisponivel
from app.integrations.mock_portal import MockPortalClient
from app.integrations.portal_transparencia import RegistroBeneficio

pytestmark = pytest.mark.anyio

PASTA_MOCK = Path(__file__).resolve().parents[2] / "app" / "data" / "mock"


@pytest.mark.parametrize(
    ("codigo_ibge", "mes", "esperado"),
    [
        (
            "4214805",
            "2024-01",
            [
                RegistroBeneficio(
                    codigo_ibge="4214805",
                    municipio_nome="RIO DO SUL",
                    uf="SC",
                    mes="2024-01",
                    valor=Decimal("1013272.42"),
                    quantidade_beneficiados=1574,
                    tipo_beneficio="Novo Bolsa Família",
                    id_fonte=900000602,
                )
            ],
        ),
        ("4202404", "2023-11", []),
    ],
    ids=["com-registro", "cenario-sem-registro"],
)
async def test_busca_le_registros_mock_portal(codigo_ibge, mes, esperado):
    assert await MockPortalClient(PASTA_MOCK).buscar(codigo_ibge, mes) == esperado


async def test_cenario_falha_fonte_indica_fonte_indisponivel():
    with pytest.raises(FonteIndisponivel):
        await MockPortalClient(PASTA_MOCK).buscar("4209102", "2024-12")
