import { describe, expect, it } from 'vitest'

import periodos from '@mock/periodos.json'
import { CODIGOS_FRONT, descreverErro, ErroConsulta } from '@/api/erros'

const criar = (codigo: string) => new ErroConsulta({ codigo, httpStatus: 422, correlacaoId: 'abc' })

describe('erros da consulta', () => {
  it('troca cada código do contrato pela mensagem e pela ação da tela', () => {
    const esperado: Record<string, [string, string]> = {
      PARAMETRO_INVALIDO: [
        'Algum filtro está incompleto ou inválido. Revise os campos destacados.',
        'revisar_filtros',
      ],
      PERIODO_INVALIDO: [
        'Escolha de 1 a 3 meses do mesmo ano, entre mar/2023 e ago/2026.',
        'revisar_filtros',
      ],
      ESTADO_INVALIDO: ['Estado não reconhecido.', 'revisar_filtros'],
      MUNICIPIO_INVALIDO: ['Município não encontrado.', 'revisar_filtros'],
      METRICA_INVALIDA: ['Métrica de ranking não reconhecida.', 'revisar_filtros'],
      FONTE_INDISPONIVEL: [
        'O Portal da Transparência não respondeu agora. Tente novamente em alguns instantes.',
        'tentar_novamente',
      ],
      LIMITE_FONTE_EXCEDIDO: [
        'Muitas consultas ao Portal em pouco tempo. Aguarde um minuto e tente novamente.',
        'tentar_novamente',
      ],
      RESPOSTA_FONTE_INVALIDA: ['O Portal respondeu de forma inesperada.', 'tentar_novamente'],
      ERRO_INTERNO: ['Ocorreu um erro inesperado.', 'tentar_novamente'],
    }

    for (const [codigo, [mensagem, acao]] of Object.entries(esperado)) {
      expect(descreverErro(criar(codigo), periodos)).toEqual({ mensagem, acao })
    }
  })

  it('usa a mensagem genérica para código desconhecido', () => {
    expect(descreverErro(criar('CODIGO_NOVO'), periodos)).toEqual({
      mensagem: 'Ocorreu um erro inesperado.',
      acao: 'tentar_novamente',
    })
  })

  it('distingue tempo esgotado, falta de conexão e cancelamento', () => {
    const tempoEsgotado = new ErroConsulta({ codigo: CODIGOS_FRONT.tempoEsgotado })
    const semConexao = new ErroConsulta({ codigo: CODIGOS_FRONT.semConexao })
    const cancelada = new ErroConsulta({ codigo: CODIGOS_FRONT.cancelada })

    expect(descreverErro(tempoEsgotado).mensagem).toBe('A consulta demorou mais que o esperado.')
    expect(descreverErro(semConexao).mensagem).toBe(
      'Não foi possível falar com o servidor do sistema.',
    )
    expect(descreverErro(tempoEsgotado).acao).toBe('tentar_novamente')
    expect(descreverErro(semConexao).acao).toBe('tentar_novamente')
    expect([tempoEsgotado.cancelada, semConexao.cancelada, cancelada.cancelada]).toEqual([
      false,
      false,
      true,
    ])
  })
})
