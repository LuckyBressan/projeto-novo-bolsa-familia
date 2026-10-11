// O jsdom não implementa matchMedia, e o Select do PrimeVue o chama ao montar.
// Fica direto na janela para sobreviver ao vi.unstubAllGlobals() dos testes.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (consulta: string) => ({
    matches: false,
    media: consulta,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
  }),
})
