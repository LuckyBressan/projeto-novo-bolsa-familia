import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from app.core.errors import FonteIndisponivel
from app.integrations.portal_transparencia import RegistroBeneficio, converter_registro


class MockPortalClient:
    def __init__(self, pasta: Path):
        pasta_portal = pasta / "portal"
        itens = json.loads(
            (pasta_portal / "novo-bolsa-familia-por-municipio.json").read_text(encoding="utf-8"),
            parse_float=Decimal,
        )
        cenarios = json.loads((pasta_portal / "cenarios.json").read_text(encoding="utf-8"))
        self._registros: dict[tuple[str, str], list[RegistroBeneficio]] = defaultdict(list)
        for registro in map(converter_registro, itens):
            self._registros[(registro.codigo_ibge, registro.mes)].append(registro)
        self._falhas = {(item["codigoIbge"], item["mes"]) for item in cenarios["falha_fonte_http_503"]}

    async def buscar(self, codigo_ibge: str, mes: str) -> list[RegistroBeneficio]:
        if (codigo_ibge, mes) in self._falhas:
            raise FonteIndisponivel()
        return list(self._registros.get((codigo_ibge, mes), []))
