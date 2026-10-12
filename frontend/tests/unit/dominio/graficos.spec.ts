import { describe, expect, it } from 'vitest'

import evolucaoLacuna from '@mock/evolucao_4202404-x-4209102_2023-10a12_lacuna.json'
import evolucaoCompleta from '@mock/evolucao_4214805-x-4202404_2024-01a03.json'
import type { Evolucao } from '@/api/tipos'
import {
  criarSeriesCidades,
  montarDadosEvolucao,
  montarOpcoesEvolucao,
  montarTabelaDados,
  montarVariacao,
  resumirEvolucao,
  type CoresGrafico,
} from '@/dominio/graficos'

const CORES: CoresGrafico = {
  series: ['#azul', '#laranja', '#verde', '#magenta', '#violeta', '#ciano'],
  eixo: '#eixo',
  grade: '#grade',
  espessura: 2,
}

const limpar = (texto: string) => texto.replace(/\xa0/g, ' ')
const lacuna = criarSeriesCidades((evolucaoLacuna as Evolucao).series)

describe('gráfico de evolução', () => {
  it('monta uma série por cidade, com lacuna no mês sem dados e identidade além da cor', () => {
    const dados = montarDadosEvolucao(lacuna, 'valor_total', CORES)

    expect(dados.labels).toEqual(['out/2023', 'nov/2023', 'dez/2023'])
    expect(dados.datasets).toHaveLength(2)
    expect(dados.datasets[0]).toMatchObject({
      label: 'Blumenau (SC)',
      data: [3683071.26, null, 3747450],
      borderColor: '#azul',
      backgroundColor: '#azul',
      borderDash: [],
      pointStyle: 'circle',
      spanGaps: false,
      borderWidth: 2,
    })
    expect(dados.datasets[1]).toMatchObject({
      label: 'Joinville (SC)',
      data: [6821228.7, 6733837.44, 6817226.91],
      borderColor: '#laranja',
      borderDash: [6, 4],
      pointStyle: 'triangle',
    })
    expect(montarDadosEvolucao(lacuna, 'beneficiarios', CORES).datasets[0]?.data).toEqual([
      5736,
      null,
      5810,
    ])
  })

  it('monta um ponto por mês para cada cidade quando não há lacuna', () => {
    const completa = criarSeriesCidades((evolucaoCompleta as Evolucao).series)
    const dados = montarDadosEvolucao(completa, 'beneficiarios', CORES)

    expect(dados.labels).toEqual(['jan/2024', 'fev/2024', 'mar/2024'])
    expect(dados.datasets.map((serie) => [serie.label, serie.data])).toEqual([
      ['Rio do Sul (SC)', [1574, 1590, 1582]],
      ['Blumenau (SC)', [5780, 5769, 5820]],
    ])
  })

  it('monta a tabela de dados com o valor completo e o motivo do mês sem número', () => {
    const tabela = montarTabelaDados(lacuna, 'valor_total')

    expect(tabela.colunas).toEqual(['Blumenau (SC)', 'Joinville (SC)'])
    expect(tabela.linhas.map((linha) => [linha.mes, ...linha.valores.map(limpar)])).toEqual([
      ['out/2023', 'R$ 3.683.071,26', 'R$ 6.821.228,70'],
      ['nov/2023', 'sem dados', 'R$ 6.733.837,44'],
      ['dez/2023', 'R$ 3.747.450,00', 'R$ 6.817.226,91'],
    ])

    const indisponivel = lacuna.map((serie) => ({
      ...serie,
      meses: serie.meses.map((mes) => ({ ...mes, status_dado: 'fonte_indisponivel' as const })),
    }))
    expect(montarTabelaDados(indisponivel, 'beneficiarios').linhas[0]?.valores).toEqual([
      'indisponível',
      'indisponível',
    ])
    expect(montarTabelaDados(lacuna, 'beneficiarios').linhas[0]?.valores).toEqual([
      '5.736',
      '10.530',
    ])
  })

  it('mostra a variação de beneficiários com o motivo quando não há comparação', () => {
    expect(montarVariacao(lacuna)).toEqual([
      {
        nome: 'Blumenau (SC)',
        celulas: [
          { mes: 'out/2023', texto: '—', dica: 'Primeiro mês do período' },
          { mes: 'nov/2023', texto: '—', dica: 'Sem dados neste mês' },
          { mes: 'dez/2023', texto: '—', dica: 'Sem mês anterior com dados para comparar' },
        ],
      },
      {
        nome: 'Joinville (SC)',
        celulas: [
          { mes: 'out/2023', texto: '—', dica: 'Primeiro mês do período' },
          { mes: 'nov/2023', texto: '▼ −73', dica: null },
          { mes: 'dez/2023', texto: '▼ −46', dica: null },
        ],
      },
    ])
  })

  it('resume o gráfico em texto e avisa quando não há nenhum dado', () => {
    expect(limpar(resumirEvolucao(lacuna, 'valor_total').texto)).toBe(
      'Blumenau (SC): de R$ 3,68 mi em out/2023 a R$ 3,75 mi em dez/2023, com mês sem dados. ' +
        'Joinville (SC): de R$ 6,82 mi em out/2023 a R$ 6,82 mi em dez/2023.',
    )
    expect(resumirEvolucao(lacuna, 'valor_total').vazio).toBe(false)

    const mesUnico = lacuna.map((serie) => ({ ...serie, meses: serie.meses.slice(0, 1) }))
    expect(limpar(resumirEvolucao(mesUnico, 'beneficiarios').texto)).toBe(
      'Blumenau (SC): 5.736 em out/2023. Joinville (SC): 10.530 em out/2023.',
    )

    const semDados = lacuna.map((serie) => ({
      ...serie,
      meses: serie.meses.map((mes) => ({ ...mes, status_dado: 'sem_dados' as const })),
    }))
    expect(resumirEvolucao(semDados, 'valor_total')).toEqual({
      texto: 'Blumenau (SC): sem dados. Joinville (SC): sem dados.',
      vazio: true,
    })
  })

  it('formata eixo e dica do gráfico e lista na dica quem ficou sem dados no mês', () => {
    const opcoes = montarOpcoesEvolucao(lacuna, 'valor_total', CORES, { animar: false })
    const dica = opcoes.plugins.tooltip.callbacks

    expect(limpar(opcoes.scales.y.ticks.callback(1500000))).toBe('R$ 1,5 mi')
    expect(opcoes.scales.y.beginAtZero).toBe(true)
    expect(opcoes.scales.y.grid.color).toBe('#grade')
    expect(opcoes.scales.x.ticks.color).toBe('#eixo')
    expect(opcoes.plugins.legend.position).toBe('top')
    expect(opcoes.animation).toBe(false)
    expect(opcoes.interaction).toEqual({ mode: 'index', intersect: false })
    expect(
      limpar(dica.label({ dataset: { label: 'Joinville (SC)' }, parsed: { y: 6733837.44 } })),
    ).toBe('Joinville (SC): R$ 6.733.837,44')
    expect(dica.footer([{ dataIndex: 1 }])).toEqual(['Blumenau (SC): sem dados'])
    expect(dica.footer([{ dataIndex: 0 }])).toEqual([])
    expect(
      montarOpcoesEvolucao(lacuna, 'beneficiarios', CORES, { animar: true }).animation,
    ).toEqual({})
  })
})
