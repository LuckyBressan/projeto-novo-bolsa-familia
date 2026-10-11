import { describe, expect, it } from 'vitest'

import comparacaoParcial from '@mock/comparacao_4202404-x-4209102_2023-10a12_parcial.json'
import type { Indicadores } from '@/api/tipos'
import { descreverStatus } from '@/dominio/status'

const [parcial, disponivel] = comparacaoParcial.municipios.map(
  (entrada) => entrada.indicadores as Indicadores,
)

describe('status do dado', () => {
  it('descreve cada estado com selo, ícone e mensagem próprios', () => {
    expect(descreverStatus(disponivel!)).toEqual({
      severidade: 'success',
      icone: 'pi pi-check',
      rotulo: 'Disponível',
      mensagem: null,
    })
    expect(descreverStatus(parcial!)).toEqual({
      severidade: 'warn',
      icone: 'pi pi-exclamation-triangle',
      rotulo: 'Parcial · 2 de 3 meses',
      mensagem: 'Dados de 2 de 3 meses. Os valores consideram só os meses com dados.',
    })
    expect(descreverStatus({ ...parcial!, status_dado: 'sem_dados', meses_com_dados: 0 })).toEqual({
      severidade: 'secondary',
      icone: 'pi pi-minus',
      rotulo: 'Sem dados',
      mensagem: 'Sem dados para este período.',
    })
    expect(
      descreverStatus({ ...parcial!, status_dado: 'fonte_indisponivel', meses_com_dados: null }),
    ).toEqual({
      severidade: 'danger',
      icone: 'pi pi-times',
      rotulo: 'Fonte indisponível',
      mensagem: 'Não foi possível consultar esta cidade agora.',
    })
  })
})
