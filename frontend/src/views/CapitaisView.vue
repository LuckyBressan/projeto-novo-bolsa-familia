<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { consultaCapitais } from '@/api/rotas'
import type { ComparacaoCapitais } from '@/api/tipos'
import EstadoCarregando from '@/componentes/estado/EstadoCarregando.vue'
import EstadoErro from '@/componentes/estado/EstadoErro.vue'
import EstadoInicial from '@/componentes/estado/EstadoInicial.vue'
import SecaoResultado from '@/componentes/estado/SecaoResultado.vue'
import SeletorCapitais from '@/componentes/filtros/SeletorCapitais.vue'
import SeletorMetrica from '@/componentes/filtros/SeletorMetrica.vue'
import SeletorMunicipio from '@/componentes/filtros/SeletorMunicipio.vue'
import SeletorPeriodo from '@/componentes/filtros/SeletorPeriodo.vue'
import GraficoEvolucao from '@/componentes/resultados/GraficoEvolucao.vue'
import GraficoRanking from '@/componentes/resultados/GraficoRanking.vue'
import TabelaCapitais from '@/componentes/resultados/TabelaCapitais.vue'
import TabelaDadosGrafico from '@/componentes/resultados/TabelaDadosGrafico.vue'
import ResumoReferencia from '@/componentes/resumo/ResumoReferencia.vue'
import SeletorCapitaisGrafico from '@/componentes/resumo/SeletorCapitaisGrafico.vue'
import { useCacheResultados } from '@/composables/useCacheResultados'
import { useConsulta } from '@/composables/useConsulta'
import { useModoMock } from '@/composables/useModoMock'
import { usePeriodos } from '@/composables/usePeriodos'
import {
  atribuirPosicoes,
  escolherCapitaisPadrao,
  listarCapitaisGrafico,
  montarSeriesCapitais,
  montarTabelaCapitais,
  type PosicoesSeries,
} from '@/dominio/capitais'
import {
  completarFiltrosCapitais,
  descreverPendenciaCapitais,
  montarQueryCapitais,
  resolverFiltrosCapitais,
  type EdicaoCapitais,
} from '@/dominio/filtros'
import { formatarHora, formatarPeriodo } from '@/dominio/formatacao'
import { montarTabelaSeries } from '@/dominio/graficos'
import type { FiltroPeriodo } from '@/dominio/periodo'
import {
  descreverPosicao,
  montarRanking,
  montarTabelaRanking,
  nomearMunicipio,
} from '@/dominio/ranking'

const SECAO_POSICAO = 'secao-posicao'
const ESPERA_AVISO_MS = 3000
const POSICAO_REFERENCIA = 1

const rota = useRoute()
const router = useRouter()
const cache = useCacheResultados()
const { carregar: carregarModo } = useModoMock()
const { periodos, erro: erroPeriodos, carregar: carregarPeriodos } = usePeriodos()
const consulta = useConsulta(consultaCapitais)

const filtros = ref<EdicaoCapitais | null>(null)
const escolhidas = ref<string[]>([])
const posicoes = ref<PosicoesSeries>({})

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
  filtros.value ? descreverPendenciaCapitais(filtros.value) : 'Carregando as opções…',
)

function descreverCapitais(dados: ComparacaoCapitais): string {
  if (!dados.filtro_capitais) return `todas as ${dados.total_capitais} capitais`
  return dados.total_capitais === 1 ? '1 capital' : `${dados.total_capitais} capitais`
}

const resultado = computed(() => {
  const dados = consulta.dados.value
  if (!dados) return null
  const intervalo = {
    ano: dados.periodo.ano,
    mesInicio: dados.periodo.mes_inicio,
    mesFim: dados.periodo.mes_fim,
  }
  const ranking = montarRanking(dados)
  return {
    dados,
    intervalo,
    ranking,
    metrica: ranking.metrica,
    referencia: nomearMunicipio(dados.referencia.municipio),
    periodo: formatarPeriodo(intervalo),
    capitais: descreverCapitais(dados),
    posicao: descreverPosicao(dados),
    tabelaRanking: montarTabelaRanking(ranking),
    tabelaCapitais: montarTabelaCapitais(dados),
    opcoes: listarCapitaisGrafico(dados),
  }
})

const evolucao = computed(() => {
  if (!resultado.value) return null
  const series = montarSeriesCapitais(resultado.value.dados, posicoes.value)
  const campo = resultado.value.metrica.campoMensal
  return { series, campo, tabela: montarTabelaSeries(series, campo) }
})

const consultadoAs = computed(() => {
  const momento = consulta.consultadoEm.value
  if (momento === null) return null
  const base = `Resultado consultado às ${formatarHora(momento)}.`
  return consulta.origemCache.value
    ? `${base} Clique em Gerar comparativo para consultar de novo.`
    : base
})

const carregando = computed(() => consulta.carregando.value)

const filtrosMudaram = computed(() => {
  const consultados = consulta.filtrosResultado.value
  if (!consultados || !filtros.value) return false
  return (
    JSON.stringify(montarQueryCapitais(consultados)) !==
    JSON.stringify(montarQueryCapitais(filtros.value))
  )
})

const mostrarInicial = computed(
  () => !carregando.value && !consulta.dados.value && !consulta.erro.value,
)

const mensagemDemora = computed(() => {
  const quantidade = filtros.value?.capitais?.length
  const alvo =
    quantidade === undefined
      ? 'todas as capitais'
      : quantidade === 1
        ? '1 capital'
        : `${quantidade} capitais`
  return `Consultando ${alvo}. Na primeira consulta de um período isso pode levar até 1 minuto.`
})

function escolherCapitais(codigos: string[]) {
  escolhidas.value = codigos
  posicoes.value = atribuirPosicoes(posicoes.value, codigos)
}

async function gerar() {
  if (!filtros.value) return
  const completos = completarFiltrosCapitais(filtros.value)
  if (!completos) return
  cache.guardarFiltros('capitais', filtros.value)
  router.replace({ query: montarQueryCapitais(filtros.value) })
  await consulta.executar(completos)
  if (!consulta.dados.value) return
  await nextTick()
  document.getElementById(SECAO_POSICAO)?.focus()
}

watch(
  () => consulta.dados.value,
  (dados) => {
    if (!dados) return
    const disponiveis = listarCapitaisGrafico(dados).map((opcao) => opcao.codigo)
    const mantidas = escolhidas.value.filter((codigo) => disponiveis.includes(codigo))
    escolherCapitais(mantidas.length ? mantidas : escolherCapitaisPadrao(dados))
  },
)

watch(
  periodos,
  async (disponiveis) => {
    if (!disponiveis || filtros.value) return
    await carregarModo()
    const iniciais = resolverFiltrosCapitais(disponiveis, rota.query, cache.lerFiltros('capitais'))
    filtros.value = iniciais
    const completos = completarFiltrosCapitais(iniciais)
    if (completos) consulta.restaurar(completos)
  },
  { immediate: true },
)
</script>

<template>
  <div class="abertura-tela">
    <h1>Comparar com as capitais</h1>
    <p class="texto-apoio">Veja como um município se posiciona frente às capitais do Brasil.</p>
  </div>

  <EstadoErro v-if="erroPeriodos" :erro="erroPeriodos" @tentar-novamente="carregarPeriodos" />

  <form v-else class="filtros" aria-label="Filtros" @submit.prevent="gerar">
    <template v-if="filtros && periodos && periodo">
      <div class="filtros__linha">
        <SeletorMunicipio
          v-model="filtros.referencia"
          rotulo="Município de referência"
          :posicao="POSICAO_REFERENCIA"
          :bloqueado="null"
        />
        <SeletorPeriodo v-model="periodo" :periodos="periodos" />
      </div>
      <div class="filtros__linha">
        <SeletorCapitais v-model="filtros.capitais" />
        <SeletorMetrica v-model="filtros.metrica" />
      </div>
      <div class="filtros__acoes">
        <span v-if="pendencia" id="motivo-pendencia" class="filtros__motivo">{{ pendencia }}</span>
        <Button
          v-if="carregando"
          label="Cancelar"
          variant="text"
          type="button"
          @click="consulta.cancelar"
        />
        <Button
          type="submit"
          :label="carregando ? 'Consultando…' : 'Gerar comparativo'"
          :loading="carregando"
          :disabled="Boolean(pendencia)"
          :aria-describedby="pendencia ? 'motivo-pendencia' : undefined"
        />
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
      abaixo ainda é de {{ resultado.referencia }}, {{ resultado.periodo }},
      {{ resultado.metrica.frase }}.
    </Message>
    <EstadoCarregando
      v-if="carregando"
      mensagem="Consultando o Portal da Transparência…"
      :mensagem-demora="mensagemDemora"
      :apos-ms="ESPERA_AVISO_MS"
    />
  </div>

  <EstadoInicial
    v-if="mostrarInicial"
    complemento="Uma consulta só alimenta as quatro seções: posição, ranking, evolução e tabela."
  />

  <div v-else class="resultados">
    <SecaoResultado
      :identificador="SECAO_POSICAO"
      titulo="Posição do município"
      :carregando="carregando"
      :erro="consulta.erro.value"
      @tentar-novamente="gerar"
    >
      <template v-if="resultado && !carregando" #resumo>
        <p class="resultados__resumo">
          <strong>{{ resultado.referencia }}</strong> · {{ resultado.periodo }} ·
          {{ resultado.capitais }}
        </p>
        <p v-if="consultadoAs" class="texto-nota">{{ consultadoAs }}</p>
      </template>
      <template #carregando>
        <div class="resultados__espera">
          <Skeleton v-for="indice in 3" :key="indice" height="7rem" />
        </div>
      </template>
      <ResumoReferencia
        v-if="resultado"
        :referencia="resultado.dados.referencia"
        :posicao="resultado.posicao"
        :periodo="resultado.intervalo"
        :metrica="resultado.metrica.valor"
      />
    </SecaoResultado>

    <template v-if="resultado || carregando">
      <SecaoResultado
        identificador="secao-ranking"
        titulo="Ranking das capitais"
        :descricao="
          resultado
            ? `Capitais ordenadas por ${resultado.metrica.frase} no período, com o município de referência na posição que ocuparia.`
            : undefined
        "
        :carregando="carregando"
        :erro="null"
      >
        <template #carregando>
          <Skeleton height="24rem" />
        </template>
        <template v-if="resultado">
          <GraficoRanking :ranking="resultado.ranking" />
          <TabelaDadosGrafico
            :legenda="resultado.metrica.tituloRanking"
            :tabela="resultado.tabelaRanking"
          />
        </template>
      </SecaoResultado>

      <SecaoResultado
        identificador="secao-evolucao"
        titulo="Evolução mensal"
        :descricao="
          resultado
            ? `${resultado.metrica.nomeMensal} de cada mês para o município de referência e as capitais escolhidas.`
            : undefined
        "
        :carregando="carregando"
        :erro="null"
      >
        <template #carregando>
          <Skeleton height="20rem" />
        </template>
        <template v-if="resultado && evolucao">
          <SeletorCapitaisGrafico
            :model-value="escolhidas"
            :opcoes="resultado.opcoes"
            @update:model-value="escolherCapitais"
          />
          <GraficoEvolucao :series="evolucao.series" :campo="evolucao.campo" />
          <TabelaDadosGrafico
            :legenda="`${resultado.metrica.nomeMensal} por mês`"
            :tabela="evolucao.tabela"
          />
        </template>
      </SecaoResultado>

      <SecaoResultado
        identificador="secao-tabela"
        titulo="Tabela detalhada por capital"
        descricao="Todos os indicadores de cada capital no período. Clique no cabeçalho para ordenar."
        :carregando="carregando"
        :erro="null"
      >
        <template #carregando>
          <Skeleton height="20rem" />
        </template>
        <TabelaCapitais v-if="resultado" :tabela="resultado.tabelaCapitais" />
      </SecaoResultado>
    </template>
  </div>
</template>

<style scoped>
.filtros__linha {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr));
  gap: var(--spacing-scale-3x);
  align-items: start;
}
</style>
