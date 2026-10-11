import type { Ref } from 'vue'

import { buscarEstados, buscarMunicipiosByUf } from '@/api/rotas'
import type { Estado, Modo, Municipio } from '@/api/tipos'
import { conferirValidade } from '@/dominio/cache'
import { gravarJson, lerJson, obterArmazenamento } from './armazenamento'
import { useModoMock } from './useModoMock'

export const VERSAO_CATALOGO = 1

const VALIDADE_CATALOGO_MS = 30 * 24 * 60 * 60 * 1000
const CHAVE_ESTADOS = 'catalogo:estados'
const CHAVE_MUNICIPIOS = 'catalogo:municipios'

interface ItemCatalogo<Dados> {
  salvoEm: number
  versao: number
  dados: Dados
}

interface Dependencias {
  armazenamento: Storage | null
  modo: Readonly<Ref<Modo>>
}

export function criarCatalogo(dependencias: Dependencias) {
  const { armazenamento } = dependencias
  const memoria = new Map<string, Promise<unknown>>()

  function lerGuardado<Dados>(chave: string): Dados | null {
    const item = lerJson<ItemCatalogo<Dados>>(armazenamento, chave)
    if (!item || item.versao !== VERSAO_CATALOGO) return null
    return conferirValidade(item.salvoEm, Date.now(), VALIDADE_CATALOGO_MS) ? item.dados : null
  }

  async function obter<Dados>(chave: string, buscar: () => Promise<Dados>): Promise<Dados> {
    const guardados = lerGuardado<Dados>(chave)
    if (guardados) return guardados
    const dados = await buscar()
    gravarJson(armazenamento, chave, { salvoEm: Date.now(), versao: VERSAO_CATALOGO, dados })
    return dados
  }

  function carregar<Dados>(chave: string, buscar: () => Promise<Dados>): Promise<Dados> {
    const andamento = memoria.get(chave) as Promise<Dados> | undefined
    if (andamento) return andamento
    const carga = obter(chave, buscar).catch((falha) => {
      memoria.delete(chave)
      throw falha
    })
    memoria.set(chave, carga)
    return carga
  }

  function carregarEstados(): Promise<Estado[]> {
    return carregar(CHAVE_ESTADOS, async () => (await buscarEstados()).items)
  }

  function carregarMunicipios(uf: string): Promise<Municipio[]> {
    const chave = `${CHAVE_MUNICIPIOS}:${dependencias.modo.value}:${uf}`
    return carregar(chave, async () => (await buscarMunicipiosByUf(uf)).items)
  }

  return { carregarEstados, carregarMunicipios }
}

export type Catalogo = ReturnType<typeof criarCatalogo>

let catalogoApp: Catalogo | null = null

export function useCatalogo(): Catalogo {
  catalogoApp ??= criarCatalogo({
    armazenamento: obterArmazenamento('localStorage'),
    modo: useModoMock().modo,
  })
  return catalogoApp
}
