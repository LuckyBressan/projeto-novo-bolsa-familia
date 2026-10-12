import type { MetricaRanking } from '@/api/tipos'
import type { CampoSerie } from './graficos'

export interface DescricaoMetrica {
  valor: MetricaRanking
  rotulo: string
  tituloRanking: string
  frase: string
  campoMensal: CampoSerie
  nomeMensal: string
}

export const METRICAS: DescricaoMetrica[] = [
  {
    valor: 'valor_total',
    rotulo: 'Valor total recebido',
    tituloRanking: 'Ranking: valor total recebido',
    frase: 'valor total recebido',
    campoMensal: 'valor_total',
    nomeMensal: 'Valor total',
  },
  {
    valor: 'beneficiarios_media_mensal',
    rotulo: 'Beneficiários (média mensal)',
    tituloRanking: 'Ranking: beneficiários (média mensal)',
    frase: 'média mensal de beneficiários',
    campoMensal: 'beneficiarios',
    nomeMensal: 'Beneficiários',
  },
  {
    valor: 'valor_medio_por_beneficiario',
    rotulo: 'Valor médio por beneficiário',
    tituloRanking: 'Ranking: valor médio por beneficiário',
    frase: 'valor médio por beneficiário',
    campoMensal: 'valor_medio_por_beneficiario',
    nomeMensal: 'Valor médio por beneficiário',
  },
]

const METRICA_PADRAO = METRICAS[0] as DescricaoMetrica

export function descreverMetrica(valor: MetricaRanking): DescricaoMetrica {
  return METRICAS.find((metrica) => metrica.valor === valor) ?? METRICA_PADRAO
}
