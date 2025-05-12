// src/styles/theme.js
const theme = {
  // Colores principales
  colors: {
    primary: '#2962ff',        // Azul principal
    secondary: '#1e3a8a',      // Azul oscuro
    accent: '#f59e0b',         // Naranja/Ámbar
    success: '#10b981',        // Verde
    error: '#ef4444',          // Rojo
    warning: '#f59e0b',        // Ámbar
    info: '#3b82f6',           // Azul claro
    
    // Tonos neutros
    text: '#1f2937',           // Texto principal
    gray: '#6b7280',           // Texto secundario
    lightGray: '#e5e7eb',      // Bordes y separadores
    background: '#f3f4f6',     // Fondo general
    white: '#ffffff',          // Componentes
    
    // Variantes de suavizado
    primaryLight: '#e3f2fd',
    errorLight: '#fee2e2',
    successLight: '#d1fae5',
  },
  
  // Tipografía
  fonts: {
    main: "'Roboto', 'Segoe UI', 'Helvetica Neue', sans-serif",
    heading: "'Montserrat', 'Roboto', 'Segoe UI', sans-serif",
    mono: "'Roboto Mono', 'Courier New', monospace",
  },
  
  // Tamaños de fuente
  fontSizes: {
    small: '0.875rem',      // 14px
    medium: '1rem',         // 16px
    large: '1.125rem',      // 18px
    xl: '1.25rem',          // 20px
    xxl: '1.5rem',          // 24px
    xxxl: '2rem',           // 32px
  },
  
  // Espaciado
  spacing: {
    xs: '0.25rem',          // 4px
    sm: '0.5rem',           // 8px
    md: '1rem',             // 16px
    lg: '1.5rem',           // 24px
    xl: '2rem',             // 32px
    xxl: '3rem',            // 48px
  },
  
  // Bordes redondeados
  borderRadius: {
    small: '0.25rem',       // 4px
    medium: '0.5rem',       // 8px
    large: '1rem',          // 16px
    full: '9999px',         // Botones circulares
  },
  
  // Sombras
  shadows: {
    small: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
    medium: '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
    large: '0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)',
  },
  
  // Transiciones
  transitions: {
    fast: '0.2s ease',
    medium: '0.3s ease',
    slow: '0.5s ease',
  },
  
  // Breakpoints
  breakpoints: {
    mobile: '640px',
    tablet: '768px',
    laptop: '1024px',
    desktop: '1280px',
  },
};

export default theme;