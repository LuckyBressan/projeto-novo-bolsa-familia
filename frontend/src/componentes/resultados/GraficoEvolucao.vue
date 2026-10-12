<script setup lang="ts">
import Chart from 'primevue/chart'
import { computed } from 'vue'

import { useCoresGrafico } from '@/composables/useCoresGrafico'
import {
  montarDadosEvolucao,
  montarOpcoesEvolucao,
  resumirEvolucao,
  type CampoSerie,
  type SerieGrafico,
} from '@/dominio/graficos'
import { espacoLegenda } from './espacoLegenda'

const props = defineProps<{
  series: SerieGrafico[]
  campo: CampoSerie
}>()

const { cores, animar } = useCoresGrafico()

const dados = computed(() => montarDadosEvolucao(props.series, props.campo, cores.value))
const opcoes = computed(() =>
  montarOpcoesEvolucao(props.series, props.campo, cores.value, { animar: animar.value }),
)
const resumo = computed(() => resumirEvolucao(props.series, props.campo))
</script>

<template>
  <figure class="grafico">
    <div class="grafico__area">
      <Chart
        type="line"
        class="grafico__tela"
        :data="dados"
        :options="opcoes"
        :plugins="[espacoLegenda]"
        :canvas-props="{ role: 'img', 'aria-label': resumo.texto }"
      />
      <p v-if="resumo.vazio" class="grafico__vazio">Sem dados para o período selecionado</p>
    </div>
    <figcaption class="texto-nota">{{ resumo.texto }} Fonte: Portal da Transparência.</figcaption>
  </figure>
</template>

<style scoped>
.grafico {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-2x);
  margin: 0;
  padding: var(--spacing-scale-3x);
  border: var(--surface-width-sm) solid var(--border);
  border-radius: var(--surface-rounder-md);
  background: var(--surface-card);
}

.grafico__area {
  position: relative;
}

.grafico__tela {
  height: 320px;
}

.grafico__vazio {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: var(--color-secondary);
  font-weight: 600;
  pointer-events: none;
}

:root.tema-escuro.alto-contraste .grafico {
  border-width: var(--surface-width-md);
}

@media (max-width: 575px) {
  .grafico {
    padding: var(--spacing-scale-baseh);
  }

  .grafico__tela {
    height: 260px;
  }
}
</style>
