import type { MetricaRanking } from '@/api/tipos'
import type { FiltroPeriodo } from './periodo'

export interface FiltrosComparacao extends FiltroPeriodo {
  cidadeA: string
  cidadeB: string
}

export interface FiltrosCapitais extends FiltroPeriodo {
  referencia: string
  capitais: string[] | null
  metrica: MetricaRanking
}
