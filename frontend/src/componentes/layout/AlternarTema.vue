<script setup lang="ts">
import Select from 'primevue/select'
import SelectButton from 'primevue/selectbutton'
import { useId } from 'vue'

import { useTelaEstreita } from '@/composables/useTelaEstreita'
import { useTema } from '@/composables/useTema'
import { OPCOES_TEMA, type EscolhaTema } from '@/dominio/tema'

const LARGURA_LISTA = 991

const { escolha, escolher } = useTema()
const estreita = useTelaEstreita(LARGURA_LISTA)
const identificador = useId()
</script>

<template>
  <div class="tema">
    <label v-if="estreita" class="tema__rotulo" :for="identificador">Tema</label>
    <span v-else :id="identificador" class="tema__rotulo">Tema</span>
    <Select
      v-if="estreita"
      :model-value="escolha"
      :options="OPCOES_TEMA"
      option-value="valor"
      option-label="rotulo"
      :label-id="identificador"
      class="tema__lista"
      @update:model-value="(nova: EscolhaTema) => escolher(nova)"
    />
    <SelectButton
      v-else
      :model-value="escolha"
      :options="OPCOES_TEMA"
      option-value="valor"
      option-label="rotulo"
      :allow-empty="false"
      :aria-labelledby="identificador"
      size="small"
      @update:model-value="(nova: EscolhaTema) => escolher(nova)"
    />
  </div>
</template>

<style scoped>
.tema {
  display: flex;
  align-items: center;
  gap: var(--spacing-scale-base);
}

.tema__rotulo {
  font-size: 0.875rem;
  font-weight: 600;
}

.tema__lista {
  flex: 1;
  min-width: 180px;
}
</style>
