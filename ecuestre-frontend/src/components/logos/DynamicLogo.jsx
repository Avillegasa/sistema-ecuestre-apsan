// src/components/logos/DynamicLogo.jsx
import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';

// Animación de rotación
const rotate = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// Animación de brillo
const shine = keyframes`
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
`;

// Contenedor principal
const LogoContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.md};
`;

// Logotipo con fallback a texto si no hay imagen
const LogoImage = styled.img`
  max-width: 100%;
  height: auto;
  max-height: ${props => props.size || '100px'};
  object-fit: contain;
  animation: ${shine} 3s infinite ease-in-out;
`;

// Logotipo de texto (fallback)
const TextLogo = styled.div`
  font-family: ${props => props.theme.fonts.heading};
  font-size: ${props => props.size ? `calc(${props.size} / 2)` : '2rem'};
  font-weight: bold;
  color: ${props => props.textColor || props.theme.colors.primary};
  text-align: center;
  animation: ${shine} 3s infinite ease-in-out;
`;

// Ícono 
const LogoIcon = styled.div`
  font-size: ${props => props.size || '3rem'};
  margin-right: ${props => props.theme.spacing.md};
  color: ${props => props.iconColor || props.theme.colors.accent};
  animation: ${rotate} 10s infinite linear;
  display: flex;
  align-items: center;
  justify-content: center;
`;

/**
 * Componente de logotipo dinámico con fallback
 * 
 * @param {Object} props - Propiedades del componente
 * @param {string} [props.src] - URL de la imagen del logotipo
 * @param {string} [props.alt='Logo'] - Texto alternativo para la imagen
 * @param {string} [props.fallbackText='APSAN'] - Texto a mostrar si no hay imagen
 * @param {string} [props.size='100px'] - Tamaño del logotipo
 * @param {string} [props.textColor] - Color del texto (fallback)
 * @param {string} [props.icon='🏇'] - Ícono para mostrar junto al texto
 * @param {string} [props.iconColor] - Color del ícono
 */
const DynamicLogo = ({ 
  src, 
  alt = 'Logo', 
  fallbackText = 'APSAN', 
  size = '100px',
  textColor,
  icon = '🏇',
  iconColor
}) => {
  const [imageError, setImageError] = useState(false);
  
  const handleImageError = () => {
    setImageError(true);
  };
  
  return (
    <LogoContainer>
      {!imageError && src ? (
        <LogoImage
          src={src}
          alt={alt}
          size={size}
          onError={handleImageError}
        />
      ) : (
        <>
          <LogoIcon
            size={size}
            iconColor={iconColor}
          >
            {icon}
          </LogoIcon>
          <TextLogo
            size={size}
            textColor={textColor}
          >
            {fallbackText}
          </TextLogo>
        </>
      )}
    </LogoContainer>
  );
};

export default DynamicLogo;