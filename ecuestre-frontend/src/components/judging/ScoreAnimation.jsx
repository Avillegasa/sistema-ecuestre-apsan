// src/components/judging/ScoreAnimation.jsx
import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { formatPercentage } from '../../utils/formatters';

/**
 * Componente para mostrar una animación cuando cambia una calificación
 */
const ScoreAnimation = ({ score, percentage, isVisible }) => {
  const [prevScore, setPrevScore] = useState(score);
  const [isIncreasing, setIsIncreasing] = useState(null);
  
  useEffect(() => {
    if (score !== prevScore) {
      setIsIncreasing(score > prevScore);
      setPrevScore(score);
    }
  }, [score, prevScore]);
  
  if (!isVisible) return null;
  
  return (
    <AnimationContainer>
      <ScoreValue isIncreasing={isIncreasing}>
        {score ? score.toFixed(1) : '0.0'}
      </ScoreValue>
      <PercentageValue>
        {formatPercentage(percentage)}
      </PercentageValue>
    </AnimationContainer>
  );
};

// Animaciones
const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const fadeInDown = keyframes`
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const pulse = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
`;

// Estilos
const AnimationContainer = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1000;
  animation: ${fadeInUp} 0.3s ease-out, ${pulse} 1s ease-in-out;
`;

const ScoreValue = styled.div`
  font-size: 28px;
  font-weight: 700;
  animation: ${props => props.isIncreasing === true ? fadeInUp : props.isIncreasing === false ? fadeInDown : 'none'} 0.3s ease-out;
  color: ${props => props.isIncreasing === true ? '#4CFF4C' : props.isIncreasing === false ? '#FF4C4C' : 'white'};
`;

const PercentageValue = styled.div`
  font-size: 16px;
  opacity: 0.8;
`;

export default ScoreAnimation;