import { describe, expect, it } from 'vitest'

import rotasMock from '@mock/_rotas.json'
import {
  consultaCapitais,
  consultaComparacao,
  consultaEvolucao,
  type DefinicaoConsulta,
} from '@/api/rotas'

function decompor(url: string) {
  const [caminho, consulta = ''] = url.split('?')
  return { caminho, parametros: Object.fromEntries(new URLSearchParams(consulta)) }
}

function rotaMock(arquivo: string) {
  const rota = rotasMock.find((item) => item.arquivo === arquivo)?.rota ?? ''
  return decompor(rota)
}

function montar<Filtros>(definicao: DefinicaoConsulta<Filtros, unknown>, filtros: Filtros) {
  return { caminho: `/api/v1${definicao.rota}`, parametros: definicao.montarParametros(filtros) }
}

describe('rotas da API', () => {
  it('monta comparação e evolução como o contrato do mock registra', () => {
    const filtros = { cidadeA: '4214805', cidadeB: '4202404', ano: 2024, mesInicio: 1, mesFim: 3 }

    expect(montar(consultaComparacao, filtros)).toEqual(
      rotaMock('comparacao_4214805-x-4202404_2024-01a03.json'),
    )
    expect(montar(consultaEvolucao, filtros)).toEqual(
      rotaMock('evolucao_4214805-x-4202404_2024-01a03.json'),
    )
  })

  it('monta a consulta das capitais com a métrica e só envia o filtro quando há UFs', () => {
    const periodo = { referencia: '4214805', ano: 2024, mesInicio: 1, mesFim: 3 }
    const todas = rotaMock('capitais_ref-4214805_2024-01a03_todas.json')

    expect(
      montar(consultaCapitais, { ...periodo, capitais: null, metrica: 'valor_total' }),
    ).toEqual({
      caminho: todas.caminho,
      parametros: { ...todas.parametros, metrica: 'valor_total' },
    })
    expect(
      montar(consultaCapitais, {
        ...periodo,
        capitais: ['SC', 'PR', 'RS'],
        metrica: 'valor_medio_por_beneficiario',
      }),
    ).toEqual(rotaMock('capitais_ref-4214805_2024-01a03_SC-PR-RS_valor-medio.json'))
  })
})
