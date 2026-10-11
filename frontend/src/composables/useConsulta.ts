import { ref, shallowRef, type Ref } from 'vue'

import { ErroConsulta } from '@/api/erros'
import type { DefinicaoConsulta } from '@/api/rotas'
import type { Fonte, Modo } from '@/api/tipos'
import { montarChaveCache } from '@/dominio/cache'
import { useCacheResultados, type CacheResultados } from './useCacheResultados'
import { useModoMock } from './useModoMock'

interface Dependencias {
  cache: CacheResultados
  modo: Readonly<Ref<Modo>>
  registrarFonte(fonte: Fonte): void
}

function criarDependencias(): Dependencias {
  const { modo, registrarFonte } = useModoMock()
  return { cache: useCacheResultados(), modo, registrarFonte }
}

function lerFonte(resposta: unknown): Fonte | null {
  if (resposta === null || typeof resposta !== 'object' || !('fonte' in resposta)) return null
  return resposta.fonte === 'mock' || resposta.fonte === 'portal_transparencia'
    ? resposta.fonte
    : null
}

function normalizarFalha(falha: unknown): ErroConsulta {
  return falha instanceof ErroConsulta ? falha : new ErroConsulta({ codigo: 'ERRO_INTERNO' })
}

export function useConsulta<Filtros, Resposta>(
  definicao: DefinicaoConsulta<Filtros, Resposta>,
  dependencias: Dependencias = criarDependencias(),
) {
  const dados = shallowRef<Resposta | null>(null)
  const erro = shallowRef<ErroConsulta | null>(null)
  const carregando = ref(false)
  const consultadoEm = ref<number | null>(null)
  const origemCache = ref(false)
  const filtrosResultado = shallowRef<Filtros | null>(null)

  let controleAtual: AbortController | null = null

  function montarChave(parametros: Record<string, string>): string {
    return montarChaveCache(definicao.rota, parametros, dependencias.modo.value)
  }

  function mostrar(resposta: Resposta, filtros: Filtros, momento: number, cache: boolean): void {
    dados.value = resposta
    filtrosResultado.value = filtros
    consultadoEm.value = momento
    origemCache.value = cache
    erro.value = null
  }

  function restaurar(filtros: Filtros): boolean {
    const entrada = dependencias.cache.ler(montarChave(definicao.montarParametros(filtros)))
    if (!entrada) return false
    mostrar(entrada.dados as Resposta, filtros, entrada.salvoEm, true)
    return true
  }

  async function executar(filtros: Filtros): Promise<void> {
    controleAtual?.abort()
    const controle = new AbortController()
    controleAtual = controle
    carregando.value = true
    erro.value = null
    const parametros = definicao.montarParametros(filtros)
    try {
      const resposta = await definicao.buscar(parametros, controle)
      if (controleAtual !== controle) return
      const fonte = lerFonte(resposta)
      if (fonte) dependencias.registrarFonte(fonte)
      const agora = Date.now()
      mostrar(resposta, filtros, agora, false)
      dependencias.cache.guardar(montarChave(parametros), resposta, agora)
    } catch (falha) {
      if (controleAtual !== controle) return
      const erroConsulta = normalizarFalha(falha)
      if (erroConsulta.cancelada) return
      erro.value = erroConsulta
      dados.value = null
      filtrosResultado.value = null
    } finally {
      if (controleAtual === controle) {
        controleAtual = null
        carregando.value = false
      }
    }
  }

  function cancelar(): void {
    controleAtual?.abort()
  }

  return {
    dados,
    erro,
    carregando,
    consultadoEm,
    origemCache,
    filtrosResultado,
    executar,
    cancelar,
    restaurar,
  }
}
