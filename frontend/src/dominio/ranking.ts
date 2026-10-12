import type { ComparacaoCapitais, Indicadores, Municipio, StatusDado } from '@/api/tipos'
import { formatarPosicao } from './formatacao'
import {
  FONTE_GRAFICO,
  formatarValorCampo,
  formatarValorEixo,
  type CoresGrafico,
  type TabelaDados,
} from './graficos'
import { descreverMetrica, type DescricaoMetrica } from './metricas'

export interface BarraRanking {
  codigo: string
  nome: string
  rotulo: string
  posicao: number
  valor: number
  valorFormatado: string
  referencia: boolean
}

export interface Ranking {
  metrica: DescricaoMetrica
  barras: BarraRanking[]
  totalRanqueadas: number
  semPosicao: string[]
}

const MOTIVOS_SEM_POSICAO: Record<StatusDado, string> = {
  disponivel: 'sem posição',
  parcial: 'dados parciais',
  sem_dados: 'sem dados',
  fonte_indisponivel: 'indisponível',
}

export function nomearMunicipio(municipio: Municipio): string {
  return `${municipio.nome} (${municipio.uf})`
}

export function verificarReferenciaCapital(resposta: ComparacaoCapitais): boolean {
  const codigo = resposta.referencia.municipio.codigo_ibge
  return resposta.capitais.some((capital) => capital.municipio.codigo_ibge === codigo)
}

export function montarRanking(resposta: ComparacaoCapitais): Ranking {
  const metrica = descreverMetrica(resposta.metrica_ranking)
  const { referencia } = resposta

  function criarBarra(
    entrada: { municipio: Municipio; indicadores: Indicadores },
    posicao: number | null,
    destacada: boolean,
  ): BarraRanking[] {
    const valor = entrada.indicadores[metrica.valor]
    if (posicao === null || valor === null) return []
    const nome = nomearMunicipio(entrada.municipio)
    return [
      {
        codigo: entrada.municipio.codigo_ibge,
        nome,
        rotulo: destacada ? `${entrada.municipio.nome} (referência)` : nome,
        posicao,
        valor,
        valorFormatado: formatarValorCampo(valor, metrica.campoMensal),
        referencia: destacada,
      },
    ]
  }

  const codigoReferencia = referencia.municipio.codigo_ibge
  const barras = resposta.capitais.flatMap((capital) =>
    criarBarra(
      capital,
      capital.posicao_ranking,
      capital.municipio.codigo_ibge === codigoReferencia,
    ),
  )
  const totalRanqueadas = barras.length
  if (!barras.some((barra) => barra.referencia)) {
    const [extra] = criarBarra(referencia, referencia.posicao_entre_capitais, true)
    if (extra) barras.splice(extra.posicao - 1, 0, extra)
  }

  return {
    metrica,
    barras,
    totalRanqueadas,
    semPosicao: resposta.capitais
      .filter((capital) => capital.posicao_ranking === null)
      .map(
        (capital) =>
          `${capital.municipio.nome} (${MOTIVOS_SEM_POSICAO[capital.indicadores.status_dado]})`,
      ),
  }
}

export interface DescricaoPosicao {
  destaque: string
  frase: string
}

export function descreverPosicao(resposta: ComparacaoCapitais): DescricaoPosicao {
  const posicao = resposta.referencia.posicao_entre_capitais
  const destaque = formatarPosicao(posicao)
  if (posicao === null) {
    return { destaque, frase: 'Sem posição no ranking: dados incompletos para o período.' }
  }
  const { totalRanqueadas } = montarRanking(resposta)
  if (totalRanqueadas === 0) {
    return {
      destaque: formatarPosicao(null),
      frase: 'Nenhuma capital com dados no período para comparar.',
    }
  }
  const criterio = descreverMetrica(resposta.metrica_ranking).frase
  const capital = verificarReferenciaCapital(resposta)
  if (capital && totalRanqueadas === 1) {
    return { destaque, frase: `É a única capital ranqueada por ${criterio}.` }
  }
  const verbo = capital ? 'Está' : 'Ficaria'
  const lugar = situarEntreCapitais(posicao, totalRanqueadas, criterio)
  return { destaque, frase: `${verbo} em ${destaque} lugar${lugar}.` }
}

function situarEntreCapitais(posicao: number, total: number, criterio: string): string {
  const depois = posicao > total
  if (total === 1) {
    return `, ${depois ? 'depois da' : 'à frente da'} única capital ranqueada por ${criterio}`
  }
  return depois
    ? `, depois das ${total} capitais ranqueadas por ${criterio}`
    : ` entre as ${total} capitais ranqueadas por ${criterio}`
}

const POSICAO_CAPITAL = 0
const POSICAO_REFERENCIA = 1

export function montarDadosRanking(ranking: Ranking, cores: CoresGrafico) {
  const { barras } = ranking
  const corCapital = cores.series[POSICAO_CAPITAL]
  return {
    labels: barras.map((barra) => `${formatarPosicao(barra.posicao)} ${barra.rotulo}`),
    datasets: [
      {
        data: barras.map((barra) => barra.valor),
        backgroundColor: barras.map((barra) =>
          barra.referencia ? cores.series[POSICAO_REFERENCIA] : corCapital,
        ),
        borderColor: barras.map((barra) => (barra.referencia ? cores.texto : corCapital)),
        borderWidth: barras.map((barra) => (barra.referencia ? 2 : 0)),
        borderRadius: 4,
        borderSkipped: 'start' as const,
        minBarLength: 3,
        barPercentage: 0.9,
        categoryPercentage: 1,
      },
    ],
  }
}

export function montarOpcoesRanking(
  ranking: Ranking,
  cores: CoresGrafico,
  ajustes: { animar: boolean },
) {
  const { barras, metrica, totalRanqueadas } = ranking

  function situar(indice: number): string {
    const barra = barras[indice]
    if (!barra) return ''
    const posicao = formatarPosicao(barra.posicao)
    return barra.referencia && barra.posicao > totalRanqueadas
      ? `Município de referência: ficaria em ${posicao}`
      : `${posicao} de ${totalRanqueadas} capitais`
  }

  return {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    locale: 'pt-BR',
    animation: ajustes.animar ? {} : (false as const),
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          color: cores.eixo,
          font: FONTE_GRAFICO,
          maxRotation: 0,
          autoSkipPadding: 16,
          callback: (valor: number | string) =>
            formatarValorEixo(Number(valor), metrica.campoMensal),
        },
        grid: { color: cores.grade },
        border: { display: false },
      },
      y: {
        ticks: { color: cores.eixo, font: FONTE_GRAFICO, autoSkip: false },
        grid: { display: false },
        border: { color: cores.eixo },
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        titleFont: FONTE_GRAFICO,
        bodyFont: FONTE_GRAFICO,
        footerFont: FONTE_GRAFICO,
        callbacks: {
          title: (itens: { dataIndex: number }[]) => barras[itens[0]?.dataIndex ?? -1]?.nome ?? '',
          label: (item: { dataIndex: number }) =>
            `${metrica.rotulo}: ${barras[item.dataIndex]?.valorFormatado ?? ''}`,
          footer: (itens: { dataIndex: number }[]) => situar(itens[0]?.dataIndex ?? -1),
        },
      },
    },
  }
}

const QUANTIDADE_RESUMO = 3

export function resumirRanking(ranking: Ranking): string {
  const { barras, metrica } = ranking
  if (!barras.length) return `${metrica.tituloRanking}. Sem dados para o período selecionado.`
  const primeiras = barras
    .filter((barra) => !barra.referencia)
    .slice(0, QUANTIDADE_RESUMO)
    .map((barra) => `${formatarPosicao(barra.posicao)} ${barra.nome}`)
    .join(', ')
  const referencia = barras.find((barra) => barra.referencia)
  const situacao = referencia
    ? ` ${referencia.nome} em ${formatarPosicao(referencia.posicao)} lugar.`
    : ''
  return `${metrica.tituloRanking}. ${primeiras}.${situacao}`
}

export function montarTabelaRanking(ranking: Ranking): TabelaDados {
  return {
    primeira: 'Município',
    colunas: ['Posição', ranking.metrica.rotulo],
    linhas: ranking.barras.map((barra) => ({
      rotulo: barra.rotulo,
      valores: [formatarPosicao(barra.posicao), barra.valorFormatado],
    })),
  }
}
