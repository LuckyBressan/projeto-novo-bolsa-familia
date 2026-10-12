import { describe, expect, it } from 'vitest'

import todas from '@mock/capitais_ref-4214805_2024-01a03_todas.json'
import type { ComparacaoCapitais } from '@/api/tipos'
import {
  atribuirPosicoes,
  escolherCapitaisPadrao,
  listarCapitaisGrafico,
  montarSeriesCapitais,
  montarTabelaCapitais,
} from '@/dominio/capitais'

const resposta = todas as ComparacaoCapitais

describe('capitais no gráfico de evolução', () => {
  it('dá a cada capital a próxima cor livre e mantém a cor de quem continua escolhida', () => {
    const iniciais = atribuirPosicoes({}, ['4205407', '4106902', '4314902'])
    expect(iniciais).toEqual({ '4205407': 0, '4106902': 2, '4314902': 3 })

    const semPrimeira = atribuirPosicoes(iniciais, ['4106902', '4314902'])
    expect(semPrimeira).toEqual({ '4106902': 2, '4314902': 3 })

    expect(atribuirPosicoes(semPrimeira, ['4106902', '4314902', '3550308'])).toEqual({
      '4106902': 2,
      '4314902': 3,
      '3550308': 0,
    })
  })

  it('oferece só capitais com dados e começa pela capital da UF da referência', () => {
    const opcoes = listarCapitaisGrafico(resposta)

    expect(opcoes).toHaveLength(26)
    expect(opcoes[0]).toEqual({ codigo: '3550308', nome: 'São Paulo (SP)' })
    expect(opcoes.map((opcao) => opcao.nome)).not.toContain('Boa Vista (RR)')
    expect(escolherCapitaisPadrao(resposta)).toEqual(['4205407'])

    const semSul = {
      ...resposta,
      capitais: resposta.capitais.filter((capital) => capital.municipio.uf !== 'SC'),
    }
    expect(escolherCapitaisPadrao(semSul)).toEqual(['3550308'])
  })

  it('monta as séries com a referência tracejada e as capitais nas cores atribuídas', () => {
    const series = montarSeriesCapitais(resposta, { '4205407': 0, '3550308': 2 })

    expect(series.map((serie) => [serie.nome, serie.posicao, serie.meses.length])).toEqual([
      ['Rio do Sul (referência)', 1, 3],
      ['Florianópolis (SC)', 0, 3],
      ['São Paulo (SP)', 2, 3],
    ])
    expect(series[1]?.meses[0]?.valor_total).toBe(11094105.44)
  })
})

describe('tabela detalhada por capital', () => {
  it('traz a referência à parte e as capitais na ordem do ranking, com as sem posição no fim', () => {
    const tabela = montarTabelaCapitais(resposta)

    expect(tabela.referencia).toMatchObject({
      nome: 'Rio do Sul (SC)',
      posicao: 27,
      valorTotal: 3042086.65,
      beneficiarios: 1582,
      valorMedio: 640.98,
      referencia: true,
    })
    expect(tabela.capitais).toHaveLength(27)
    expect(tabela.capitais[0]).toMatchObject({
      nome: 'São Paulo (SP)',
      posicao: 1,
      valorTotal: 1384095675.14,
      referencia: false,
    })
    expect(tabela.capitais.at(-1)).toMatchObject({
      nome: 'Boa Vista (RR)',
      posicao: null,
      valorTotal: null,
      beneficiarios: null,
      valorMedio: null,
    })
    expect(tabela.capitais.at(-1)?.situacao.status_dado).toBe('sem_dados')
  })
})
