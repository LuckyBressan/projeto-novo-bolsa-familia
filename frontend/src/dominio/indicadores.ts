import type { Indicadores } from '@/api/tipos'
import {
  formatarInteiro,
  formatarMoeda,
  formatarMoedaCompacta,
  formatarPeriodo,
} from './formatacao'
import type { FiltroPeriodo } from './periodo'

export interface CardIndicador {
  titulo: string
  valor: string
  valorCompacto: string
  complemento: string
}

export function montarCards(indicadores: Indicadores, periodo: FiltroPeriodo): CardIndicador[] {
  const mesUnico = periodo.mesInicio === periodo.mesFim
  const intervalo = formatarPeriodo(periodo)
  return [
    {
      titulo: 'Valor total recebido',
      valor: formatarMoeda(indicadores.valor_total),
      valorCompacto: formatarMoedaCompacta(indicadores.valor_total),
      complemento: mesUnico ? `Valor de ${intervalo}` : `Soma de ${intervalo}`,
    },
    {
      titulo: mesUnico ? 'Beneficiários no mês' : 'Beneficiários (média mensal)',
      valor: formatarInteiro(indicadores.beneficiarios_media_mensal),
      valorCompacto: formatarInteiro(indicadores.beneficiarios_media_mensal),
      complemento: mesUnico ? 'Pessoas que receberam no mês' : 'Média de pessoas por mês',
    },
    {
      titulo: 'Valor médio por beneficiário (por mês)',
      valor: formatarMoeda(indicadores.valor_medio_por_beneficiario),
      valorCompacto: formatarMoeda(indicadores.valor_medio_por_beneficiario),
      complemento: `Quanto cada pessoa recebeu, em média, ${mesUnico ? 'no' : 'por'} mês`,
    },
  ]
}
