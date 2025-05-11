import React from 'react';
import styled, { css } from 'styled-components';

// Estilos para diferentes variantes de botones
const variants = {
  primary: css`
    background-color: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.white};
    &:hover {
      background-color: ${props => darken(0.1, props.theme.colors.primary)};
    }
  `,
  secondary: css`
    background-color: ${props => props.theme.colors.secondary};
    color: ${props => props.theme.colors.white};
    &:hover {
      background-color: ${props => darken(0.1, props.theme.colors.secondary)};
    }
  `,
  success: css`
    background-color: ${props => props.theme.colors.success};
    color: ${props => props.theme.colors.white};
    &:hover {
      background-color: ${props => darken(0.1, props.theme.colors.success)};
    }
  `,
  error: css`
    background-color: ${props => props.theme.colors.error};
    color: ${props => props.theme.colors.white};
    &:hover {
      background-color: ${props => darken(0.1, props.theme.colors.error)};
    }
  `,
  warning: css`
    background-color: ${props => props.theme.colors.warning};
    color: ${props => props.theme.colors.white};
    &:hover {
      background-color: ${props => darken(0.1, props.theme.colors.warning)};
    }
  `,
  outline: css`
    background-color: transparent;
    color: ${props => props.theme.colors.primary};
    border: 2px solid ${props => props.theme.colors.primary};
    &:hover {
      background-color: ${props => props.theme.colors.primary};
      color: ${props => props.theme.colors.white};
    }
  `,
  text: css`
    background-color: transparent;
    color: ${props => props.theme.colors.primary};
    border: none;
    padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
    &:hover {
      background-color: rgba(0, 0, 0, 0.05);
    }
  `,
};

// Función auxiliar para oscurecer un color (similar a la función darken de SASS)
const darken = (amount, color) => {
  // Implementación simple para evitar dependencias adicionales
  const parseColor = (colorStr) => {
    const hexMatch = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(colorStr);
    if (hexMatch) {
      return [
        parseInt(hexMatch[1], 16),
        parseInt(hexMatch[2], 16),
        parseInt(hexMatch[3], 16)
      ];
    }
    return [0, 0, 0];
  };

  const [r, g, b] = parseColor(color);
  const darkenComponent = (comp) => Math.max(0, Math.floor(comp * (1 - amount)));
  
  return `rgb(${darkenComponent(r)}, ${darkenComponent(g)}, ${darkenComponent(b)})`;
};

// Estilos para diferentes tamaños de botones
const sizes = {
  small: css`
    padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
    font-size: ${props => props.theme.fontSizes.small};
  `,
  medium: css`
    padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
    font-size: ${props => props.theme.fontSizes.medium};
  `,
  large: css`
    padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
    font-size: ${props => props.theme.fontSizes.large};
  `,
  xlarge: css`
    padding: ${props => props.theme.spacing.lg} ${props => props.theme.spacing.xl};
    font-size: ${props => props.theme.fontSizes.xl};
  `,
};

// Styled button base
const StyledButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: ${props => props.theme.borderRadius.medium};
  border: none;
  cursor: pointer;
  font-family: ${props => props.theme.fonts.main};
  font-weight: 500;
  transition: all ${props => props.theme.transitions.fast};
  text-align: center;
  min-height: 44px; /* Para mejor experiencia en dispositivos táctiles */
  
  /* Aplicar variante */
  ${props => variants[props.variant]}
  
  /* Aplicar tamaño */
  ${props => sizes[props.size]}
  
  /* Estilo para botón deshabilitado */
  ${props => props.disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
    &:hover {
      filter: none;
    }
  `}
  
  /* Estilo para botón full width */
  ${props => props.fullWidth && css`
    width: 100%;
  `}
  
  /* Estilo cuando hay un icono */
  ${props => props.hasIcon && css`
    svg {
      margin-right: ${props.iconPosition === 'right' ? 0 : props.theme.spacing.xs};
      margin-left: ${props.iconPosition === 'right' ? props.theme.spacing.xs : 0};
    }
  `}
  
  /* Estilo para botones grandes en dispositivos móviles (mejor para tocar con guantes) */
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    min-height: 48px;
    font-size: 16px;
    padding: 12px 16px;
  }
`;

/**
 * Componente Button reutilizable
 * 
 * @param {Object} props - Propiedades del componente
 * @param {string} [props.variant='primary'] - Variante del botón: primary, secondary, success, error, warning, outline, text
 * @param {string} [props.size='medium'] - Tamaño del botón: small, medium, large, xlarge
 * @param {boolean} [props.disabled=false] - Si el botón está deshabilitado
 * @param {boolean} [props.fullWidth=false] - Si el botón debe ocupar todo el ancho disponible
 * @param {Function} props.onClick - Función a ejecutar cuando se hace click en el botón
 * @param {React.ReactNode} props.children - Contenido del botón
 * @param {React.ReactNode} [props.icon] - Icono a mostrar
 * @param {string} [props.iconPosition='left'] - Posición del icono: left, right
 * @param {string} [props.type='button'] - Tipo de botón: button, submit, reset
 */
const Button = ({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  fullWidth = false,
  onClick,
  children,
  icon,
  iconPosition = 'left',
  type = 'button',
  ...rest
}) => {
  const hasIcon = !!icon;
  
  return (
    <StyledButton
      variant={variant}
      size={size}
      disabled={disabled}
      fullWidth={fullWidth}
      onClick={onClick}
      hasIcon={hasIcon}
      iconPosition={iconPosition}
      type={type}
      {...rest}
    >
      {hasIcon && iconPosition === 'left' && icon}
      {children}
      {hasIcon && iconPosition === 'right' && icon}
    </StyledButton>
  );
};

export default Button;