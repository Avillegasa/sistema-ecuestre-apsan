// src/components/common/Timer.jsx
import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

// Animación para los segundos
const tick = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.3; }
  100% { opacity: 1; }
`;

// Contenedor principal
const TimerContainer = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: ${props => props.large ? '2rem' : '1rem'};
  font-family: monospace;
  background-color: ${props => props.theme.colors.white};
  color: ${props => props.theme.colors.primary};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  user-select: none;
`;

// Separador que parpadea
const Separator = styled.span`
  animation: ${tick} 1s infinite;
  margin: 0 2px;
`;

/**
 * Componente de reloj digital
 * 
 * @param {Object} props - Propiedades del componente
 * @param {boolean} [props.large=false] - Si mostrar el reloj en tamaño grande
 * @param {boolean} [props.showSeconds=true] - Si mostrar los segundos
 * @param {boolean} [props.is24Hour=true] - Si usar formato de 24 horas
 */
const Timer = ({ large = false, showSeconds = true, is24Hour = true }) => {
  const [time, setTime] = useState(new Date());
  
  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  // Formatear hora
  const formatHour = () => {
    let hours = time.getHours();
    
    if (!is24Hour) {
      const period = hours >= 12 ? 'PM' : 'AM';
      hours = hours % 12 || 12; // Convertir a formato 12 horas
      
      return `${hours}${showSeconds ? ':' : Separator}${String(time.getMinutes()).padStart(2, '0')}${showSeconds ? `:${String(time.getSeconds()).padStart(2, '0')}` : ''} ${period}`;
    }
    
    return `${String(hours).padStart(2, '0')}${showSeconds ? ':' : Separator}${String(time.getMinutes()).padStart(2, '0')}${showSeconds ? `:${String(time.getSeconds()).padStart(2, '0')}` : ''}`;
  };
  
  return (
    <TimerContainer large={large}>
      {formatHour()}
    </TimerContainer>
  );
};

export default Timer;