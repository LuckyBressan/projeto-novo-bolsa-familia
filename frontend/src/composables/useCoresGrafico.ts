import { onBeforeUnmount, onMounted, shallowRef } from 'vue'

import type { CoresGrafico } from '@/dominio/graficos'

const QUANTIDADE_SERIES = 6

function lerCores(): CoresGrafico {
  const raiz = document.documentElement
  const estilo = getComputedStyle(raiz)
  const ler = (nome: string) => estilo.getPropertyValue(nome).trim()
  return {
    series: Array.from({ length: QUANTIDADE_SERIES }, (_, posicao) =>
      ler(`--series-${posicao + 1}`),
    ),
    eixo: ler('--chart-axis'),
    grade: ler('--chart-grid'),
    texto: ler('--color'),
    espessura: raiz.classList.contains('alto-contraste') ? 3 : 2,
  }
}

export function useCoresGrafico() {
  const cores = shallowRef<CoresGrafico>(lerCores())
  const animar = shallowRef(true)
  let observador: MutationObserver | undefined

  onMounted(() => {
    cores.value = lerCores()
    animar.value = !window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    observador = new MutationObserver(() => {
      cores.value = lerCores()
    })
    observador.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
  })

  onBeforeUnmount(() => observador?.disconnect())

  return { cores, animar }
}
