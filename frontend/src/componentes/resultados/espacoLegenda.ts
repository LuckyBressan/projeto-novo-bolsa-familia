import type { Chart, Plugin } from 'chart.js'

const FOLGA = 12

export const espacoLegenda: Plugin = {
  id: 'espacoLegenda',
  beforeInit(grafico: Chart) {
    const legenda = grafico.legend
    if (!legenda) return
    const ajustar = legenda.fit
    legenda.fit = function () {
      ajustar.call(this)
      this.height += FOLGA
    }
  },
}
