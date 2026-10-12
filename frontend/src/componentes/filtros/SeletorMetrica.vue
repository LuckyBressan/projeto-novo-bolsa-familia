<script setup lang="ts">
import Select from 'primevue/select'
import { useId } from 'vue'

import type { MetricaRanking } from '@/api/tipos'
import { METRICAS } from '@/dominio/metricas'

const metrica = defineModel<MetricaRanking>({ required: true })

const identificador = useId()
</script>

<template>
  <div class="campo">
    <label class="campo__rotulo metrica__rotulo" :for="identificador">Ranking por</label>
    <Select
      v-model="metrica"
      :options="METRICAS"
      option-value="valor"
      option-label="rotulo"
      :label-id="identificador"
      fluid
    />
  </div>
</template>

<style scoped>
.metrica__rotulo {
  margin-bottom: var(--spacing-scale-base);
  font-size: 1.05rem;
  font-weight: 700;
}
</style>
