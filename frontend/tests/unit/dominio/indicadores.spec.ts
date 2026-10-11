import { describe, expect, it } from 'vitest'

import comparacaoFalha from '@mock/comparacao_4209102-x-4214805_2024-10a12_falha-fonte.json'
import comparacao from '@mock/comparacao_4214805-x-4202404_2024-01a03.json'
import mesUnico from '@mock/indicadores_4214805_2024-02.json'
import type { Indicadores } from '@/api/tipos'
import { montarCards } from '@/dominio/indicadores'

const normalizar = (texto: string) => texto.replace(/\xa0/g, ' ')
const textos = (indicadores: unknown, periodo: Parameters<typeof montarCards>[1]) =>
  montarCards(indicadores as Indicadores, periodo).map((card) => ({
    ...card,
    valor: normalizar(card.valor),
    valorCompacto: normalizar(card.valorCompacto),
  }))

describe('cards de indicadores', () => {
  it('monta os três cards do período com os rótulos de soma e de média mensal', () => {
    const rioDoSul = comparacao.municipios[0]!.indicadores

    expect(textos(rioDoSul, { ano: 2024, mesInicio: 1, mesFim: 3 })).toEqual([
      {
        titulo: 'Valor total recebido',
        valor: 'R$ 3.042.086,65',
        valorCompacto: 'R$ 3,04 mi',
        complemento: 'Soma de jan/2024 a mar/2024',
      },
      {
        titulo: 'Beneficiários (média mensal)',
        valor: '1.582',
        valorCompacto: '1.582',
        complemento: 'Média de pessoas por mês',
      },
      {
        titulo: 'Valor médio por beneficiário (por mês)',
        valor: 'R$ 640,98',
        valorCompacto: 'R$ 640,98',
        complemento: 'Quanto cada pessoa recebeu, em média, por mês',
      },
    ])
  })

  it('troca os rótulos quando o período tem um mês só', () => {
    const cards = textos(mesUnico.indicadores, { ano: 2024, mesInicio: 2, mesFim: 2 })

    expect(cards.map((card) => [card.titulo, card.valor, card.complemento])).toEqual([
      ['Valor total recebido', 'R$ 1.023.980,19', 'Valor de fev/2024'],
      ['Beneficiários no mês', '1.590', 'Pessoas que receberam no mês'],
      [
        'Valor médio por beneficiário (por mês)',
        'R$ 644,01',
        'Quanto cada pessoa recebeu, em média, no mês',
      ],
    ])
  })

  it('mostra travessão, nunca zero, na cidade sem valores', () => {
    const joinville = comparacaoFalha.municipios[0]!.indicadores
    const cards = textos(joinville, { ano: 2024, mesInicio: 10, mesFim: 12 })

    expect(cards.map((card) => card.valor)).toEqual(['—', '—', '—'])
    expect(cards.map((card) => card.valorCompacto)).toEqual(['—', '—', '—'])
  })
})
