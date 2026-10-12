import { describe, expect, it } from 'vitest'

import { descreverMetrica, METRICAS } from '@/dominio/metricas'

describe('métricas do ranking', () => {
  it('liga cada métrica ao campo mensal e aos textos da tela', () => {
    expect(METRICAS.map((metrica) => [metrica.valor, metrica.campoMensal])).toEqual([
      ['valor_total', 'valor_total'],
      ['beneficiarios_media_mensal', 'beneficiarios'],
      ['valor_medio_por_beneficiario', 'valor_medio_por_beneficiario'],
    ])
    expect(descreverMetrica('beneficiarios_media_mensal')).toMatchObject({
      rotulo: 'Beneficiários (média mensal)',
      tituloRanking: 'Ranking: beneficiários (média mensal)',
      frase: 'média mensal de beneficiários',
      nomeMensal: 'Beneficiários',
    })
    expect(descreverMetrica('valor_total').tituloRanking).toBe('Ranking: valor total recebido')
    expect(descreverMetrica('valor_medio_por_beneficiario').tituloRanking).toBe(
      'Ranking: valor médio por beneficiário',
    )
  })
})
