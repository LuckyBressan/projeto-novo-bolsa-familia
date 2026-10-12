<script setup lang="ts">
import Tag from 'primevue/tag'
import { computed } from 'vue'

import type { MetricaRanking, Referencia } from '@/api/tipos'
import SeloStatus from '@/componentes/estado/SeloStatus.vue'
import CardIndicador from '@/componentes/resultados/CardIndicador.vue'
import { montarCards } from '@/dominio/indicadores'
import { METRICAS } from '@/dominio/metricas'
import type { FiltroPeriodo } from '@/dominio/periodo'
import type { DescricaoPosicao } from '@/dominio/ranking'
import { descreverStatus } from '@/dominio/status'

const props = defineProps<{
  referencia: Referencia
  posicao: DescricaoPosicao
  periodo: FiltroPeriodo
  metrica: MetricaRanking
}>()

const cards = computed(() =>
  montarCards(props.referencia.indicadores, props.periodo).map((card, indice) => ({
    ...card,
    ranqueada: METRICAS[indice]?.valor === props.metrica,
  })),
)

const mensagem = computed(() => descreverStatus(props.referencia.indicadores).mensagem)
</script>

<template>
  <div class="resumo">
    <div class="resumo__posicao">
      <span class="resumo__destaque">{{ posicao.destaque }}</span>
      <p class="resumo__frase">{{ posicao.frase }}</p>
      <SeloStatus :situacao="referencia.indicadores" />
    </div>
    <p v-if="mensagem" class="resumo__mensagem">{{ mensagem }}</p>
    <div class="resumo__cards">
      <CardIndicador
        v-for="card in cards"
        :key="card.titulo"
        v-bind="card"
        :nivel="3"
        :class="{ 'resumo__card--ranqueada': card.ranqueada }"
      >
        <template #titulo>
          {{ card.titulo }}
          <Tag v-if="card.ranqueada" severity="info" value="Métrica do ranking" />
        </template>
      </CardIndicador>
    </div>
  </div>
</template>

<style scoped>
.resumo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-3x);
}

.resumo__posicao {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-scale-base) var(--spacing-scale-2x);
  padding: var(--spacing-scale-2x) var(--spacing-scale-3x);
  border: var(--surface-width-sm) solid transparent;
  border-radius: var(--surface-rounder-md);
  background: var(--interactive-subtle);
}

.resumo__destaque {
  font-size: 2.613rem;
  font-weight: 700;
  line-height: 1;
}

.resumo__frase {
  flex: 1 1 280px;
  font-size: 1.05rem;
}

.resumo__mensagem {
  color: var(--color-secondary);
}

.resumo__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--spacing-scale-3x);
}

.resumo__card--ranqueada {
  border-color: var(--interactive);
  border-width: var(--surface-width-md);
}

.resumo :deep(.indicador__titulo) {
  flex-wrap: wrap;
  justify-content: space-between;
}

:root.tema-escuro.alto-contraste .resumo__posicao {
  border-color: var(--border-control);
  border-width: var(--surface-width-md);
}
</style>
