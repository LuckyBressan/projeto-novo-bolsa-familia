import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

const azulGovBr = {
  50: '#edf5ff',
  100: '#d4e5ff',
  200: '#adcdff',
  300: '#81aefc',
  400: '#5992ed',
  500: '#2670e8',
  600: '#155bcb',
  700: '#1351b4',
  800: '#0c326f',
  900: '#071d41',
  950: '#071d41',
}

const cinzaGovBr = {
  0: '#ffffff',
  50: '#f8f8f8',
  100: '#f0f0f0',
  200: '#e6e6e6',
  300: '#cccccc',
  400: '#adadad',
  500: '#888888',
  600: '#757575',
  700: '#555555',
  800: '#333333',
  900: '#1b1b1b',
  950: '#000000',
}

const superficieEscura = {
  0: '#ffffff',
  50: '#edf5ff',
  100: '#d4e5ff',
  200: '#c5d4eb',
  300: '#adcdff',
  400: '#81aefc',
  500: '#5992ed',
  600: '#2670e8',
  700: '#155bcb',
  800: '#0c326f',
  900: '#071d41',
  950: '#071d41',
}

const foco = { color: 'var(--focus)', shadow: 'none' }

const camada = {
  background: 'var(--surface-card)',
  borderColor: 'var(--border)',
  color: 'var(--color)',
}

// As cores apontam para os tokens de tokens.css: o mesmo esquema serve aos três temas,
// e o alto contraste muda só as variáveis, sem repetir aqui cada cor.
const esquema = {
  primary: {
    color: 'var(--interactive)',
    contrastColor: 'var(--on-interactive)',
    hoverColor: 'var(--interactive-hover)',
    activeColor: 'var(--interactive-active)',
  },
  highlight: {
    background: 'var(--interactive)',
    focusBackground: 'var(--interactive-hover)',
    color: 'var(--on-interactive)',
    focusColor: 'var(--on-interactive)',
  },
  text: {
    color: 'var(--color)',
    hoverColor: 'var(--color)',
    mutedColor: 'var(--color-secondary)',
    hoverMutedColor: 'var(--color)',
  },
  content: {
    background: 'var(--surface-card)',
    hoverBackground: 'var(--interactive-subtle)',
    borderColor: 'var(--border)',
    color: 'var(--color)',
    hoverColor: 'var(--color)',
  },
  formField: {
    background: 'var(--background)',
    disabledBackground: 'var(--background-alternative)',
    filledBackground: 'var(--background-alternative)',
    filledHoverBackground: 'var(--background-alternative)',
    filledFocusBackground: 'var(--background-alternative)',
    borderColor: 'var(--border-control)',
    hoverBorderColor: 'var(--interactive)',
    focusBorderColor: 'var(--interactive)',
    invalidBorderColor: 'var(--danger)',
    color: 'var(--color)',
    disabledColor: 'var(--disabled-text)',
    placeholderColor: 'var(--color-secondary)',
    invalidPlaceholderColor: 'var(--danger)',
    iconColor: 'var(--interactive)',
    shadow: 'none',
  },
  overlay: { select: camada, popover: camada, modal: camada },
  list: {
    option: {
      focusBackground: 'var(--interactive-subtle)',
      selectedBackground: 'var(--interactive)',
      selectedFocusBackground: 'var(--interactive-hover)',
      color: 'var(--color)',
      focusColor: 'var(--color)',
      selectedColor: 'var(--on-interactive)',
      selectedFocusColor: 'var(--on-interactive)',
      icon: { color: 'var(--color-secondary)', focusColor: 'var(--color)' },
    },
    optionGroup: { background: 'transparent', color: 'var(--color-secondary)' },
  },
}

const botaoVazado = {
  hoverBackground: 'var(--interactive-subtle)',
  activeBackground: 'var(--interactive-subtle)',
  borderColor: 'var(--interactive)',
  color: 'var(--interactive)',
}

const botaoTexto = {
  hoverBackground: 'var(--interactive-subtle)',
  activeBackground: 'var(--interactive-subtle)',
  color: 'var(--interactive)',
}

const botao = {
  root: { primary: { focusRing: foco }, secondary: { focusRing: foco } },
  outlined: { primary: botaoVazado, secondary: botaoVazado },
  text: { primary: botaoTexto, secondary: botaoTexto },
}

function colorirMensagem(estado: 'info' | 'success' | 'warning' | 'danger') {
  return {
    background: `var(--${estado}-alternative)`,
    borderColor: `var(--${estado})`,
    color: 'var(--color)',
    shadow: 'none',
  }
}

const mensagem = {
  info: colorirMensagem('info'),
  success: colorirMensagem('success'),
  warn: colorirMensagem('warning'),
  error: colorirMensagem('danger'),
}

const selo = {
  success: { background: 'var(--success)', color: 'var(--on-success)' },
  info: { background: 'var(--info)', color: 'var(--on-info)' },
  warn: { background: 'var(--warning)', color: 'var(--on-warning)' },
  danger: { background: 'var(--danger)', color: 'var(--on-danger)' },
  secondary: { background: 'var(--background-alternative)', color: 'var(--color)' },
}

export const presetGovBr = definePreset(Aura, {
  primitive: {
    borderRadius: { none: '0', xs: '2px', sm: '4px', md: '8px', lg: '16px', xl: '16px' },
  },
  semantic: {
    primary: azulGovBr,
    disabledOpacity: '0.45',
    focusRing: {
      width: '4px',
      style: 'dashed',
      color: 'var(--focus)',
      offset: '4px',
      shadow: 'none',
    },
    formField: {
      paddingX: '16px',
      paddingY: '8px',
      borderRadius: '4px',
      focusRing: {
        width: '4px',
        style: 'dashed',
        color: 'var(--focus)',
        offset: '4px',
        shadow: 'none',
      },
    },
    colorScheme: {
      light: { surface: cinzaGovBr, ...esquema },
      dark: { surface: superficieEscura, ...esquema },
    },
  },
  components: {
    button: {
      root: {
        borderRadius: '999em',
        paddingX: '24px',
        paddingY: '0',
        gap: '8px',
        label: { fontWeight: '600' },
      },
      colorScheme: { light: botao, dark: botao },
    },
    card: {
      root: { borderRadius: '8px', shadow: 'var(--surface-shadow-sm)' },
      body: { padding: '24px' },
    },
    tag: {
      root: { borderRadius: '4px', fontWeight: '600', fontSize: '0.875rem' },
      colorScheme: { light: selo, dark: selo },
    },
    message: {
      root: { borderRadius: '4px' },
      content: { padding: '12px 16px', gap: '12px' },
      text: { fontSize: '0.875rem', fontWeight: '400' },
      colorScheme: { light: mensagem, dark: mensagem },
    },
  },
})
