// src/components/judging/RealtimeScoreView.jsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { formatPercentage } from '../../utils/formatters';
import { calculateRanking } from '../../utils/calculations';
import RealtimeScoreCard from './RealtimeScoreCard';
import ScoreAnimation from './ScoreAnimation';
import Button from '../common/Button';

const RealtimeScoreView = ({ 
  competitionId,
  participantId, 
  judgeId,
  rider,
  horse,
  parameters,
  onBackClick
}) => {
  const [totalScore, setTotalScore] = useState(0);
  const [percentage, setPercentage] = useState(0);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showAnimation, setShowAnimation] = useState(false);
  
  // Calcular puntaje total cuando cambian los scores o parámetros
  useEffect(() => {
    setLastUpdate(new Date());
  }, [parameters]);
  
  // Manejar calificación actualizada
  const handleScoreUpdated = (scores) => {
    try {
      // Calcular puntaje total
      const scoreValues = Object.values(scores).map(s => s.value);
      const paramData = parameters.reduce((obj, param) => {
        obj[param.id] = param;
        return obj;
      }, {});
      
      const ranking = calculateRanking(scores, paramData);
      
      setTotalScore(ranking.average);
      setPercentage(ranking.percentage);
      setLastUpdate(new Date());
      
      // Mostrar animación
      setShowAnimation(true);
      setTimeout(() => setShowAnimation(false), 3000);
    } catch (error) {
      console.error('Error calculando puntaje total:', error);
    }
  };
  
  // Formatear última actualización
  const getLastUpdateText = () => {
    if (!lastUpdate) return 'No hay datos';
    
    return lastUpdate.toLocaleTimeString('es-BO', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  // Alternar pantalla completa
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };
  
  const containerComponent = (content) => isFullscreen ? (
    <FullscreenContainer>
      {content}
      <ExitFullscreenButton onClick={toggleFullscreen}>
        ✕
      </ExitFullscreenButton>
    </FullscreenContainer>
  ) : (
    <Container>
      {content}
    </Container>
  );
  
  const content = (
    <>
      <Header>
        <HeaderLeft>
          <Title>Calificación en Tiempo Real</Title>
          <Subtitle>Sistema FEI (3 Celdas)</Subtitle>
        </HeaderLeft>
        
        <HeaderRight>
          <ScoreSummary>
            <ScoreLabel>Puntaje Total:</ScoreLabel>
            <ScoreValue>{totalScore.toFixed(2)}</ScoreValue>
            <ScorePercentage>{formatPercentage(percentage)}</ScorePercentage>
          </ScoreSummary>
        </HeaderRight>
      </Header>
      
      <ActionBar>
        <Button variant="outline" onClick={onBackClick}>
          Volver a la Competencia
        </Button>
        
        <Button variant="primary" onClick={toggleFullscreen}>
          {isFullscreen ? 'Salir de Pantalla Completa' : 'Modo Pantalla Completa'}
        </Button>
      </ActionBar>
      
      <RiderInfoCard>
        <RiderName>{rider?.firstName} {rider?.lastName}</RiderName>
        <HorseInfo>
          <Label>Caballo:</Label> {horse?.name} • 
          <Label>Categoría:</Label> {horse?.category}
        </HorseInfo>
        <UpdateInfo>
          <Label>Última actualización:</Label> {getLastUpdateText()}
        </UpdateInfo>
      </RiderInfoCard>
      
      <ScoreCardContainer>
        <RealtimeScoreCard
          rider={rider}
          horse={horse}
          parameters={parameters}
          competitionId={competitionId}
          participantId={participantId}
          judgeId={judgeId}
          onScoreUpdated={handleScoreUpdated}
        />
      </ScoreCardContainer>
      
      {/* Animación de puntaje */}
      <ScoreAnimation 
        score={totalScore} 
        percentage={percentage}
        isVisible={showAnimation}
      />
    </>
  );
  
  return containerComponent(content);
};

// Estilos
const Container = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
`;

const FullscreenContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${props => props.theme.colors.white};
  z-index: 1000;
  overflow-y: auto;
  padding: 24px;
`;

const ExitFullscreenButton = styled.button`
  position: fixed;
  top: 16px;
  right: 16px;
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1001;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
`;

const HeaderLeft = styled.div``;

const HeaderRight = styled.div``;

const Title = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin: 0;
`;

const Subtitle = styled.div`
  color: ${props => props.theme.colors.gray};
  margin-top: 4px;
`;

const ScoreSummary = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  padding: 12px 16px;
  border-radius: 8px;
`;

const ScoreLabel = styled.span`
  font-weight: 500;
`;

const ScoreValue = styled.span`
  font-size: 24px;
  font-weight: 700;
`;

const ScorePercentage = styled.span`
  font-size: 16px;
  opacity: 0.8;
`;

const RiderInfoCard = styled.div`
  background-color: ${props => props.theme.colors.background};
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
`;

const RiderName = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin: 0 0 8px;
`;

const HorseInfo = styled.div`
  margin-bottom: 8px;
`;

const UpdateInfo = styled.div`
  color: ${props => props.theme.colors.gray};
  font-size: 14px;
`;

const Label = styled.span`
  font-weight: 500;
  margin-right: 4px;
`;

const ActionBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
`;

const ScoreCardContainer = styled.div`
`;

export default RealtimeScoreView;