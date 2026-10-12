<script setup lang="ts">
import Column from 'primevue/column'
import DataTable from 'primevue/datatable'

import SeloStatus from '@/componentes/estado/SeloStatus.vue'
import type { LinhaCapital, TabelaCapitais } from '@/dominio/capitais'
import { formatarInteiro, formatarMoeda, formatarPosicao } from '@/dominio/formatacao'

defineProps<{ tabela: TabelaCapitais }>()

function classificarLinha(linha: LinhaCapital) {
  return linha.referencia ? 'capitais__referencia' : undefined
}
</script>

<template>
  <DataTable
    class="capitais-tabela"
    :value="tabela.capitais"
    :frozen-value="[tabela.referencia]"
    data-key="codigo"
    :row-class="classificarLinha"
    scrollable
    removable-sort
    size="small"
    aria-label="Indicadores de cada capital no período"
  >
    <Column field="posicao" header="#" sortable class="capitais__posicao">
      <template #body="{ data }: { data: LinhaCapital }">
        {{ formatarPosicao(data.posicao) }}
      </template>
    </Column>
    <Column field="nome" header="Capital" sortable frozen class="capitais__nome">
      <template #body="{ data }: { data: LinhaCapital }">
        <strong>{{ data.nome }}</strong>
        <span v-if="data.referencia" class="capitais__marca">referência</span>
      </template>
    </Column>
    <Column field="valorTotal" header="Valor total" sortable class="tabela__numero">
      <template #body="{ data }: { data: LinhaCapital }">
        {{ formatarMoeda(data.valorTotal) }}
      </template>
    </Column>
    <Column field="beneficiarios" header="Benef./mês" sortable class="tabela__numero">
      <template #body="{ data }: { data: LinhaCapital }">
        {{ formatarInteiro(data.beneficiarios) }}
      </template>
    </Column>
    <Column field="valorMedio" header="Valor médio" sortable class="tabela__numero">
      <template #body="{ data }: { data: LinhaCapital }">
        {{ formatarMoeda(data.valorMedio) }}
      </template>
    </Column>
    <Column header="Situação">
      <template #body="{ data }: { data: LinhaCapital }">
        <SeloStatus :situacao="data.situacao" />
      </template>
    </Column>
  </DataTable>
</template>

<style scoped>
.capitais-tabela {
  border: var(--surface-width-sm) solid var(--border);
  border-radius: var(--surface-rounder-md);
  font-size: 0.875rem;
}

.capitais-tabela :deep(.p-datatable-header-cell) {
  border-bottom: var(--surface-width-md) solid var(--border-control);
  background: var(--background-alternative);
  font-weight: 600;
}

.capitais-tabela :deep(.tabela__numero) {
  text-align: right;
  white-space: nowrap;
}

.capitais-tabela :deep(th.tabela__numero .p-datatable-column-header-content) {
  justify-content: flex-end;
}

.capitais-tabela :deep(.capitais__nome) {
  white-space: nowrap;
}

.capitais-tabela :deep(.capitais__referencia),
.capitais-tabela :deep(.capitais__referencia > td) {
  background: var(--interactive-subtle);
}

.capitais__marca {
  margin-left: var(--spacing-scale-base);
  padding: 0 var(--spacing-scale-base);
  border: var(--surface-width-sm) solid var(--border-control);
  border-radius: var(--surface-rounder-pill);
  font-size: 0.75rem;
  font-weight: 600;
}
</style>
