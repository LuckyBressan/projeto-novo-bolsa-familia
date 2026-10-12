import { describe, expect, it } from 'vitest'

import estados from '@mock/estados.json'
import periodos from '@mock/periodos.json'
import {
  completarFiltrosCapitais,
  completarFiltrosComparacao,
  descreverPendenciaCapitais,
  descreverPendenciaComparacao,
  encontrarUf,
  montarQueryCapitais,
  montarQueryComparacao,
  resolverFiltrosCapitais,
  resolverFiltrosComparacao,
  type EdicaoCapitais,
} from '@/dominio/filtros'

describe('filtros', () => {
  it('descobre a UF pelos dois primeiros dígitos do código IBGE', () => {
    expect(encontrarUf(estados.items, '4214805')).toBe('SC')
    expect(encontrarUf(estados.items, '3550308')).toBe('SP')
    expect(encontrarUf(estados.items, '9999999')).toBeNull()
    expect(encontrarUf(estados.items, null)).toBeNull()
  })

  it('preenche os filtros pela URL, descartando só o que for inválido', () => {
    const padrao = { ano: 2026, mesInicio: 6, mesFim: 8 }
    const completa = {
      cidadeA: '4214805',
      cidadeB: '4202404',
      ano: '2024',
      mesInicio: '1',
      mesFim: '3',
    }

    expect(resolverFiltrosComparacao(periodos, completa, null)).toEqual({
      cidadeA: '4214805',
      cidadeB: '4202404',
      ano: 2024,
      mesInicio: 1,
      mesFim: 3,
    })
    expect(resolverFiltrosComparacao(periodos, { ...completa, mesFim: '9' }, null)).toEqual({
      cidadeA: '4214805',
      cidadeB: '4202404',
      ...padrao,
    })
    expect(
      resolverFiltrosComparacao(periodos, { ...completa, cidadeA: 'abc', cidadeB: '123' }, null),
    ).toMatchObject({ cidadeA: null, cidadeB: null, ano: 2024 })
    expect(
      resolverFiltrosComparacao(periodos, { ...completa, cidadeB: '4214805' }, null),
    ).toMatchObject({ cidadeA: '4214805', cidadeB: null })
  })

  it('sem filtros na URL, usa os últimos da sessão e, sem eles, o padrão', () => {
    const guardados = {
      cidadeA: '4202404',
      cidadeB: '4209102',
      ano: 2023,
      mesInicio: 10,
      mesFim: 12,
    }

    expect(resolverFiltrosComparacao(periodos, {}, guardados)).toEqual(guardados)
    expect(resolverFiltrosComparacao(periodos, { tema: 'escuro' }, guardados)).toEqual(guardados)
    expect(resolverFiltrosComparacao(periodos, { cidadeA: '4214805' }, guardados)).toEqual({
      cidadeA: '4214805',
      cidadeB: null,
      ano: 2026,
      mesInicio: 6,
      mesFim: 8,
    })
    expect(resolverFiltrosComparacao(periodos, {}, null)).toEqual({
      cidadeA: null,
      cidadeB: null,
      ano: 2026,
      mesInicio: 6,
      mesFim: 8,
    })
    expect(resolverFiltrosComparacao(periodos, {}, { ...guardados, ano: 2022 })).toMatchObject({
      cidadeA: '4202404',
      ano: 2026,
      mesInicio: 6,
    })
  })

  it('diz o que falta para gerar o comparativo e monta a consulta e a URL quando está completo', () => {
    const periodo = { ano: 2024, mesInicio: 1, mesFim: 3 }
    const completos = { cidadeA: '4214805', cidadeB: '4202404', ...periodo }

    expect(descreverPendenciaComparacao({ ...completos, cidadeA: null })).toBe('Escolha a cidade A')
    expect(descreverPendenciaComparacao({ ...completos, cidadeB: null })).toBe('Escolha a cidade B')
    expect(descreverPendenciaComparacao(completos)).toBeNull()

    expect(completarFiltrosComparacao({ ...completos, cidadeB: null })).toBeNull()
    expect(completarFiltrosComparacao(completos)).toEqual(completos)

    expect(montarQueryComparacao(completos)).toEqual({
      cidadeA: '4214805',
      cidadeB: '4202404',
      ano: '2024',
      mesInicio: '1',
      mesFim: '3',
    })
    expect(montarQueryComparacao({ ...completos, cidadeB: null })).not.toHaveProperty('cidadeB')
  })
})

describe('filtros da tela de capitais', () => {
  const padrao: EdicaoCapitais = {
    referencia: null,
    capitais: null,
    metrica: 'valor_total',
    ano: 2026,
    mesInicio: 6,
    mesFim: 8,
  }

  it('preenche pela URL, descartando só o que for inválido', () => {
    expect(
      resolverFiltrosCapitais(
        periodos,
        {
          referencia: '4214805',
          ano: '2024',
          mesInicio: '1',
          mesFim: '3',
          capitais: 'SC,PR,RS',
          metrica: 'valor_medio_por_beneficiario',
        },
        null,
      ),
    ).toEqual({
      referencia: '4214805',
      capitais: ['SC', 'PR', 'RS'],
      metrica: 'valor_medio_por_beneficiario',
      ano: 2024,
      mesInicio: 1,
      mesFim: 3,
    })
    expect(
      resolverFiltrosCapitais(
        periodos,
        { referencia: 'abc', capitais: 'sc,XX1,,PR,SC', metrica: 'outra', ano: '2024' },
        null,
      ),
    ).toEqual({ ...padrao, capitais: ['SC', 'PR'] })
    expect(resolverFiltrosCapitais(periodos, { capitais: ',' }, null).capitais).toBeNull()
  })

  it('sem filtros na URL, usa os últimos da sessão e, sem eles, o padrão', () => {
    const guardados: EdicaoCapitais = {
      referencia: '4214805',
      capitais: ['SC', 'PR'],
      metrica: 'beneficiarios_media_mensal',
      ano: 2024,
      mesInicio: 2,
      mesFim: 2,
    }

    expect(resolverFiltrosCapitais(periodos, {}, guardados)).toEqual(guardados)
    expect(resolverFiltrosCapitais(periodos, { referencia: '4205407' }, guardados)).toEqual({
      ...padrao,
      referencia: '4205407',
    })
    expect(resolverFiltrosCapitais(periodos, {}, null)).toEqual(padrao)
  })

  it('explica o que falta, monta a consulta e a URL', () => {
    const completos: EdicaoCapitais = {
      ...padrao,
      referencia: '4214805',
      capitais: ['SC', 'PR', 'RS'],
    }

    expect(descreverPendenciaCapitais(padrao)).toBe('Escolha o município de referência')
    expect(descreverPendenciaCapitais({ ...completos, capitais: [] })).toBe(
      'Escolha ao menos uma UF',
    )
    expect(descreverPendenciaCapitais(completos)).toBeNull()
    expect(completarFiltrosCapitais(padrao)).toBeNull()
    expect(completarFiltrosCapitais({ ...completos, capitais: [] })).toBeNull()
    expect(completarFiltrosCapitais(completos)).toEqual(completos)
    expect(montarQueryCapitais(completos)).toEqual({
      referencia: '4214805',
      capitais: 'SC,PR,RS',
      metrica: 'valor_total',
      ano: '2026',
      mesInicio: '6',
      mesFim: '8',
    })
    expect(montarQueryCapitais({ ...completos, capitais: null })).not.toHaveProperty('capitais')
  })
})
