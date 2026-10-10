import pytest

from app.core.errors import EstadoInvalido, MunicipioInvalido
from app.services.catalogos import Catalogo, Estado, Municipio

ESTADOS = [Estado("42", "SC", "Santa Catarina"), Estado("41", "PR", "Paraná")]
MUNICIPIOS = [
    Municipio("4214805", "Rio do Sul", "SC"),
    Municipio("4202404", "Blumenau", "SC"),
    Municipio("4200606", "Águas Mornas", "SC"),
    Municipio("4205407", "Florianópolis", "SC"),
    Municipio("4106902", "Curitiba", "PR"),
]


@pytest.fixture
def catalogo() -> Catalogo:
    return Catalogo(estados=ESTADOS, municipios=MUNICIPIOS, capitais=[])


@pytest.mark.parametrize(
    ("uf", "busca", "nomes"),
    [
        ("SC", None, ["Águas Mornas", "Blumenau", "Florianópolis", "Rio do Sul"]),
        ("sc", "FLORIAN", ["Florianópolis"]),
        ("SC", "aguas", ["Águas Mornas"]),
        ("SC", "do s", ["Rio do Sul"]),
        ("PR", None, ["Curitiba"]),
        ("SC", "xyz", []),
    ],
)
def test_municipios_filtrados_por_uf_e_busca_em_ordem_alfabetica(catalogo, uf, busca, nomes):
    assert [municipio.nome for municipio in catalogo.municipios_uf(uf, busca)] == nomes


def test_municipio_encontrado_pelo_codigo_ibge(catalogo):
    assert catalogo.municipio("4214805") == Municipio("4214805", "Rio do Sul", "SC")


def test_municipio_fora_catalogo_indica_municipio_invalido(catalogo):
    with pytest.raises(MunicipioInvalido) as erro:
        catalogo.municipio("9999999")

    assert (erro.value.mensagem, erro.value.detalhes) == (
        "Município não encontrado no catálogo.",
        {"codigo_ibge": "9999999"},
    )


def test_uf_inexistente_indica_estado_invalido(catalogo):
    with pytest.raises(EstadoInvalido) as erro:
        catalogo.municipios_uf("XX")

    assert (erro.value.mensagem, erro.value.detalhes) == ("UF inexistente.", {"uf": "XX"})


CAPITAIS = [Municipio("4205407", "Florianópolis", "SC"), Municipio("4106902", "Curitiba", "PR")]


@pytest.mark.parametrize(
    ("filtro", "ufs", "nomes"),
    [
        (None, None, ["Florianópolis", "Curitiba"]),
        ("PR", ["PR"], ["Curitiba"]),
        ("sc, PR,sc", ["SC", "PR"], ["Florianópolis", "Curitiba"]),
    ],
)
def test_capitais_filtradas_pelas_ufs_informadas(filtro, ufs, nomes):
    catalogo = Catalogo(estados=ESTADOS, municipios=MUNICIPIOS + CAPITAIS, capitais=CAPITAIS)

    capitais, filtro_aplicado = catalogo.capitais_ufs(filtro)

    assert filtro_aplicado == ufs
    assert [capital.nome for capital in capitais] == nomes


def test_capitais_com_uf_inexistente_indica_estado_invalido():
    catalogo = Catalogo(estados=ESTADOS, municipios=CAPITAIS, capitais=CAPITAIS)

    with pytest.raises(EstadoInvalido) as erro:
        catalogo.capitais_ufs("SC,XX")

    assert erro.value.detalhes == {"uf": "XX"}
