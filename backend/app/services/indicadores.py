from dataclasses import dataclass
from decimal import Decimal

from app.integrations.portal_transparencia import RegistroBeneficio


@dataclass(frozen=True)
class TotaisMes:
    valor: Decimal
    beneficiarios: int


def consolidar_mes(registros: list[RegistroBeneficio]) -> TotaisMes | None:
    if not registros:
        return None
    return TotaisMes(
        valor=sum((registro.valor for registro in registros), Decimal(0)),
        beneficiarios=sum(registro.quantidade_beneficiados for registro in registros),
    )
