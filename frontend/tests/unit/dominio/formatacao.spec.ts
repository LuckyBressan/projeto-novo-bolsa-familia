import { describe, expect, it } from 'vitest'

import {
  formatarHora,
  formatarInteiro,
  formatarInteiroCompacto,
  formatarMes,
  formatarMoeda,
  formatarMoedaCompacta,
  formatarPeriodo,
  formatarPosicao,
  formatarVariacao,
  nomearMes,
} from '@/dominio/formatacao'

const normalizar = (texto: string) => texto.replace(/\xa0/g, ' ')

describe('formatação', () => {
  it('formata moeda completa com 2 casas e mostra travessão sem valor', () => {
    expect(normalizar(formatarMoeda(3042086.65))).toBe('R$ 3.042.086,65')
    expect(normalizar(formatarMoeda(665.8))).toBe('R$ 665,80')
    expect(formatarMoeda(null)).toBe('—')
  })

  it('formata moeda compacta em mil, mi e bi', () => {
    expect(normalizar(formatarMoedaCompacta(1384095675.14))).toBe('R$ 1,38 bi')
    expect(normalizar(formatarMoedaCompacta(3042086.65))).toBe('R$ 3,04 mi')
    expect(normalizar(formatarMoedaCompacta(11300000))).toBe('R$ 11,3 mi')
    expect(normalizar(formatarMoedaCompacta(688825))).toBe('R$ 689 mil')
    expect(formatarMoedaCompacta(null)).toBe('—')
  })

  it('arredonda inteiros para exibir e tem a forma compacta', () => {
    expect(formatarInteiro(5773.5)).toBe('5.774')
    expect(formatarInteiro(1582)).toBe('1.582')
    expect(formatarInteiro(null)).toBe('—')
    expect(normalizar(formatarInteiroCompacto(688825))).toBe('689 mil')
    expect(formatarInteiroCompacto(null)).toBe('—')
  })

  it('escreve o mês e o período por extenso', () => {
    expect(formatarMes('2024-01')).toBe('jan/2024')
    expect(formatarMes('2023-12')).toBe('dez/2023')
    expect(formatarPeriodo({ ano: 2024, mesInicio: 1, mesFim: 3 })).toBe('jan/2024 a mar/2024')
    expect(formatarPeriodo({ ano: 2024, mesInicio: 2, mesFim: 2 })).toBe('fev/2024')
    expect(nomearMes(8)).toBe('ago')
  })

  it('mostra a variação com seta e sinal, usando o menos tipográfico', () => {
    expect(formatarVariacao(16)).toBe('▲ +16')
    expect(formatarVariacao(-7)).toBe('▼ −7')
    expect(formatarVariacao(-1234)).toBe('▼ −1.234')
    expect(formatarVariacao(0)).toBe('= 0')
    expect(formatarVariacao(null)).toBe('—')
  })

  it('escreve a hora da consulta com dois dígitos', () => {
    expect(formatarHora(new Date(2026, 9, 11, 15, 40, 59).getTime())).toBe('15:40')
    expect(formatarHora(new Date(2026, 9, 11, 9, 5).getTime())).toBe('09:05')
  })

  it('formata a posição no ranking como ordinal e mostra travessão sem posição', () => {
    expect(formatarPosicao(3)).toBe('3º')
    expect(formatarPosicao(27)).toBe('27º')
    expect(formatarPosicao(null)).toBe('—')
  })
})
