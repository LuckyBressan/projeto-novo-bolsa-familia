import { describe, expect, it } from 'vitest'
import { nextTick } from 'vue'

import { criarTema } from '@/composables/useTema'

type Ouvinte = (evento: { matches: boolean }) => void

function simularSistema(inicial: { contraste: boolean; escuro: boolean }) {
  const estado: Record<string, boolean> = {
    '(prefers-contrast: more)': inicial.contraste,
    '(prefers-color-scheme: dark)': inicial.escuro,
  }
  const ouvintes: Record<string, Ouvinte[]> = {}
  return {
    consultar: (consulta: string) =>
      ({
        get matches() {
          return estado[consulta] ?? false
        },
        addEventListener: (_tipo: string, ouvinte: Ouvinte) => {
          ouvintes[consulta] = [...(ouvintes[consulta] ?? []), ouvinte]
        },
      }) as unknown as MediaQueryList,
    mudar(consulta: string, valor: boolean) {
      estado[consulta] = valor
      ouvintes[consulta]?.forEach((ouvinte) => ouvinte({ matches: valor }))
    },
  }
}

function criarAmbiente(sistema = { contraste: false, escuro: false }) {
  const simulado = simularSistema(sistema)
  const raiz = document.createElement('html')
  const armazenamento = window.localStorage
  return { simulado, raiz, armazenamento, consultar: simulado.consultar }
}

describe('useTema', () => {
  it('sem escolha guardada, segue o sistema e aplica as classes no html', () => {
    localStorage.clear()
    const ambiente = criarAmbiente({ contraste: false, escuro: true })

    const { escolha, tema } = criarTema(ambiente)

    expect(escolha.value).toBe('automatico')
    expect(tema.value).toBe('escuro')
    expect([...ambiente.raiz.classList]).toEqual(['tema-escuro'])
  })

  it('a escolha é aplicada na hora e continua valendo ao reabrir', async () => {
    localStorage.clear()
    const ambiente = criarAmbiente({ contraste: false, escuro: true })
    const { escolher, tema } = criarTema(ambiente)

    escolher('contraste')
    await nextTick()

    expect(tema.value).toBe('contraste')
    expect([...ambiente.raiz.classList]).toEqual(['tema-escuro', 'alto-contraste'])
    expect(localStorage.getItem('tema')).toBe('contraste')

    escolher('claro')
    await nextTick()
    expect([...ambiente.raiz.classList]).toEqual([])

    const reaberto = criarTema(criarAmbiente({ contraste: false, escuro: true }))
    expect(reaberto.escolha.value).toBe('claro')
    expect(reaberto.tema.value).toBe('claro')
  })

  it('no automático, acompanha a mudança do sistema sem recarregar', async () => {
    localStorage.clear()
    const ambiente = criarAmbiente()
    const { tema, escolher } = criarTema(ambiente)
    expect(tema.value).toBe('claro')

    ambiente.simulado.mudar('(prefers-color-scheme: dark)', true)
    await nextTick()
    expect([...ambiente.raiz.classList]).toEqual(['tema-escuro'])

    ambiente.simulado.mudar('(prefers-contrast: more)', true)
    await nextTick()
    expect([...ambiente.raiz.classList]).toEqual(['tema-escuro', 'alto-contraste'])

    escolher('claro')
    ambiente.simulado.mudar('(prefers-contrast: more)', false)
    await nextTick()
    expect(tema.value).toBe('claro')
  })

  it('com o armazenamento bloqueado, a escolha vale enquanto a página estiver aberta', async () => {
    const bloqueado = {
      getItem: () => {
        throw new Error('bloqueado')
      },
      setItem: () => {
        throw new Error('bloqueado')
      },
    } as unknown as Storage
    const ambiente = { ...criarAmbiente(), armazenamento: bloqueado }

    const { escolha, escolher } = criarTema(ambiente)
    expect(escolha.value).toBe('automatico')

    escolher('escuro')
    await nextTick()
    expect([...ambiente.raiz.classList]).toEqual(['tema-escuro'])
  })
})
