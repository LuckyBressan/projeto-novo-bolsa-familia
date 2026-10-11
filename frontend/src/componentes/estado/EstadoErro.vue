<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import { computed } from 'vue'

import { descreverErro, type ErroConsulta } from '@/api/erros'
import { usePeriodos } from '@/composables/usePeriodos'

const props = defineProps<{ erro: ErroConsulta }>()
defineEmits<{ tentarNovamente: [] }>()

const { periodos } = usePeriodos()
const descricao = computed(() => descreverErro(props.erro, periodos.value))
</script>

<template>
  <Message class="erro" severity="error" :closable="false" role="alert">
    <template #icon>
      <span class="erro__icone" aria-hidden="true">×</span>
    </template>
    <div class="erro__corpo">
      <strong>{{ descricao.mensagem }}</strong>
      <span v-if="erro.correlacaoId" class="texto-nota">
        Código para suporte: {{ erro.correlacaoId }}
      </span>
      <div v-if="descricao.acao === 'tentar_novamente'">
        <Button
          label="Tentar novamente"
          severity="secondary"
          variant="outlined"
          @click="$emit('tentarNovamente')"
        />
      </div>
    </div>
  </Message>
</template>

<style scoped>
.erro :deep(.p-message-content) {
  align-items: flex-start;
}

.erro__icone {
  display: grid;
  place-items: center;
  flex: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--danger);
  color: var(--on-danger);
  font-size: 1rem;
  font-weight: 800;
  line-height: 1;
}

.erro__corpo {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
}
</style>
