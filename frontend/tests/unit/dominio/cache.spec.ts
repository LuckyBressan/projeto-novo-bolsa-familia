import { describe, expect, it } from 'vitest'

import capitaisTodas from '@mock/capitais_ref-4214805_2024-01a03_todas.json'
import comparacaoParcial from '@mock/comparacao_4202404-x-4209102_2023-10a12_parcial.json'
import comparacaoFalhaFonte from '@mock/comparacao_4209102-x-4214805_2024-10a12_falha-fonte.json'
import {
  adicionarEntrada,
  conferirValidade,
  LIMITE_RESULTADOS,
  montarChaveCache,
  podeGuardar,
  VALIDADE_RESULTADO_MS,
} from '@/dominio/cache'

describe('cache de resultados', () => {
  it('gera a mesma chave para os mesmos parâmetros em outra ordem', () => {
    const chave = montarChaveCache('/evolucao-mensal', { ano: '2024', mes_inicio: '1' }, 'mock')
    const invertida = montarChaveCache('/evolucao-mensal', { mes_inicio: '1', ano: '2024' }, 'mock')

    expect(invertida).toBe(chave)
    expect(montarChaveCache('/evolucao-mensal', { ano: '2025', mes_inicio: '1' }, 'mock')).not.toBe(
      chave,
    )
    expect(
      montarChaveCache('/capitais/comparacao', { ano: '2024', mes_inicio: '1' }, 'mock'),
    ).not.toBe(chave)
  })

  it('separa as chaves do modo mock e do modo real', () => {
    const parametros = { ano: '2024', mes_inicio: '1' }

    expect(montarChaveCache('/evolucao-mensal', parametros, 'mock')).not.toBe(
      montarChaveCache('/evolucao-mensal', parametros, 'real'),
    )
  })

  it('considera válido o resultado de 59 minutos e vencido o de 61', () => {
    const agora = Date.UTC(2026, 9, 11, 15, 0)
    const minutos = (quantidade: number) => quantidade * 60 * 1000

    expect(conferirValidade(agora - minutos(59), agora, VALIDADE_RESULTADO_MS)).toBe(true)
    expect(conferirValidade(agora - minutos(61), agora, VALIDADE_RESULTADO_MS)).toBe(false)
    expect(conferirValidade(agora + minutos(5), agora, VALIDADE_RESULTADO_MS)).toBe(false)
  })

  it('tira o resultado mais antigo ao guardar além do limite de 20', () => {
    const criar = (posicao: number) => ({
      chave: `chave-${posicao}`,
      salvoEm: posicao,
      dados: posicao,
    })
    const cheias = Array.from({ length: LIMITE_RESULTADOS }, (_, posicao) => criar(posicao + 1))

    const entradas = adicionarEntrada(cheias, criar(21))

    expect(entradas).toHaveLength(20)
    expect(entradas.map((entrada) => entrada.chave)).not.toContain('chave-1')
    expect(entradas.at(-1)?.chave).toBe('chave-21')
  })

  it('substitui o resultado guardado com a mesma chave', () => {
    const entradas = adicionarEntrada([{ chave: 'igual', salvoEm: 1, dados: 'antigo' }], {
      chave: 'igual',
      salvoEm: 2,
      dados: 'novo',
    })

    expect(entradas).toEqual([{ chave: 'igual', salvoEm: 2, dados: 'novo' }])
  })

  it('não guarda resposta com alguma entrada de fonte indisponível', () => {
    expect(podeGuardar(comparacaoFalhaFonte)).toBe(false)
    expect(podeGuardar(comparacaoParcial)).toBe(true)
    expect(podeGuardar(capitaisTodas)).toBe(true)
    expect(
      podeGuardar({ series: [{ meses: [{ mes: '2024-10', status_dado: 'fonte_indisponivel' }] }] }),
    ).toBe(false)
  })
})
