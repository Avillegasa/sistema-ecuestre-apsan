// src/components/rankings/RankingAnimation.jsx
import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { formatPercentage } from '../../utils/formatters';

// Animaciones
const slideIn = keyframes`
  0% { transform: translateX(-100%); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
`;

const slideOut = keyframes`
  0% { transform: translateX(0); opacity: 1; }
  100% { transform: translateX(100%); opacity: 0; }
`;

const highlight = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

// Contenedor principal
const AnimationContainer = styled.div`
  position: fixed;
  bottom: 40px;
  right: 40px;
  z-index: 1000;
  width: 400px;
  max-width: 90vw;
  animation: ${props => props.isExiting ? slideOut : slideIn} 0.5s ease-in-out;
  
  @media (max-width: 768px) {
    bottom: 20px;
    right: 20px;
  }
`;

// Tarjeta de animación
const AnimationCard = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.large};
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

// Cabecera
const CardHeader = styled.div`
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.md};
  font-weight: 600;
  text-align: center;
  font-size: ${props => props.theme.fontSizes.medium};
`;

// Contenido
const CardBody = styled.div`
  padding: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

// Avatar o imagen del jinete
const RiderAvatar = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: ${props => props.theme.colors.lightGray};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 600;
  color: ${props => props.theme.colors.primary};
  flex-shrink: 0;
`;

// Información del ranking
const RankingInfo = styled.div`
  flex: 1;
`;

const RiderName = styled.div`
  font-weight: 600;
  font-size: ${props => props.theme.fontSizes.medium};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const HorseName = styled.div`
  color: ${props => props.theme.colors.gray};
  font-size: ${props => props.theme.fontSizes.small};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

// Cambio de posición
const PositionChange = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  color: ${props => {
    switch (props.direction) {
      case 'up': return props.theme.colors.success;
      case 'down': return props.theme.colors.error;
      default: return props.theme.colors.gray;
    }
  }};
  font-weight: 500;
  margin-top: ${props => props.theme.spacing.xs};
  animation: ${highlight} 1s ease;
`;

// Porcentaje
const PercentageContainer = styled.div`
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.large};
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: ${props => props.theme.fontSizes.large};
  min-width: 90px;
  text-align: center;
`;

/**
 * Componente de animación para cambios en rankings
 * Muestra una tarjeta flotante cuando un participante cambia de posición
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Object} props.rankingEntry - Datos del ranking que cambió
 * @param {boolean} props.visible - Si la animación debe mostrarse
 * @param {Function} props.onClose - Función a ejecutar cuando termina la animación
 */
const RankingAnimation = ({ rankingEntry, visible, onClose }) => {
  const [isExiting, setIsExiting] = useState(false);
  
  useEffect(() => {
    let showTimer;
    let exitTimer;
    
    if (visible) {
      // Duración total de la animación: 5 segundos
      showTimer = setTimeout(() => {
        setIsExiting(true);
        
        // Esperar a que termine la animación de salida
        exitTimer = setTimeout(() => {
          setIsExiting(false);
          if (onClose) onClose();
        }, 500); // Duración de la animación de salida
      }, 4500); // Mostrar por 4.5s + 0.5s de animación = 5s total
    }
    
    return () => {
      if (showTimer) clearTimeout(showTimer);
      if (exitTimer) clearTimeout(exitTimer);
    };
  }, [visible, onClose]);
  
  if (!visible || !rankingEntry) return null;
  
  // Obtener iniciales del jinete
  const getInitials = () => {
    const firstName = rankingEntry.rider?.firstName || rankingEntry.rider?.first_name || '';
    const lastName = rankingEntry.rider?.lastName || rankingEntry.rider?.last_name || '';
    
    if (!firstName && !lastName) return '?';
    
    return `${firstName.charAt(0)}${lastName ? lastName.charAt(0) : ''}`.toUpperCase();
  };
  
  // Texto para el cambio de posición
  const getPositionChangeText = () => {
    if (rankingEntry.direction === 'up') {
      return `Subió a la posición ${rankingEntry.position}`;
    } else if (rankingEntry.direction === 'down') {
      return `Bajó a la posición ${rankingEntry.position}`;
    } else if (rankingEntry.direction === 'new') {
      return `Nueva entrada en posición ${rankingEntry.position}`;
    } else {
      return `Posición ${rankingEntry.position}`;
    }
  };
  
  // Ícono para el cambio de posición
  const getPositionIcon = () => {
    if (rankingEntry.direction === 'up') {
      return '↑';
    } else if (rankingEntry.direction === 'down') {
      return '↓';
    } else if (rankingEntry.direction === 'new') {
      return '✦';
    } else {
      return '•';
    }
  };
  
  return (
    <AnimationContainer isExiting={isExiting}>
      <AnimationCard>
        <CardHeader>Actualización de Ranking</CardHeader>
        <CardBody>
          <RiderAvatar>{getInitials()}</RiderAvatar>
          
          <RankingInfo>
            <RiderName>
              {rankingEntry.rider?.firstName || rankingEntry.rider?.first_name} {rankingEntry.rider?.lastName || rankingEntry.rider?.last_name}
            </RiderName>
            
            <HorseName>
              {rankingEntry.horse?.name}
            </HorseName>
            
            <PositionChange direction={rankingEntry.direction}>
              {getPositionIcon()} {getPositionChangeText()}
            </PositionChange>
          </RankingInfo>
          
          <PercentageContainer>
            {formatPercentage(rankingEntry.percentage)}
          </PercentageContainer>
        </CardBody>
      </AnimationCard>
    </AnimationContainer>
  );
};

export default RankingAnimation;