import type { Capital, ComparacaoCapitais, Indicadores, Municipio } from '@/api/tipos'
import type { SerieGrafico } from './graficos'
import { nomearMunicipio } from './ranking'

export const LIMITE_CAPITAIS_GRAFICO = 5

const POSICAO_REFERENCIA = 1
const POSICOES_CAPITAIS = [0, 2, 3, 4, 5]

export type PosicoesSeries = Record<string, number>

export function atribuirPosicoes(anteriores: PosicoesSeries, escolhidas: string[]): PosicoesSeries {
  const mantidas = escolhidas.filter((codigo) => codigo in anteriores)
  const posicoes: PosicoesSeries = Object.fromEntries(
    mantidas.map((codigo) => [codigo, anteriores[codigo] ?? POSICAO_REFERENCIA]),
  )
  for (const codigo of escolhidas) {
    if (codigo in posicoes) continue
    const ocupadas = Object.values(posicoes)
    const livre = POSICOES_CAPITAIS.find((posicao) => !ocupadas.includes(posicao))
    if (livre !== undefined) posicoes[codigo] = livre
  }
  return posicoes
}

export interface OpcaoCapital {
  codigo: string
  nome: string
}

function listarDisponiveis(resposta: ComparacaoCapitais): Capital[] {
  const codigoReferencia = resposta.referencia.municipio.codigo_ibge
  return resposta.capitais.filter(
    (capital) =>
      capital.municipio.codigo_ibge !== codigoReferencia &&
      capital.meses.some((mes) => mes.status_dado === 'disponivel'),
  )
}

export function listarCapitaisGrafico(resposta: ComparacaoCapitais): OpcaoCapital[] {
  return listarDisponiveis(resposta).map((capital) => ({
    codigo: capital.municipio.codigo_ibge,
    nome: nomearMunicipio(capital.municipio),
  }))
}

export function escolherCapitaisPadrao(resposta: ComparacaoCapitais): string[] {
  const disponiveis = listarDisponiveis(resposta)
  const vizinha = disponiveis.find(
    (capital) => capital.municipio.uf === resposta.referencia.municipio.uf,
  )
  const escolhida = vizinha ?? disponiveis[0]
  return escolhida ? [escolhida.municipio.codigo_ibge] : []
}

export function montarSeriesCapitais(
  resposta: ComparacaoCapitais,
  posicoes: PosicoesSeries,
): SerieGrafico[] {
  const { referencia } = resposta
  const capitais = resposta.capitais.flatMap((capital) => {
    const posicao = posicoes[capital.municipio.codigo_ibge]
    return posicao === undefined
      ? []
      : [{ nome: nomearMunicipio(capital.municipio), posicao, meses: capital.meses }]
  })
  return [
    {
      nome: `${referencia.municipio.nome} (referência)`,
      posicao: POSICAO_REFERENCIA,
      meses: referencia.meses,
    },
    ...capitais.sort((anterior, seguinte) => anterior.posicao - seguinte.posicao),
  ]
}

export interface LinhaCapital {
  codigo: string
  nome: string
  posicao: number | null
  valorTotal: number | null
  beneficiarios: number | null
  valorMedio: number | null
  situacao: Indicadores
  referencia: boolean
}

export interface TabelaCapitais {
  referencia: LinhaCapital
  capitais: LinhaCapital[]
}

function criarLinha(
  entrada: { municipio: Municipio; indicadores: Indicadores },
  posicao: number | null,
  referencia: boolean,
): LinhaCapital {
  return {
    codigo: entrada.municipio.codigo_ibge,
    nome: nomearMunicipio(entrada.municipio),
    posicao,
    valorTotal: entrada.indicadores.valor_total,
    beneficiarios: entrada.indicadores.beneficiarios_media_mensal,
    valorMedio: entrada.indicadores.valor_medio_por_beneficiario,
    situacao: entrada.indicadores,
    referencia,
  }
}

export function montarTabelaCapitais(resposta: ComparacaoCapitais): TabelaCapitais {
  const { referencia } = resposta
  const codigoReferencia = referencia.municipio.codigo_ibge
  const linhas = resposta.capitais.map((capital) =>
    criarLinha(
      capital,
      capital.posicao_ranking,
      capital.municipio.codigo_ibge === codigoReferencia,
    ),
  )
  return {
    referencia: criarLinha(referencia, referencia.posicao_entre_capitais, true),
    capitais: [
      ...linhas
        .filter((linha) => linha.posicao !== null)
        .sort((anterior, seguinte) => (anterior.posicao ?? 0) - (seguinte.posicao ?? 0)),
      ...linhas.filter((linha) => linha.posicao === null),
    ],
  }
}
