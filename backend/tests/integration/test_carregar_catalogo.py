from pathlib import Path

import pytest

from app.services.catalogos import carregar_catalogo

PASTA_DADOS = Path(__file__).resolve().parents[2] / "app" / "data"


@pytest.mark.parametrize("modo_mock", [True, False])
def test_catalogo_tem_27_ufs_e_27_capitais_distintas_presentes_nos_municipios(modo_mock):
    catalogo = carregar_catalogo(PASTA_DADOS, modo_mock=modo_mock)

    capitais = catalogo.capitais()
    assert len(catalogo.estados()) == 27
    assert len({capital.codigo_ibge for capital in capitais}) == 27
    assert sorted(capital.uf for capital in capitais) == sorted(estado.uf for estado in catalogo.estados())
    assert all(catalogo.municipio(capital.codigo_ibge) == capital for capital in capitais)


def test_catalogo_real_tem_todos_municipios_ibge():
    catalogo = carregar_catalogo(PASTA_DADOS, modo_mock=False)

    assert sum(len(catalogo.municipios_uf(estado.uf)) for estado in catalogo.estados()) == 5571
    assert catalogo.municipio("4214805").nome == "Rio do Sul"


def test_catalogo_mock_tem_so_municipios_do_mock():
    catalogo = carregar_catalogo(PASTA_DADOS, modo_mock=True)

    assert sum(len(catalogo.municipios_uf(estado.uf)) for estado in catalogo.estados()) == 32
    assert [municipio.nome for municipio in catalogo.municipios_uf("SC")] == [
        "Blumenau",
        "Florianópolis",
        "Joinville",
        "Rio do Sul",
    ]
