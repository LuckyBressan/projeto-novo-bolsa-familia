from decimal import Decimal

import pytest

from app.integrations.portal_transparencia import RegistroBeneficio
from app.services.indicadores import TotaisMes, consolidar_mes


def registro(valor: str, beneficiarios: int) -> RegistroBeneficio:
    return RegistroBeneficio(
        codigo_ibge="4214805",
        municipio_nome="RIO DO SUL",
        uf="SC",
        mes="2024-01",
        valor=Decimal(valor),
        quantidade_beneficiados=beneficiarios,
        tipo_beneficio="Novo Bolsa Família",
        id_fonte=None,
    )


@pytest.mark.parametrize(
    ("registros", "esperado"),
    [
        ([registro("1043055.00", 1525)], TotaisMes(valor=Decimal("1043055.00"), beneficiarios=1525)),
        (
            [registro("1000.10", 10), registro("500.25", 5)],
            TotaisMes(valor=Decimal("1500.35"), beneficiarios=15),
        ),
        ([], None),
    ],
    ids=["um-registro", "varios-registros-somados", "sem-registro"],
)
def test_consolidar_mes_soma_registros_e_sem_registro_vira_none(registros, esperado):
    assert consolidar_mes(registros) == esperado
