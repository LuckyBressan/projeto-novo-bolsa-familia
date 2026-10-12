<script setup lang="ts">
import Chart from 'primevue/chart'
import Tag from 'primevue/tag'
import { computed } from 'vue'

import { useCoresGrafico } from '@/composables/useCoresGrafico'
import {
  montarDadosRanking,
  montarOpcoesRanking,
  resumirRanking,
  type Ranking,
} from '@/dominio/ranking'

const props = defineProps<{ ranking: Ranking }>()

const ALTURA_BARRA = 28
const ALTURA_EIXO = 56

const { cores, animar } = useCoresGrafico()

const dados = computed(() => montarDadosRanking(props.ranking, cores.value))
const opcoes = computed(() =>
  montarOpcoesRanking(props.ranking, cores.value, { animar: animar.value }),
)
const resumo = computed(() => resumirRanking(props.ranking))
const altura = computed(() => `${props.ranking.barras.length * ALTURA_BARRA + ALTURA_EIXO}px`)
const destacada = computed(() => props.ranking.barras.some((barra) => barra.referencia))
</script>

<template>
  <figure class="ranking">
    <div class="ranking__topo">
      <h3 class="ranking__titulo">{{ ranking.metrica.tituloRanking }}</h3>
      <ul class="ranking__legenda">
        <li><span class="ranking__cor ranking__cor--capital" aria-hidden="true" />Capital</li>
        <li v-if="destacada">
          <span class="ranking__cor ranking__cor--referencia" aria-hidden="true" />
          Município de referência
        </li>
      </ul>
    </div>
    <div v-if="ranking.barras.length" class="ranking__area" :style="{ height: altura }">
      <Chart
        type="bar"
        class="ranking__tela"
        :data="dados"
        :options="opcoes"
        :canvas-props="{ role: 'img', 'aria-label': resumo }"
      />
    </div>
    <p v-else class="ranking__vazio">Sem dados para o período selecionado</p>
    <p v-if="ranking.semPosicao.length" class="ranking__fora">
      <Tag severity="secondary" icon="pi pi-minus" value="Fora do ranking" />
      Sem posição no ranking: {{ ranking.semPosicao.join(', ') }}.
    </p>
    <figcaption class="texto-nota">
      Passe o cursor sobre uma barra para ver o valor completo. Fonte: Portal da Transparência.
    </figcaption>
  </figure>
</template>

<style scoped>
.ranking {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-2x);
  margin: 0;
  padding: var(--spacing-scale-3x);
  border: var(--surface-width-sm) solid var(--border);
  border-radius: var(--surface-rounder-md);
  background: var(--surface-card);
}

.ranking__topo {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-scale-baseh);
}

.ranking__titulo {
  font-size: 1.05rem;
  font-weight: 600;
}

.ranking__legenda {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-scale-base) var(--spacing-scale-3x);
  margin: 0;
  padding: 0;
  font-weight: 600;
  list-style: none;
}

.ranking__legenda li {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-scale-base);
}

.ranking__cor {
  width: 16px;
  height: 12px;
  border-radius: 2px;
}

.ranking__cor--capital {
  background: var(--series-1);
}

.ranking__cor--referencia {
  border: var(--surface-width-md) solid var(--color);
  background: var(--series-2);
}

.ranking__area {
  position: relative;
}

.ranking__tela {
  height: 100%;
}

.ranking__vazio {
  padding-block: var(--spacing-scale-6x);
  color: var(--color-secondary);
  font-weight: 600;
  text-align: center;
}

.ranking__fora {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-scale-base);
}

:root.tema-escuro.alto-contraste .ranking {
  border-width: var(--surface-width-md);
}

@media (max-width: 575px) {
  .ranking {
    padding: var(--spacing-scale-baseh);
  }
}
</style>
