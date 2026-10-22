<script setup lang="ts">
import Select from 'primevue/select'
import Tooltip from 'primevue/tooltip'
import { computed, useId } from 'vue'

import type { Periodos } from '@/api/tipos'
import { formatarMes, nomearMes } from '@/dominio/formatacao'
import {
  ajustarPeriodo,
  listarAnos,
  listarMeses,
  listarOpcoesMesFim,
  type FiltroPeriodo,
} from '@/dominio/periodo'

const props = defineProps<{ periodos: Periodos }>()
const periodo = defineModel<FiltroPeriodo>({ required: true })

const vTooltip = Tooltip
const identificador = useId()

const anos = computed(() => listarAnos(props.periodos))
const mesesInicio = computed(() =>
  listarMeses(props.periodos, periodo.value.ano).map((mes) => ({ mes, nome: nomearMes(mes) })),
)
const mesesFim = computed(() =>
  listarOpcoesMesFim(props.periodos, periodo.value.ano, periodo.value.mesInicio).map((opcao) => ({
    ...opcao,
    nome: nomearMes(opcao.mes),
  })),
)
const regra = computed(
  () =>
    `Até ${props.periodos.max_meses_intervalo} meses do mesmo ano, de ${formatarMes(props.periodos.periodo_min)} a ${formatarMes(props.periodos.periodo_max)}. Os meses fora da regra aparecem desabilitados.`,
)

function alterar(mudanca: Partial<FiltroPeriodo>) {
  periodo.value = ajustarPeriodo(props.periodos, { ...periodo.value, ...mudanca })
}
</script>

<template>
  <fieldset class="periodo">
    <legend class="periodo__titulo">
      Período
      <button
        v-tooltip.top="{ value: regra, autoHide: false, class: 'tooltip-regra' }"
        type="button"
        class="periodo__ajuda"
        aria-label="Regra do período"
        :aria-describedby="`${identificador}-regra`"
      >
        <i class="pi pi-question-circle" aria-hidden="true" />
      </button>
    </legend>
    <div class="periodo__campos">
      <div class="campo">
        <label class="campo__rotulo" :for="`${identificador}-ano`">Ano</label>
        <Select
          :model-value="periodo.ano"
          :options="anos"
          :label-id="`${identificador}-ano`"
          fluid
          @update:model-value="(ano: number) => alterar({ ano })"
        />
      </div>
      <div class="campo">
        <label class="campo__rotulo" :for="`${identificador}-inicio`">De</label>
        <Select
          :model-value="periodo.mesInicio"
          :options="mesesInicio"
          option-value="mes"
          option-label="nome"
          :label-id="`${identificador}-inicio`"
          fluid
          @update:model-value="(mesInicio: number) => alterar({ mesInicio })"
        />
      </div>
      <div class="campo">
        <label class="campo__rotulo" :for="`${identificador}-fim`">Até</label>
        <Select
          :model-value="periodo.mesFim"
          :options="mesesFim"
          option-value="mes"
          option-label="nome"
          option-disabled="desabilitado"
          :label-id="`${identificador}-fim`"
          :aria-describedby="`${identificador}-regra`"
          fluid
          @update:model-value="(mesFim: number) => alterar({ mesFim })"
        />
      </div>
    </div>
    <span :id="`${identificador}-regra`" class="periodo__regra">{{ regra }}</span>
  </fieldset>
</template>

<style scoped>
.periodo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
  min-width: 0;
  margin: 0;
  padding: 0;
  border: 0;
}

.periodo__titulo {
  margin-bottom: var(--spacing-scale-base);
  padding: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.periodo__ajuda {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  margin-left: var(--spacing-scale-half);
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--color-secondary);
  vertical-align: middle;
  cursor: help;
}

.periodo__ajuda:hover {
  color: var(--color);
}

.periodo__ajuda .pi {
  font-size: 1rem;
}

.periodo__regra {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.periodo__campos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--spacing-scale-2x);
}

@media (max-width: 575px) {
  .periodo__campos {
    gap: var(--spacing-scale-base);
  }

  .periodo__campos :deep(.p-select-label) {
    padding-inline: var(--spacing-scale-baseh) 0;
  }

  .periodo__campos :deep(.p-select-dropdown) {
    width: 2rem;
  }
}
</style>
