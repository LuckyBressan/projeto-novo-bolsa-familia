<script setup lang="ts">
import MultiSelect from 'primevue/multiselect'
import { computed, useId } from 'vue'

import { LIMITE_CAPITAIS_GRAFICO, type OpcaoCapital } from '@/dominio/capitais'

const props = defineProps<{ opcoes: OpcaoCapital[] }>()

const escolhidas = defineModel<string[]>({ required: true })

const identificador = useId()

const noLimite = computed(() => escolhidas.value.length >= LIMITE_CAPITAIS_GRAFICO)
const rotulo = `Capitais no gráfico (até ${LIMITE_CAPITAIS_GRAFICO})`
</script>

<template>
  <div class="campo capitais-grafico">
    <label class="campo__rotulo" :for="identificador">{{ rotulo }}</label>
    <MultiSelect
      v-model="escolhidas"
      :options="props.opcoes"
      option-value="codigo"
      option-label="nome"
      :input-id="identificador"
      :selection-limit="LIMITE_CAPITAIS_GRAFICO"
      placeholder="Selecione as capitais"
      display="chip"
      filter
      filter-locale="pt-BR"
      filter-placeholder="Buscar capital"
      :show-toggle-all="false"
      fluid
    />
    <span class="texto-nota" aria-live="polite">
      <strong v-if="noLimite">Até {{ LIMITE_CAPITAIS_GRAFICO }} capitais no gráfico.</strong>
      Escolher capitais aqui não faz nova consulta.
    </span>
  </div>
</template>

<style scoped>
.capitais-grafico {
  max-width: 720px;
}
</style>
