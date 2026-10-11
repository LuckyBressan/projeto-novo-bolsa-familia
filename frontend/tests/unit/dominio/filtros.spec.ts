import { describe, expect, it } from 'vitest'

import estados from '@mock/estados.json'
import periodos from '@mock/periodos.json'
import {
  completarFiltrosComparacao,
  descreverPendenciaComparacao,
  encontrarUf,
  montarQueryComparacao,
  resolverFiltrosComparacao,
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
