<script setup lang="ts">
import Button from 'primevue/button'
import Select from 'primevue/select'
import { onMounted, ref, shallowRef, useId, watch } from 'vue'

import type { Estado, Municipio } from '@/api/tipos'
import MarcadorSerie from '@/componentes/resultados/MarcadorSerie.vue'
import { useCatalogo } from '@/composables/useCatalogo'
import { encontrarUf } from '@/dominio/filtros'

const props = defineProps<{
  rotulo: string
  posicao: number | null
  bloqueado: string | null
}>()

const codigo = defineModel<string | null>({ required: true })

const ALTURA_OPCAO = 40

const { carregarEstados, carregarMunicipios } = useCatalogo()
const identificador = useId()
const estados = shallowRef<Estado[]>([])
const municipios = shallowRef<Municipio[]>([])
const uf = ref<string | null>(null)
const carregando = ref(false)
const falha = ref(false)

async function carregarUfs() {
  falha.value = false
  try {
    estados.value = await carregarEstados()
    uf.value = encontrarUf(estados.value, codigo.value) ?? uf.value
  } catch {
    falha.value = true
  }
}

async function carregarLista(sigla: string | null) {
  municipios.value = []
  if (!sigla) return
  carregando.value = true
  falha.value = false
  try {
    const lista = await carregarMunicipios(sigla)
    if (uf.value === sigla) municipios.value = lista
  } catch {
    if (uf.value === sigla) falha.value = true
  } finally {
    if (uf.value === sigla) carregando.value = false
  }
}

function escolherUf(sigla: string | null) {
  uf.value = sigla
  if (encontrarUf(estados.value, codigo.value) !== sigla) codigo.value = null
}

function tentarNovamente() {
  if (estados.value.length) carregarLista(uf.value)
  else carregarUfs()
}

watch(codigo, (novo) => {
  const sigla = encontrarUf(estados.value, novo)
  if (sigla) uf.value = sigla
})

watch(uf, carregarLista)

onMounted(carregarUfs)
</script>

<template>
  <fieldset class="seletor">
    <legend class="seletor__titulo">
      <MarcadorSerie v-if="props.posicao !== null" :posicao="props.posicao" />
      {{ props.rotulo }}
    </legend>
    <div class="seletor__campos">
      <div class="campo">
        <label class="campo__rotulo" :for="`${identificador}-uf`">UF</label>
        <Select
          :model-value="uf"
          :options="estados"
          option-value="uf"
          :option-label="(estado: Estado) => `${estado.uf} · ${estado.nome}`"
          :label-id="`${identificador}-uf`"
          placeholder="UF"
          :disabled="!estados.length"
          fluid
          @update:model-value="escolherUf"
        >
          <template #value="{ value, placeholder }">
            {{ value ?? placeholder }}
          </template>
        </Select>
      </div>
      <div class="campo">
        <label class="campo__rotulo" :for="`${identificador}-municipio`">Município</label>
        <Select
          v-model="codigo"
          :options="municipios"
          option-value="codigo_ibge"
          option-label="nome"
          :option-disabled="(municipio: Municipio) => municipio.codigo_ibge === props.bloqueado"
          :label-id="`${identificador}-municipio`"
          :placeholder="uf ? 'Selecione o município' : 'Escolha a UF primeiro'"
          :disabled="!uf"
          :loading="carregando"
          filter
          filter-match-mode="contains"
          filter-locale="pt-BR"
          filter-placeholder="Buscar município"
          auto-filter-focus
          reset-filter-on-hide
          :virtual-scroller-options="{ itemSize: ALTURA_OPCAO }"
          fluid
        >
          <template #option="{ option }">
            <span>{{ option.nome }}</span>
            <span v-if="option.codigo_ibge === props.bloqueado" class="seletor__nota">
              (já escolhido na outra cidade)
            </span>
          </template>
        </Select>
      </div>
    </div>
    <p v-if="falha" class="seletor__falha" role="alert">
      Não foi possível carregar as opções.
      <Button label="Tentar novamente" variant="text" size="small" @click="tentarNovamente" />
    </p>
  </fieldset>
</template>

<style scoped>
.seletor {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
  min-width: 0;
  margin: 0;
  padding: 0;
  border: 0;
}

.seletor__titulo {
  display: flex;
  align-items: center;
  gap: var(--spacing-scale-base);
  margin-bottom: var(--spacing-scale-base);
  padding: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.seletor__campos {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  gap: var(--spacing-scale-2x);
}

.seletor__nota {
  margin-left: var(--spacing-scale-half);
  color: var(--disabled-text);
}

.seletor__falha {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-scale-base);
  color: var(--danger);
}
</style>
