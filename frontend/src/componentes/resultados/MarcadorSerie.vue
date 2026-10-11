<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ posicao: number; tamanho?: number }>(), { tamanho: 12 })

const FORMAS = [
  'M1 6a5 5 0 1 0 10 0a5 5 0 1 0 -10 0Z',
  'M6 0.8L11.5 10.8H0.5Z',
  'M1.5 1.5H10.5V10.5H1.5Z',
  'M6 0.5L11.5 6L6 11.5L0.5 6Z',
  'M6 0.5L7.6 4.3L11.7 4.6L8.6 7.3L9.5 11.3L6 9.2L2.5 11.3L3.4 7.3L0.3 4.6L4.4 4.3Z',
  'M2 0.6L6 4.6L10 0.6L11.4 2L7.4 6L11.4 10L10 11.4L6 7.4L2 11.4L0.6 10L4.6 6L0.6 2Z',
]

const forma = computed(() => FORMAS[props.posicao % FORMAS.length])
const cor = computed(() => `var(--series-${(props.posicao % FORMAS.length) + 1})`)
</script>

<template>
  <svg class="marcador" :width="tamanho" :height="tamanho" viewBox="0 0 12 12" aria-hidden="true">
    <path :d="forma" :fill="cor" />
  </svg>
</template>

<style scoped>
.marcador {
  flex: none;
}
</style>
