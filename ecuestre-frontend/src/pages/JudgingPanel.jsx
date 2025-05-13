// src/pages/JudgingPanel.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import RealtimeScoreView from '../components/judging/RealtimeScoreView';
import Modal from '../components/common/Modal';
import Button from '../components/common/Button';
import { AuthContext } from '../context/AuthContext';
import { CompetitionContext } from '../context/CompetitionContext';
import useOffline from '../hooks/useOffline';
import { fetchScorecard } from '../services/api';

// Contenedor principal
const JudgingContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

// Cabecera
const Header = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Subtitle = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
`;

// Navegación entre participantes
const Navigation = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Mensaje de error
const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Estado de carga
const LoadingMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.gray};
`;

/**
 * Panel de calificación FEI para jueces - Versión mejorada con soporte en tiempo real
 */
const JudgingPanel = () => {
  const { competition_id, participant_id } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const { currentCompetition, participants, loading, error, loadCompetition } = useContext(CompetitionContext);
  const { isOnline } = useOffline();
  
  const [currentParticipant, setCurrentParticipant] = useState(null);
  const [parameters, setParameters] = useState([]);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [scorecardError, setScorecardError] = useState(null);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(competition_id));
  }, [competition_id, loadCompetition]);
  
  // Obtener participante actual
  useEffect(() => {
    if (participants && participants.length > 0) {
      const participant = participants.find(p => p.id === parseInt(participant_id));
      setCurrentParticipant(participant);
    }
  }, [participant_id, participants]);
  
  // Cargar scorecard
  useEffect(() => {
    const loadScorecard = async () => {
      setIsLoading(true);
      setScorecardError(null);
      
      try {
        const response = await fetchScorecard(competition_id, participant_id);
        const { parameters: params } = response.data;
        
        setParameters(params);
      } catch (err) {
        console.error('Error al cargar scorecard:', err);
        setScorecardError('Error al cargar la tarjeta de calificación. ' + err.message);
      } finally {
        setIsLoading(false);
      }
    };
    
    if (user && user.id) {
      loadScorecard();
    }
  }, [competition_id, participant_id, user]);
  
  // Navegar al participante anterior/siguiente
  const navigateToParticipant = (direction) => {
    if (!participants || participants.length === 0) return;
    
    const currentIndex = participants.findIndex(p => p.id === parseInt(participant_id));
    if (currentIndex === -1) return;
    
    let newIndex;
    if (direction === 'prev') {
      newIndex = (currentIndex - 1 + participants.length) % participants.length;
    } else {
      newIndex = (currentIndex + 1) % participants.length;
    }
    
    navigate(`/judging/${competition_id}/${participants[newIndex].id}`);
  };
  
  // Si está cargando, mostrar mensaje
  if (loading || isLoading) {
    return (
      <Layout>
        <JudgingContainer>
          <LoadingMessage>Cargando datos...</LoadingMessage>
        </JudgingContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (error || scorecardError) {
    return (
      <Layout>
        <JudgingContainer>
          <ErrorMessage>{error || scorecardError}</ErrorMessage>
          <Button as={Link} to="/competitions">Volver a Competencias</Button>
        </JudgingContainer>
      </Layout>
    );
  }
  
  // Si no hay competencia o participante, mostrar mensaje
  if (!currentCompetition || !currentParticipant) {
    return (
      <Layout>
        <JudgingContainer>
          <ErrorMessage>No se encontraron los datos necesarios.</ErrorMessage>
          <Button as={Link} to="/competitions">Volver a Competencias</Button>
        </JudgingContainer>
      </Layout>
    );
  }
  
  // Conversiones de formato para mantener compatibilidad
  const riderData = {
    firstName: currentParticipant.rider_details?.first_name || '',
    lastName: currentParticipant.rider_details?.last_name || '',
  };
  
  const horseData = {
    name: currentParticipant.horse_details?.name || '',
    category: currentParticipant.category_details?.name || '',
    breed: currentParticipant.horse_details?.breed || '',
  };
  
  return (
    <Layout>
      <JudgingContainer>
        <Header>
          <Title>Panel de Calificación FEI (3 Celdas)</Title>
          <Subtitle>{currentCompetition.name}</Subtitle>
        </Header>
        
        <Navigation>
          <Button
            variant="outline"
            onClick={() => navigateToParticipant('prev')}
            disabled={participants.length <= 1}
          >
            ← Anterior
          </Button>
          
          <Button
            variant="outline"
            onClick={() => setShowHelpModal(true)}
          >
            Ayuda Sistema FEI
          </Button>
          
          <Button
            variant="outline"
            onClick={() => navigateToParticipant('next')}
            disabled={participants.length <= 1}
          >
            Siguiente →
          </Button>
        </Navigation>
        
        <RealtimeScoreView
          competitionId={parseInt(competition_id)}
          participantId={parseInt(participant_id)}
          judgeId={user.id}
          rider={riderData}
          horse={horseData}
          parameters={parameters}
          onBackClick={() => navigate(`/competitions/${competition_id}`)}
        />
        
        {/* Modal de Ayuda */}
        <Modal
          isOpen={showHelpModal}
          onClose={() => setShowHelpModal(false)}
          title="Sistema de Calificación FEI (3 Celdas)"
          size="large"
        >
          <div>
            <h3>Explicación del Sistema FEI</h3>
            <p>El sistema de 3 celdas de la Federación Ecuestre Internacional (FEI) funciona de la siguiente manera:</p>
            
            <ul>
              <li><strong>Celda 1 (Máximo):</strong> Siempre es 10 puntos, el valor máximo posible.</li>
              <li><strong>Celda 2 (Coeficiente):</strong> Valor multiplicador según las tablas FEI, varía dependiendo de la importancia del parámetro.</li>
              <li><strong>Celda 3 (Calificación del Juez):</strong> Su puntuación, de 0 a 10 puntos.</li>
            </ul>
            
            <p><strong>Fórmula de cálculo:</strong> Resultado = Calificación del Juez × Coeficiente</p>
            <p>El resultado final nunca debe exceder 10 puntos y debe ser un número entero.</p>
            
            <h3>Escala de Calificación FEI</h3>
            <ul>
              <li><strong>10:</strong> Excelente</li>
              <li><strong>9:</strong> Muy Bueno</li>
              <li><strong>8:</strong> Bueno</li>
              <li><strong>7:</strong> Bastante Bueno</li>
              <li><strong>6:</strong> Satisfactorio</li>
              <li><strong>5:</strong> Suficiente</li>
              <li><strong>4:</strong> Insuficiente</li>
              <li><strong>3:</strong> Bastante Malo</li>
              <li><strong>2:</strong> Malo</li>
              <li><strong>1:</strong> Muy Malo</li>
              <li><strong>0:</strong> No Ejecutado</li>
            </ul>
            
            <p>Se recomienda usar decimales (0.5) para proporcionar una evaluación más precisa entre dos niveles consecutivos.</p>
            
            <div style={{ marginTop: '20px', textAlign: 'center' }}>
              <Button as={Link} to="/help/fei" variant="primary" target="_blank">
                Ver Guía Completa del Sistema FEI
              </Button>
            </div>
          </div>
        </Modal>
      </JudgingContainer>
    </Layout>
  );
};

export default JudgingPanel;