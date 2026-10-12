import type { ItemSerie, SerieMunicipio, StatusDado } from '@/api/tipos'
import {
  formatarInteiro,
  formatarInteiroCompacto,
  formatarMes,
  formatarMoeda,
  formatarMoedaCompacta,
  formatarVariacao,
  SEM_VALOR,
} from './formatacao'

export type CampoSerie = 'valor_total' | 'beneficiarios' | 'valor_medio_por_beneficiario'

export interface CoresGrafico {
  series: string[]
  eixo: string
  grade: string
  espessura: number
}

export interface SerieGrafico {
  nome: string
  posicao: number
  meses: ItemSerie[]
}

const FONTE_GRAFICO = { family: '"NBF Digitos", Rawline, Raleway, sans-serif', size: 12 }
const FORMAS_PONTO = ['circle', 'triangle', 'rect', 'rectRot', 'star', 'cross']
const POSICAO_TRACEJADA = 1
const TRACEJADO = [6, 4]

export function criarSeriesCidades(series: SerieMunicipio[]): SerieGrafico[] {
  return series.map((serie, posicao) => ({
    nome: `${serie.municipio.nome} (${serie.municipio.uf})`,
    posicao,
    meses: serie.meses,
  }))
}

function lerValor(mes: ItemSerie, campo: CampoSerie): number | null {
  return mes.status_dado === 'disponivel' ? mes[campo] : null
}

export function montarDadosEvolucao(
  series: SerieGrafico[],
  campo: CampoSerie,
  cores: CoresGrafico,
) {
  return {
    labels: (series[0]?.meses ?? []).map((mes) => formatarMes(mes.mes)),
    datasets: series.map((serie) => ({
      label: serie.nome,
      data: serie.meses.map((mes) => lerValor(mes, campo)),
      borderColor: cores.series[serie.posicao],
      backgroundColor: cores.series[serie.posicao],
      borderWidth: cores.espessura,
      borderDash: serie.posicao === POSICAO_TRACEJADA ? TRACEJADO : [],
      pointStyle: FORMAS_PONTO[serie.posicao],
      pointRadius: 4,
      pointHoverRadius: 6,
      tension: 0,
      spanGaps: false,
    })),
  }
}

export interface TabelaDados {
  colunas: string[]
  linhas: { mes: string; valores: string[] }[]
}

const TEXTO_SEM_NUMERO: Partial<Record<StatusDado, string>> = {
  sem_dados: 'sem dados',
  fonte_indisponivel: 'indisponível',
}

export function formatarValorCampo(valor: number | null, campo: CampoSerie): string {
  return campo === 'beneficiarios' ? formatarInteiro(valor) : formatarMoeda(valor)
}

function descreverCelula(mes: ItemSerie, campo: CampoSerie): string {
  return TEXTO_SEM_NUMERO[mes.status_dado] ?? formatarValorCampo(mes[campo], campo)
}

export function montarTabelaDados(series: SerieGrafico[], campo: CampoSerie): TabelaDados {
  return {
    colunas: series.map((serie) => serie.nome),
    linhas: (series[0]?.meses ?? []).map((mes, indice) => ({
      mes: formatarMes(mes.mes),
      valores: series.map((serie) => {
        const item = serie.meses[indice]
        return item ? descreverCelula(item, campo) : SEM_VALOR
      }),
    })),
  }
}

export interface CelulaVariacao {
  mes: string
  texto: string
  dica: string | null
}

export interface LinhaVariacao {
  nome: string
  celulas: CelulaVariacao[]
}

function explicarVariacao(mes: ItemSerie, indice: number): string | null {
  if (indice === 0) return 'Primeiro mês do período'
  if (mes.status_dado === 'fonte_indisponivel') return 'Dado indisponível neste mês'
  if (mes.status_dado !== 'disponivel') return 'Sem dados neste mês'
  if (mes.variacao_beneficiarios_absoluta === null)
    return 'Sem mês anterior com dados para comparar'
  return null
}

export function montarVariacao(series: SerieGrafico[]): LinhaVariacao[] {
  return series.map((serie) => ({
    nome: serie.nome,
    celulas: serie.meses.map((mes, indice) => {
      const dica = explicarVariacao(mes, indice)
      return {
        mes: formatarMes(mes.mes),
        texto: dica ? SEM_VALOR : formatarVariacao(mes.variacao_beneficiarios_absoluta),
        dica,
      }
    }),
  }))
}

export function formatarValorEixo(valor: number | null, campo: CampoSerie): string {
  return campo === 'beneficiarios' ? formatarInteiroCompacto(valor) : formatarMoedaCompacta(valor)
}

function resumirSerie(serie: SerieGrafico, campo: CampoSerie): string {
  const pontos = serie.meses.filter((mes) => lerValor(mes, campo) !== null)
  const primeiro = pontos[0]
  const ultimo = pontos.at(-1)
  if (!primeiro || !ultimo) return `${serie.nome}: sem dados.`
  if (serie.meses.length === 1) {
    return `${serie.nome}: ${formatarValorCampo(primeiro[campo], campo)} em ${formatarMes(primeiro.mes)}.`
  }
  const lacuna = pontos.length < serie.meses.length ? ', com mês sem dados' : ''
  const inicio = `${formatarValorEixo(primeiro[campo], campo)} em ${formatarMes(primeiro.mes)}`
  const fim = `${formatarValorEixo(ultimo[campo], campo)} em ${formatarMes(ultimo.mes)}`
  return `${serie.nome}: de ${inicio} a ${fim}${lacuna}.`
}

export function resumirEvolucao(series: SerieGrafico[], campo: CampoSerie) {
  return {
    texto: series.map((serie) => resumirSerie(serie, campo)).join(' '),
    vazio: series.every((serie) => serie.meses.every((mes) => lerValor(mes, campo) === null)),
  }
}

interface ItemDica {
  dataset: { label?: string }
  parsed: { y: number | null }
}

export function montarOpcoesEvolucao(
  series: SerieGrafico[],
  campo: CampoSerie,
  cores: CoresGrafico,
  ajustes: { animar: boolean },
) {
  function listarAusentes(indice: number): string[] {
    return series.flatMap((serie) => {
      const motivo = TEXTO_SEM_NUMERO[serie.meses[indice]?.status_dado ?? 'disponivel']
      return motivo ? [`${serie.nome}: ${motivo}`] : []
    })
  }

  return {
    responsive: true,
    maintainAspectRatio: false,
    locale: 'pt-BR',
    animation: ajustes.animar ? {} : (false as const),
    interaction: { mode: 'index' as const, intersect: false },
    scales: {
      x: {
        ticks: { color: cores.eixo, font: FONTE_GRAFICO },
        grid: { display: false },
        border: { color: cores.eixo },
      },
      y: {
        beginAtZero: true,
        suggestedMax: 1,
        ticks: {
          color: cores.eixo,
          font: FONTE_GRAFICO,
          callback: (valor: number | string) => formatarValorEixo(Number(valor), campo),
        },
        grid: { color: cores.grade },
        border: { display: false },
      },
    },
    plugins: {
      legend: {
        position: 'top' as const,
        align: 'start' as const,
        labels: {
          color: cores.eixo,
          font: FONTE_GRAFICO,
          usePointStyle: true,
          boxHeight: 8,
          padding: 16,
        },
      },
      tooltip: {
        titleFont: FONTE_GRAFICO,
        bodyFont: FONTE_GRAFICO,
        footerFont: FONTE_GRAFICO,
        callbacks: {
          label: (item: ItemDica) =>
            `${item.dataset.label}: ${formatarValorCampo(item.parsed.y, campo)}`,
          footer: (itens: { dataIndex: number }[]) => listarAusentes(itens[0]?.dataIndex ?? -1),
        },
      },
    },
  }
}
