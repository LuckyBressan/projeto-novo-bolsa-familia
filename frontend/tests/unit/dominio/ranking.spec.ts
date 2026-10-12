import { describe, expect, it } from 'vitest'

import sul from '@mock/capitais_ref-4214805_2024-01a03_SC-PR-RS_valor-medio.json'
import todas from '@mock/capitais_ref-4214805_2024-01a03_todas.json'
import type { ComparacaoCapitais } from '@/api/tipos'
import {
  descreverPosicao,
  montarDadosRanking,
  montarOpcoesRanking,
  montarRanking,
  montarTabelaRanking,
  resumirRanking,
} from '@/dominio/ranking'

const resposta = todas as ComparacaoCapitais
const CORES = {
  series: ['#azul', '#laranja', '#verde', '#magenta', '#violeta', '#ciano'],
  eixo: '#eixo',
  grade: '#grade',
  texto: '#texto',
  espessura: 2,
}
const limpar = (texto: string) => texto.replace(/\xa0/g, ' ')

describe('ranking das capitais', () => {
  it('ordena as capitais com posição e encaixa a referência no lugar que ocuparia', () => {
    const ranking = montarRanking(resposta)

    expect(ranking.barras).toHaveLength(27)
    expect(ranking.totalRanqueadas).toBe(26)
    expect(ranking.barras[0]).toMatchObject({
      nome: 'São Paulo (SP)',
      posicao: 1,
      valor: 1384095675.14,
      referencia: false,
    })
    expect(limpar(ranking.barras[0]?.valorFormatado ?? '')).toBe('R$ 1.384.095.675,14')
    expect(ranking.barras.at(-1)).toMatchObject({
      nome: 'Rio do Sul (SC)',
      rotulo: 'Rio do Sul (referência)',
      posicao: 27,
      valor: 3042086.65,
      referencia: true,
    })
    expect(ranking.barras.map((barra) => barra.nome)).not.toContain('Boa Vista (RR)')
    expect(ranking.semPosicao).toEqual(['Boa Vista (sem dados)'])
  })

  it('usa a métrica pedida e não desenha a referência sem posição', () => {
    const medio = montarRanking(sul as ComparacaoCapitais)

    expect(medio.barras.map((barra) => [barra.posicao, barra.rotulo, barra.valor])).toEqual([
      [1, 'Porto Alegre (RS)', 651.24],
      [2, 'Curitiba (PR)', 649.49],
      [3, 'Florianópolis (SC)', 647.45],
      [4, 'Rio do Sul (referência)', 640.98],
    ])
    expect(medio.semPosicao).toEqual([])

    const semPosicao = montarRanking({
      ...resposta,
      referencia: { ...resposta.referencia, posicao_entre_capitais: null },
    })
    expect(semPosicao.barras).toHaveLength(26)
    expect(semPosicao.barras.some((barra) => barra.referencia)).toBe(false)
  })

  it('quando a referência é uma capital, destaca a barra dela em vez de repetir', () => {
    const florianopolis = resposta.capitais.find((capital) => capital.municipio.uf === 'SC')
    if (!florianopolis) throw new Error('fixture sem Florianópolis')
    const ranking = montarRanking({
      ...resposta,
      referencia: {
        municipio: florianopolis.municipio,
        indicadores: florianopolis.indicadores,
        meses: florianopolis.meses,
        posicao_entre_capitais: florianopolis.posicao_ranking,
      },
    })

    expect(ranking.barras).toHaveLength(26)
    expect(ranking.barras.filter((barra) => barra.referencia)).toMatchObject([
      { rotulo: 'Florianópolis (referência)', posicao: 26 },
    ])
  })

  it('descreve em uma frase a posição do município de referência', () => {
    expect(descreverPosicao(resposta)).toEqual({
      destaque: '27º',
      frase: 'Ficaria em 27º lugar, depois das 26 capitais ranqueadas por valor total recebido.',
    })
    expect(descreverPosicao(sul as ComparacaoCapitais)).toEqual({
      destaque: '4º',
      frase:
        'Ficaria em 4º lugar, depois das 3 capitais ranqueadas por valor médio por beneficiário.',
    })
    expect(
      descreverPosicao({
        ...resposta,
        referencia: { ...resposta.referencia, posicao_entre_capitais: 5 },
      }).frase,
    ).toBe('Ficaria em 5º lugar entre as 26 capitais ranqueadas por valor total recebido.')
    expect(
      descreverPosicao({
        ...resposta,
        referencia: { ...resposta.referencia, posicao_entre_capitais: null },
      }),
    ).toEqual({
      destaque: '—',
      frase: 'Sem posição no ranking: dados incompletos para o período.',
    })
  })

  it('quando a referência é uma capital, diz a posição que ela já ocupa', () => {
    const florianopolis = resposta.capitais.find((capital) => capital.municipio.uf === 'SC')
    if (!florianopolis) throw new Error('fixture sem Florianópolis')

    expect(
      descreverPosicao({
        ...resposta,
        referencia: {
          municipio: florianopolis.municipio,
          indicadores: florianopolis.indicadores,
          meses: florianopolis.meses,
          posicao_entre_capitais: 26,
        },
      }).frase,
    ).toBe('Está em 26º lugar entre as 26 capitais ranqueadas por valor total recebido.')
  })
})

describe('posição com uma capital ou nenhuma', () => {
  const curitiba = resposta.capitais.filter((capital) => capital.municipio.uf === 'PR')

  it('fala no singular quando só uma capital foi ranqueada', () => {
    expect(
      descreverPosicao({
        ...resposta,
        capitais: curitiba,
        referencia: { ...resposta.referencia, posicao_entre_capitais: 2 },
      }).frase,
    ).toBe('Ficaria em 2º lugar, depois da única capital ranqueada por valor total recebido.')
    expect(
      descreverPosicao({
        ...resposta,
        capitais: curitiba,
        referencia: { ...resposta.referencia, posicao_entre_capitais: 1 },
      }).frase,
    ).toBe('Ficaria em 1º lugar, à frente da única capital ranqueada por valor total recebido.')
  })

  it('quando a referência é a única capital ranqueada, diz isso', () => {
    const [capital] = curitiba
    if (!capital) throw new Error('fixture sem Curitiba')

    expect(
      descreverPosicao({
        ...resposta,
        capitais: curitiba,
        referencia: {
          municipio: capital.municipio,
          indicadores: capital.indicadores,
          meses: capital.meses,
          posicao_entre_capitais: 1,
        },
      }).frase,
    ).toBe('É a única capital ranqueada por valor total recebido.')
  })

  it('avisa quando nenhuma capital tem dados para comparar', () => {
    expect(
      descreverPosicao({
        ...resposta,
        capitais: resposta.capitais.filter((capital) => capital.municipio.uf === 'RR'),
        referencia: { ...resposta.referencia, posicao_entre_capitais: 1 },
      }),
    ).toEqual({
      destaque: '—',
      frase: 'Nenhuma capital com dados no período para comparar.',
    })
  })
})

describe('gráfico do ranking', () => {
  it('desenha as capitais em uma cor e a referência em outra, com borda', () => {
    const ranking = montarRanking(sul as ComparacaoCapitais)
    const dados = montarDadosRanking(ranking, CORES)

    expect(dados.labels).toEqual([
      '1º Porto Alegre (RS)',
      '2º Curitiba (PR)',
      '3º Florianópolis (SC)',
      '4º Rio do Sul (referência)',
    ])
    expect(dados.datasets).toHaveLength(1)
    expect(dados.datasets[0]).toMatchObject({
      data: [651.24, 649.49, 647.45, 640.98],
      backgroundColor: ['#azul', '#azul', '#azul', '#laranja'],
      borderColor: ['#azul', '#azul', '#azul', '#texto'],
      borderWidth: [0, 0, 0, 2],
    })
  })

  it('mostra o eixo na forma curta e, na dica, o valor completo com a posição', () => {
    const ranking = montarRanking(resposta)
    const opcoes = montarOpcoesRanking(ranking, CORES, { animar: false })
    const dica = opcoes.plugins.tooltip.callbacks

    expect(opcoes.indexAxis).toBe('y')
    expect(opcoes.animation).toBe(false)
    expect(opcoes.plugins.legend.display).toBe(false)
    expect(opcoes.scales.x.beginAtZero).toBe(true)
    expect(limpar(opcoes.scales.x.ticks.callback(1400000000))).toBe('R$ 1,4 bi')
    expect(opcoes.scales.y.ticks.autoSkip).toBe(false)
    expect(dica.title([{ dataIndex: 0 }])).toBe('São Paulo (SP)')
    expect(limpar(dica.label({ dataIndex: 0 }))).toBe('Valor total recebido: R$ 1.384.095.675,14')
    expect(dica.footer([{ dataIndex: 0 }])).toBe('1º de 26 capitais')
    expect(dica.footer([{ dataIndex: 26 }])).toBe('Município de referência: ficaria em 27º')
  })

  it('resume o ranking em texto e monta a tabela de dados com o valor completo', () => {
    const ranking = montarRanking(sul as ComparacaoCapitais)

    expect(resumirRanking(ranking)).toBe(
      'Ranking: valor médio por beneficiário. 1º Porto Alegre (RS), 2º Curitiba (PR), ' +
        '3º Florianópolis (SC). Rio do Sul (SC) em 4º lugar.',
    )
    const tabela = montarTabelaRanking(ranking)
    expect(tabela.primeira).toBe('Município')
    expect(tabela.colunas).toEqual(['Posição', 'Valor médio por beneficiário'])
    expect(tabela.linhas.map((linha) => [linha.rotulo, ...linha.valores.map(limpar)])).toEqual([
      ['Porto Alegre (RS)', '1º', 'R$ 651,24'],
      ['Curitiba (PR)', '2º', 'R$ 649,49'],
      ['Florianópolis (SC)', '3º', 'R$ 647,45'],
      ['Rio do Sul (referência)', '4º', 'R$ 640,98'],
    ])

    const vazio = montarRanking({ ...resposta, capitais: [] })
    expect(resumirRanking({ ...vazio, barras: [] })).toBe(
      'Ranking: valor total recebido. Sem dados para o período selecionado.',
    )
  })
})
