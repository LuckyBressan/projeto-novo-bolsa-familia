<script setup lang="ts">
import Tag from 'primevue/tag'
import { computed } from 'vue'

import type { Indicadores } from '@/api/tipos'
import { descreverStatus } from '@/dominio/status'

const props = defineProps<{
  situacao: Pick<Indicadores, 'status_dado' | 'meses_com_dados' | 'meses_solicitados'>
}>()

const descricao = computed(() => descreverStatus(props.situacao))
</script>

<template>
  <Tag :severity="descricao.severidade" :icon="descricao.icone" :value="descricao.rotulo" />
</template>
