import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html, body {
    font-family: ${props => props.theme.fonts.main};
    font-size: 16px;
    color: ${props => props.theme.colors.text};
    background-color: ${props => props.theme.colors.background};
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: ${props => props.theme.fonts.heading};
    margin-bottom: ${props => props.theme.spacing.md};
    font-weight: 600;
  }

  h1 {
    font-size: ${props => props.theme.fontSizes.xxl};
  }

  h2 {
    font-size: ${props => props.theme.fontSizes.xl};
  }

  h3 {
    font-size: ${props => props.theme.fontSizes.large};
  }

  p {
    margin-bottom: ${props => props.theme.spacing.md};
  }

  a {
    color: ${props => props.theme.colors.primary};
    text-decoration: none;
    transition: color ${props => props.theme.transitions.fast};

    &:hover {
      color: ${props => props.theme.colors.accent};
    }
  }

  button {
    cursor: pointer;
    font-family: ${props => props.theme.fonts.main};
  }

  img {
    max-width: 100%;
    height: auto;
  }

  /* Para hacer responsive en móviles con pantallas táctiles */
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    html {
      font-size: 14px;
    }

    button, input, select {
      min-height: 44px; /* Para mejor experiencia táctil */
    }
  }

  /* Mejorar visibilidad para uso en campo (sol, guantes) */
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    button, a.button, input[type="submit"] {
      min-height: 48px;
      font-size: 16px;
      padding: 12px 16px;
    }
  }
`;

export default GlobalStyles;