<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { consultaComparacao, consultaEvolucao } from '@/api/rotas'
import EstadoCarregando from '@/componentes/estado/EstadoCarregando.vue'
import EstadoErro from '@/componentes/estado/EstadoErro.vue'
import EstadoInicial from '@/componentes/estado/EstadoInicial.vue'
import SecaoResultado from '@/componentes/estado/SecaoResultado.vue'
import SeletorMunicipio from '@/componentes/filtros/SeletorMunicipio.vue'
import SeletorPeriodo from '@/componentes/filtros/SeletorPeriodo.vue'
import GraficoEvolucao from '@/componentes/resultados/GraficoEvolucao.vue'
import GrupoCards from '@/componentes/resultados/GrupoCards.vue'
import TabelaDadosGrafico from '@/componentes/resultados/TabelaDadosGrafico.vue'
import TabelaVariacao from '@/componentes/resultados/TabelaVariacao.vue'
import { useCacheResultados } from '@/composables/useCacheResultados'
import { useConsulta } from '@/composables/useConsulta'
import { useModoMock } from '@/composables/useModoMock'
import { usePeriodos } from '@/composables/usePeriodos'
import {
  completarFiltrosComparacao,
  descreverPendenciaComparacao,
  montarQueryComparacao,
  resolverFiltrosComparacao,
  type EdicaoComparacao,
} from '@/dominio/filtros'
import { formatarHora, formatarPeriodo } from '@/dominio/formatacao'
import { criarSeriesCidades, montarTabelaDados, montarVariacao } from '@/dominio/graficos'
import type { FiltroPeriodo } from '@/dominio/periodo'

const SECAO_INDICADORES = 'secao-indicadores'
const ESPERA_AVISO_MS = 3000

const rota = useRoute()
const router = useRouter()
const cache = useCacheResultados()
const { carregar: carregarModo } = useModoMock()
const { periodos, erro: erroPeriodos, carregar: carregarPeriodos } = usePeriodos()
const comparacao = useConsulta(consultaComparacao)
const evolucao = useConsulta(consultaEvolucao)

const filtros = ref<EdicaoComparacao | null>(null)

const periodo = computed<FiltroPeriodo | null>({
  get: () =>
    filtros.value && {
      ano: filtros.value.ano,
      mesInicio: filtros.value.mesInicio,
      mesFim: filtros.value.mesFim,
    },
  set: (novo) => {
    if (filtros.value && novo) filtros.value = { ...filtros.value, ...novo }
  },
})

const pendencia = computed(() =>
  filtros.value ? descreverPendenciaComparacao(filtros.value) : 'Carregando as opções…',
)

const resultado = computed(() => {
  const dados = comparacao.dados.value
  if (!dados) return null
  const intervalo = {
    ano: dados.periodo.ano,
    mesInicio: dados.periodo.mes_inicio,
    mesFim: dados.periodo.mes_fim,
  }
  const quantidade = dados.periodo.meses.length
  return {
    entradas: dados.municipios,
    intervalo,
    cidades: dados.municipios
      .map((entrada) => `${entrada.municipio.nome} (${entrada.municipio.uf})`)
      .join(' × '),
    periodo: formatarPeriodo(intervalo),
    meses: quantidade === 1 ? '1 mês' : `${quantidade} meses`,
  }
})

const consultadoAs = computed(() => {
  const momento = comparacao.consultadoEm.value
  if (momento === null) return null
  const base = `Resultado consultado às ${formatarHora(momento)}.`
  return comparacao.origemCache.value
    ? `${base} Clique em Gerar comparativo para consultar de novo.`
    : base
})

const carregando = computed(() => comparacao.carregando.value || evolucao.carregando.value)

const series = computed(() =>
  evolucao.dados.value ? criarSeriesCidades(evolucao.dados.value.series) : null,
)

const tabelas = computed(() =>
  series.value
    ? {
        valor: montarTabelaDados(series.value, 'valor_total'),
        beneficiarios: montarTabelaDados(series.value, 'beneficiarios'),
        variacao: montarVariacao(series.value),
      }
    : null,
)

const mostrarEvolucao = computed(
  () => Boolean(evolucao.dados.value || evolucao.erro.value) || evolucao.carregando.value,
)

const filtrosMudaram = computed(() => {
  const consultados = comparacao.filtrosResultado.value ?? evolucao.filtrosResultado.value
  if (!consultados || !filtros.value) return false
  return (
    JSON.stringify(montarQueryComparacao(consultados)) !==
    JSON.stringify(montarQueryComparacao(filtros.value))
  )
})

const mostrarInicial = computed(
  () =>
    !carregando.value &&
    !comparacao.dados.value &&
    !comparacao.erro.value &&
    !mostrarEvolucao.value,
)

function cancelar() {
  comparacao.cancelar()
  evolucao.cancelar()
}

function refazerEvolucao() {
  const consultados =
    comparacao.filtrosResultado.value ??
    (filtros.value && completarFiltrosComparacao(filtros.value))
  if (consultados) evolucao.executar(consultados)
}

async function gerar() {
  if (!filtros.value) return
  const completos = completarFiltrosComparacao(filtros.value)
  if (!completos) return
  cache.guardarFiltros('comparacao', filtros.value)
  router.replace({ query: montarQueryComparacao(filtros.value) })
  await Promise.all([comparacao.executar(completos), evolucao.executar(completos)])
  if (!comparacao.dados.value) return
  await nextTick()
  document.getElementById(SECAO_INDICADORES)?.focus()
}

watch(
  periodos,
  async (disponiveis) => {
    if (!disponiveis || filtros.value) return
    await carregarModo()
    const iniciais = resolverFiltrosComparacao(
      disponiveis,
      rota.query,
      cache.lerFiltros('comparacao'),
    )
    filtros.value = iniciais
    const completos = completarFiltrosComparacao(iniciais)
    if (!completos) return
    comparacao.restaurar(completos)
    evolucao.restaurar(completos)
  },
  { immediate: true },
)
</script>

<template>
  <div class="abertura-tela">
    <h1>Comparar cidades</h1>
    <p class="texto-apoio">
      Compare o Novo Bolsa Família de dois municípios em até 3 meses do mesmo ano.
    </p>
  </div>

  <EstadoErro v-if="erroPeriodos" :erro="erroPeriodos" @tentar-novamente="carregarPeriodos" />

  <form v-else class="filtros" aria-label="Filtros" @submit.prevent="gerar">
    <template v-if="filtros && periodos && periodo">
      <div class="filtros__cidades">
        <SeletorMunicipio
          v-model="filtros.cidadeA"
          rotulo="Cidade A"
          :posicao="0"
          :bloqueado="filtros.cidadeB"
        />
        <SeletorMunicipio
          v-model="filtros.cidadeB"
          rotulo="Cidade B"
          :posicao="1"
          :bloqueado="filtros.cidadeA"
        />
      </div>
      <div class="filtros__rodape">
        <SeletorPeriodo v-model="periodo" class="filtros__periodo" :periodos="periodos" />
        <div class="filtros__acoes">
          <span v-if="pendencia" id="motivo-pendencia" class="filtros__motivo">{{
            pendencia
          }}</span>
          <Button
            v-if="carregando"
            label="Cancelar"
            variant="text"
            type="button"
            @click="cancelar"
          />
          <Button
            type="submit"
            :label="carregando ? 'Consultando…' : 'Gerar comparativo'"
            :loading="carregando"
            :disabled="Boolean(pendencia)"
            :aria-describedby="pendencia ? 'motivo-pendencia' : undefined"
          />
        </div>
      </div>
    </template>
    <div v-else class="filtros__espera" aria-hidden="true">
      <Skeleton height="4.5rem" />
      <Skeleton height="4.5rem" />
    </div>
  </form>

  <div class="avisos" aria-live="polite">
    <Message v-if="filtrosMudaram && resultado" severity="info" :closable="false">
      <strong>Os filtros mudaram.</strong> Clique em Gerar comparativo para atualizar. O resultado
      abaixo ainda é de {{ resultado.cidades }}, {{ resultado.periodo }}.
    </Message>
    <EstadoCarregando
      v-if="carregando"
      mensagem="Consultando o Portal da Transparência…"
      mensagem-demora="As duas cidades são consultadas ao mesmo tempo. Você pode esperar ou cancelar."
      :apos-ms="ESPERA_AVISO_MS"
    />
  </div>

  <EstadoInicial
    v-if="mostrarInicial"
    complemento="Nada é consultado antes disso. Os resultados aparecem aqui, em seções."
  />

  <div v-else class="resultados">
    <SecaoResultado
      :identificador="SECAO_INDICADORES"
      titulo="Indicadores do período"
      :carregando="comparacao.carregando.value"
      :erro="comparacao.erro.value"
      @tentar-novamente="gerar"
    >
      <template v-if="resultado && !comparacao.carregando.value" #resumo>
        <p class="resultados__resumo">
          <strong>{{ resultado.cidades }}</strong> · {{ resultado.periodo }} · {{ resultado.meses }}
        </p>
        <p v-if="consultadoAs" class="texto-nota">{{ consultadoAs }}</p>
      </template>
      <template #carregando>
        <div class="resultados__espera">
          <Skeleton v-for="indice in 2" :key="indice" height="9rem" />
        </div>
      </template>
      <GrupoCards
        v-if="resultado"
        :entradas="resultado.entradas"
        :periodo="resultado.intervalo"
        @tentar-novamente="gerar"
      />
    </SecaoResultado>

    <template v-if="mostrarEvolucao">
      <SecaoResultado
        identificador="secao-valor"
        titulo="Evolução do valor total"
        descricao="Quanto cada cidade recebeu em cada mês do período."
        :carregando="evolucao.carregando.value"
        :erro="evolucao.erro.value"
        @tentar-novamente="refazerEvolucao"
      >
        <template #carregando>
          <Skeleton height="20rem" />
        </template>
        <template v-if="series && tabelas">
          <GraficoEvolucao :series="series" campo="valor_total" />
          <TabelaDadosGrafico legenda="Valor total recebido por mês" :tabela="tabelas.valor" />
        </template>
      </SecaoResultado>

      <SecaoResultado
        identificador="secao-beneficiarios"
        titulo="Evolução dos beneficiários"
        descricao="Quantas pessoas receberam em cada mês e quanto isso variou de um mês para o outro."
        :carregando="evolucao.carregando.value"
        :erro="evolucao.erro.value"
        @tentar-novamente="refazerEvolucao"
      >
        <template #carregando>
          <Skeleton height="20rem" />
        </template>
        <template v-if="series && tabelas">
          <GraficoEvolucao :series="series" campo="beneficiarios" />
          <TabelaVariacao :linhas="tabelas.variacao" />
          <TabelaDadosGrafico legenda="Beneficiários por mês" :tabela="tabelas.beneficiarios" />
        </template>
      </SecaoResultado>
    </template>
  </div>
</template>

<style scoped>
.filtros {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-3x);
  padding: var(--spacing-scale-3x);
  border: var(--surface-width-sm) solid var(--border);
  border-radius: var(--surface-rounder-md);
  background: var(--background-alternative);
}

.filtros__cidades {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-scale-3x);
}

.filtros__cidades > * {
  flex: 1 1 340px;
}

.filtros__rodape {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--spacing-scale-3x);
}

.filtros__periodo {
  flex: 1 1 340px;
  max-width: 560px;
}

.filtros__acoes {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-scale-baseh) var(--spacing-scale-2x);
}

.filtros__motivo {
  color: var(--color-secondary);
}

.filtros__espera,
.resultados__espera {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-scale-3x);
}

.avisos {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-2x);
}

.avisos:empty {
  display: none;
}

.resultados {
  display: flex;
  flex-direction: column;
}

.resultados__resumo {
  font-size: 1.05rem;
}

:root.tema-escuro.alto-contraste .filtros {
  border-width: var(--surface-width-md);
}

@media (max-width: 575px) {
  .filtros {
    padding: var(--spacing-scale-2x);
  }

  .filtros__acoes {
    width: 100%;
  }

  .filtros__acoes :deep(.p-button[type='submit']) {
    width: 100%;
  }
}
</style>
