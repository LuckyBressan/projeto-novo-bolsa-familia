import { describe, expect, it } from 'vitest'

import periodos from '@mock/periodos.json'
import {
  ajustarPeriodo,
  calcularPeriodoPadrao,
  lerPeriodoQuery,
  listarAnos,
  listarMeses,
  listarOpcoesMesFim,
} from '@/dominio/periodo'

describe('período', () => {
  it('oferece os anos de 2023 a 2026', () => {
    expect(listarAnos(periodos)).toEqual([2023, 2024, 2025, 2026])
  })

  it('começa 2023 em março e termina 2026 em agosto', () => {
    expect(listarMeses(periodos, 2023)[0]).toBe(3)
    expect(listarMeses(periodos, 2026).at(-1)).toBe(8)
    expect(listarMeses(periodos, 2030)).toEqual([])
  })

  it('desabilita no mês final o que passa de 3 meses ou vem antes do inicial', () => {
    const habilitados = (ano: number, mesInicio: number) =>
      listarOpcoesMesFim(periodos, ano, mesInicio)
        .filter((opcao) => !opcao.desabilitado)
        .map((opcao) => opcao.mes)

    expect(habilitados(2024, 1)).toEqual([1, 2, 3])
    expect(listarOpcoesMesFim(periodos, 2024, 1)).toContainEqual({ mes: 4, desabilitado: true })
    expect(habilitados(2026, 7)).toEqual([7, 8])
    expect(habilitados(2024, 5)).toEqual([5, 6, 7])
  })

  it('leva o mês inicial para o mês válido mais próximo quando o ano não tem aquele mês', () => {
    expect(ajustarPeriodo(periodos, { ano: 2023, mesInicio: 2, mesFim: 2 })).toEqual({
      ano: 2023,
      mesInicio: 3,
      mesFim: 3,
    })
    expect(ajustarPeriodo(periodos, { ano: 2026, mesInicio: 11, mesFim: 12 })).toEqual({
      ano: 2026,
      mesInicio: 8,
      mesFim: 8,
    })
  })

  it('mantém o mês final entre o inicial e o limite de 3 meses', () => {
    expect(ajustarPeriodo(periodos, { ano: 2024, mesInicio: 5, mesFim: 2 }).mesFim).toBe(5)
    expect(ajustarPeriodo(periodos, { ano: 2024, mesInicio: 1, mesFim: 9 }).mesFim).toBe(3)
    expect(ajustarPeriodo(periodos, { ano: 2024, mesInicio: 4, mesFim: 6 }).mesFim).toBe(6)
  })

  it('usa como padrão os últimos 3 meses disponíveis, sem sair do ano', () => {
    expect(calcularPeriodoPadrao(periodos)).toEqual({ ano: 2026, mesInicio: 6, mesFim: 8 })

    const anoRecente = { ...periodos, anos: [...periodos.anos, { ano: 2027, meses: [1, 2] }] }
    expect(calcularPeriodoPadrao(anoRecente)).toEqual({ ano: 2027, mesInicio: 1, mesFim: 2 })
  })

  it('lê o período da query string e descarta o que for inválido', () => {
    expect(lerPeriodoQuery(periodos, { ano: '2024', mesInicio: '1', mesFim: '3' })).toEqual({
      ano: 2024,
      mesInicio: 1,
      mesFim: 3,
    })
    expect(lerPeriodoQuery(periodos, { ano: '2024', mesInicio: '1', mesFim: '9' })).toBeNull()
    expect(lerPeriodoQuery(periodos, { ano: '2023', mesInicio: '1', mesFim: '2' })).toBeNull()
    expect(lerPeriodoQuery(periodos, { ano: '2024', mesInicio: '3', mesFim: '2' })).toBeNull()
    expect(lerPeriodoQuery(periodos, { ano: 'abc', mesInicio: '1', mesFim: '2' })).toBeNull()
    expect(lerPeriodoQuery(periodos, { ano: '2024', mesInicio: '1.5', mesFim: '2' })).toBeNull()
    expect(lerPeriodoQuery(periodos, { ano: '2024' })).toBeNull()
  })
})
