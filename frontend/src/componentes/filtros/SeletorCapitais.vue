<script setup lang="ts">
import Button from 'primevue/button'
import MultiSelect from 'primevue/multiselect'
import RadioButton from 'primevue/radiobutton'
import { computed, onMounted, ref, shallowRef, useId, watch } from 'vue'

import type { Estado } from '@/api/tipos'
import { useCatalogo } from '@/composables/useCatalogo'

const capitais = defineModel<string[] | null>({ required: true })

const { carregarEstados } = useCatalogo()
const identificador = useId()
const estados = shallowRef<Estado[]>([])
const falha = ref(false)
const lembradas = ref<string[]>(capitais.value ?? [])

const modo = computed({
  get: () => (capitais.value === null ? 'todas' : 'escolher'),
  set: (novo) => {
    capitais.value = novo === 'todas' ? null : lembradas.value
  },
})

const rotuloTodas = computed(() =>
  estados.value.length ? `Todas as ${estados.value.length}` : 'Todas',
)

async function carregar() {
  falha.value = false
  try {
    estados.value = await carregarEstados()
  } catch {
    falha.value = true
  }
}

watch(capitais, (novas) => {
  if (novas) lembradas.value = novas
})

onMounted(carregar)
</script>

<template>
  <fieldset class="capitais">
    <legend class="capitais__titulo">Capitais</legend>
    <div class="capitais__modos">
      <label class="capitais__modo" :for="`${identificador}-todas`">
        <RadioButton v-model="modo" :input-id="`${identificador}-todas`" value="todas" />
        {{ rotuloTodas }}
      </label>
      <label class="capitais__modo" :for="`${identificador}-escolher`">
        <RadioButton v-model="modo" :input-id="`${identificador}-escolher`" value="escolher" />
        Escolher por UF
      </label>
    </div>
    <div v-if="capitais !== null" class="campo">
      <label class="campo__rotulo" :for="`${identificador}-ufs`">UFs das capitais</label>
      <MultiSelect
        v-model="capitais"
        :options="estados"
        option-value="uf"
        :option-label="(estado: Estado) => `${estado.uf} · ${estado.nome}`"
        :input-id="`${identificador}-ufs`"
        placeholder="Selecione as UFs"
        display="chip"
        filter
        filter-locale="pt-BR"
        filter-placeholder="Buscar UF"
        :show-toggle-all="false"
        :max-selected-labels="8"
        selected-items-label="{0} UFs escolhidas"
        fluid
      />
      <span class="texto-nota">Entra a capital de cada UF escolhida.</span>
    </div>
    <p v-if="falha" class="capitais__falha" role="alert">
      Não foi possível carregar as UFs.
      <Button label="Tentar novamente" variant="text" size="small" @click="carregar" />
    </p>
  </fieldset>
</template>

<style scoped>
.capitais {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
  min-width: 0;
  margin: 0;
  padding: 0;
  border: 0;
}

.capitais__titulo {
  margin-bottom: var(--spacing-scale-base);
  padding: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.capitais__modos {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-scale-base) var(--spacing-scale-3x);
}

.capitais__modo {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-scale-base);
  min-height: var(--spacing-scale-5x);
  cursor: pointer;
}

.capitais__falha {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-scale-base);
  color: var(--danger);
}
</style>
