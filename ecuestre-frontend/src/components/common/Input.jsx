import React, { forwardRef } from 'react';
import styled, { css } from 'styled-components';

// Estilos para diferentes estados del input
const inputStates = {
  default: css`
    border-color: ${props => props.theme.colors.lightGray};
    &:focus {
      border-color: ${props => props.theme.colors.primary};
      box-shadow: 0 0 0 2px rgba(41, 98, 255, 0.2);
    }
  `,
  error: css`
    border-color: ${props => props.theme.colors.error};
    &:focus {
      border-color: ${props => props.theme.colors.error};
      box-shadow: 0 0 0 2px rgba(211, 47, 47, 0.2);
    }
  `,
  success: css`
    border-color: ${props => props.theme.colors.success};
    &:focus {
      border-color: ${props => props.theme.colors.success};
      box-shadow: 0 0 0 2px rgba(67, 160, 71, 0.2);
    }
  `,
};

// Estilos para diferentes tamaños del input
const inputSizes = {
  small: css`
    padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
    font-size: ${props => props.theme.fontSizes.small};
    height: 32px;
  `,
  medium: css`
    padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
    font-size: ${props => props.theme.fontSizes.medium};
    height: 44px;
  `,
  large: css`
    padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
    font-size: ${props => props.theme.fontSizes.large};
    height: 56px;
  `,
};

// Contenedor del campo de entrada
const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  margin-bottom: ${props => props.theme.spacing.md};
  width: ${props => props.fullWidth ? '100%' : 'auto'};
`;

// Etiqueta del campo
const Label = styled.label`
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.small};
  font-weight: 500;
  margin-bottom: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.text};
`;

// Campo de entrada base
const StyledInput = styled.input`
  font-family: ${props => props.theme.fonts.main};
  border-radius: ${props => props.theme.borderRadius.medium};
  border: 1px solid ${props => props.theme.colors.lightGray};
  outline: none;
  transition: border-color ${props => props.theme.transitions.fast},
              box-shadow ${props => props.theme.transitions.fast};
  width: 100%;
  
  /* Aplicar estado */
  ${props => inputStates[props.state]}
  
  /* Aplicar tamaño */
  ${props => inputSizes[props.size]}
  
  /* Estilo para campo deshabilitado */
  ${props => props.disabled && css`
    background-color: ${props => props.theme.colors.lightGray};
    cursor: not-allowed;
    opacity: 0.7;
  `}
  
  /* Modificar para mejor experiencia en móviles */
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    min-height: 48px;
    font-size: 16px; /* Evitar zoom en iOS */
  }
`;

// Mensaje de error o ayuda
const HelperText = styled.span`
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.small};
  margin-top: ${props => props.theme.spacing.xs};
  color: ${props => props.error ? props.theme.colors.error : props.theme.colors.gray};
`;

/**
 * Componente Input reutilizable
 * 
 * @param {Object} props - Propiedades del componente
 * @param {string} props.id - ID del campo de entrada
 * @param {string} [props.label] - Etiqueta del campo
 * @param {string} [props.type='text'] - Tipo de campo: text, password, email, number, etc.
 * @param {string} [props.placeholder] - Texto de placeholder
 * @param {string} [props.value] - Valor del campo
 * @param {Function} [props.onChange] - Función a ejecutar cuando cambia el valor
 * @param {boolean} [props.disabled=false] - Si el campo está deshabilitado
 * @param {boolean} [props.required=false] - Si el campo es requerido
 * @param {string} [props.size='medium'] - Tamaño del campo: small, medium, large
 * @param {boolean} [props.fullWidth=false] - Si el campo debe ocupar todo el ancho disponible
 * @param {string} [props.error] - Mensaje de error
 * @param {string} [props.helperText] - Texto de ayuda
 * @param {string} [props.state='default'] - Estado del campo: default, error, success
 */
const Input = forwardRef(({
  id,
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  disabled = false,
  required = false,
  size = 'medium',
  fullWidth = false,
  error,
  helperText,
  state = 'default',
  ...rest
}, ref) => {
  // Determinar el estado del input basado en si hay un error
  const inputState = error ? 'error' : state;
  
  return (
    <InputContainer fullWidth={fullWidth}>
      {label && (
        <Label htmlFor={id}>
          {label}
          {required && <span style={{ color: 'red' }}> *</span>}
        </Label>
      )}
      
      <StyledInput
        id={id}
        ref={ref}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
        size={size}
        state={inputState}
        aria-invalid={!!error}
        {...rest}
      />
      
      {(error || helperText) && (
        <HelperText error={!!error}>
          {error || helperText}
        </HelperText>
      )}
    </InputContainer>
  );
});

export default Input;