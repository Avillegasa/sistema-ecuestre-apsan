import React, { useState, useEffect, useContext } from 'react';
import styled from 'styled-components';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { CompetitionContext } from '../../context/CompetitionContext';
import useOffline from '../../hooks/useOffline';
import { fetchScorecard, submitScore } from '../../services/api';
import { subscribeToScores, updateScore } from '../../services/firebase';
import ScoreCard from './ScoreCard';
import Button from '../common/Button';
import Modal from '../common/Modal';

// Contenedor principal
const JudgingFormContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.lg};
`;

// Cabecera
const Header = styled.header`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Title = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const CompetitionInfo = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
`;

// Barra de navegación entre jinetes
const RiderNavigation = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.lg};
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.medium};
`;

const RiderInfo = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  font-weight: 500;
`;

// Indicador de conexión
const ConnectionIndicator = styled.div`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background-color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.warning};
  color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.small};
  margin-bottom: ${props => props.theme.spacing.md};
  
  span {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: ${props => props.theme.colors.white};
    margin-right: ${props => props.theme.spacing.sm};
  }
`;

// Componente de pantalla completa
const FullscreenContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${props => props.theme.colors.white};
  z-index: 1000;
  overflow-y: auto;
  padding: ${props => props.theme.spacing.lg};
`;

const ExitFullscreenButton = styled.button`
  position: fixed;
  top: ${props => props.theme.spacing.md};
  right: ${props => props.theme.spacing.md};
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

// Barra de acciones
const ActionBar = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Contenedor de información de parámetro
const ParameterInfoContainer = styled.div`
  background-color: ${props => props.theme.colors.background};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.small};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ParameterTitle = styled.h3`
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ParameterDescription = styled.p`
  margin-bottom: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.gray};
`;

/**
 * Componente JudgingForm para la evaluación de jinetes
 */
const JudgingForm = () => {
  const { competitionId, participantId } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const { currentCompetition, participants, loadCompetition } = useContext(CompetitionContext);
  const { isOnline, saveScore, pendingActions, forceSyncPendingActions } = useOffline();
  
  // Estados locales
  const [participant, setParticipant] = useState(null);
  const [parameters, setParameters] = useState([]);
  const [scores, setScores] = useState({});
  const [savedStatus, setSavedStatus] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [selectedParameterInfo, setSelectedParameterInfo] = useState(null);
  const [showPendingModal, setShowPendingModal] = useState(false);
  
  // Cargar datos de la competencia si no existen
  useEffect(() => {
    if (!currentCompetition) {
      loadCompetition(parseInt(competitionId));
    }
  }, [competitionId, currentCompetition, loadCompetition]);
  
  // Obtener datos del participante
  useEffect(() => {
    if (participants && participants.length > 0) {
      const found = participants.find(p => p.id === parseInt(participantId));
      if (found) {
        setParticipant(found);
      }
    }
  }, [participantId, participants]);
  
  // Cargar parámetros y calificaciones
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Obtener tarjeta de calificación
        const response = await fetchScorecard(competitionId, participantId);
        const { parameters: params, scores: initialScores } = response.data;
        
        setParameters(params);
        setScores(initialScores[user.id] || {});
        
        setIsLoading(false);
      } catch (err) {
        console.error('Error al cargar datos:', err);
        setError('Error al cargar los datos de calificación');
        setIsLoading(false);
      }
    };
    
    if (competitionId && participantId && user) {
      loadData();
    }
  }, [competitionId, participantId, user]);
  
  // Suscribirse a cambios en tiempo real
  useEffect(() => {
    if (!competitionId || !participantId || !user) return;
    
    const unsubscribe = subscribeToScores(
      competitionId,
      participantId,
      (data) => {
        if (data && data[user.id]) {
          setScores(data[user.id]);
        }
      }
    );
    
    return () => unsubscribe();
  }, [competitionId, participantId, user]);
  
  // Manejar guardado de calificaciones
  const handleSaveScores = async (scoreData) => {
    setSavedStatus('pending');
    
    try {
      // Preparar datos para enviar
      const submitData = {
        scores: Object.entries(scoreData).map(([paramId, data]) => ({
          parameter_id: parseInt(paramId),
          value: data.value,
          comments: data.comments || ''
        })),
        edit_reason: scoreData.editReason || ''
      };
      
      // Guardar usando el hook de offline
      const result = await saveScore(
        parseInt(competitionId),
        parseInt(participantId),
        user.id,
        submitData
      );
      
      if (result.success) {
        setSavedStatus(result.offline ? 'offline' : 'saved');
        
        // Si está online, actualizar también en Firebase
        if (isOnline) {
          // Transformar datos para Firebase
          const firebaseData = {};
          Object.entries(scoreData).forEach(([paramId, data]) => {
            if (paramId !== 'editReason') {
              firebaseData[paramId] = {
                value: data.value,
                comments: data.comments || ''
              };
            }
          });
          
          await updateScore(
            competitionId,
            participantId,
            user.id,
            firebaseData
          );
        }
        
        // Mostrar notificación de acciones pendientes si hay
        if (pendingActions.length > 0 && isOnline) {
          setShowPendingModal(true);
        }
      } else {
        setSavedStatus('error');
      }
    } catch (err) {
      console.error('Error al guardar calificaciones:', err);
      setSavedStatus('error');
    }
  };
  
  // Navegar al siguiente o anterior participante
  const navigateToParticipant = (direction) => {
    if (!participants || participants.length === 0) return;
    
    const currentIndex = participants.findIndex(p => p.id === parseInt(participantId));
    if (currentIndex === -1) return;
    
    let newIndex;
    if (direction === 'next') {
      newIndex = (currentIndex + 1) % participants.length;
    } else {
      newIndex = (currentIndex - 1 + participants.length) % participants.length;
    }
    
    navigate(`/judging/${competitionId}/${participants[newIndex].id}`);
  };
  
  // Mostrar información del parámetro seleccionado
  const showParameterInfo = (parameter) => {
    setSelectedParameterInfo(parameter);
    setShowHelpModal(true);
  };
  
  // Sincronizar datos pendientes
  const handleSyncPending = () => {
    forceSyncPendingActions();
    setShowPendingModal(false);
  };
  
  // Alternar modo pantalla completa
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };
  
  // Si está cargando, mostrar spinner o mensaje
  if (isLoading) {
    return (
      <JudgingFormContainer>
        <p>Cargando datos de calificación...</p>
      </JudgingFormContainer>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (error) {
    return (
      <JudgingFormContainer>
        <p>{error}</p>
        <Button onClick={() => navigate('/competitions')}>
          Volver a Competencias
        </Button>
      </JudgingFormContainer>
    );
  }
  
  // Si no hay participante, mostrar mensaje
  if (!participant) {
    return (
      <JudgingFormContainer>
        <p>No se encontró el participante</p>
        <Button onClick={() => navigate('/competitions')}>
          Volver a Competencias
        </Button>
      </JudgingFormContainer>
    );
  }
  
  // Contenido principal
  const content = (
    <>
      <Header>
        <Title>Panel de Calificación FEI (3 Celdas)</Title>
        <CompetitionInfo>
          {currentCompetition?.name} - {new Date(currentCompetition?.date).toLocaleDateString()}
        </CompetitionInfo>
      </Header>
      
      <ConnectionIndicator isOnline={isOnline}>
        <span />
        {isOnline ? 'Conectado' : 'Modo Offline - Los cambios se sincronizarán cuando vuelva la conexión'}
      </ConnectionIndicator>
      
      <ActionBar>
        <Button
          variant="outline"
          onClick={() => setShowHelpModal(true)}
        >
          Ayuda Sistema FEI
        </Button>
        
        {pendingActions.length > 0 && isOnline && (
          <Button
            variant="warning"
            onClick={() => setShowPendingModal(true)}
          >
            Sincronizar {pendingActions.length} calificaciones pendientes
          </Button>
        )}
        
        <Button
          variant="primary"
          onClick={toggleFullscreen}
        >
          {isFullscreen ? 'Salir de Pantalla Completa' : 'Modo Pantalla Completa'}
        </Button>
      </ActionBar>
      
      <RiderNavigation>
        <Button
          variant="outline"
          size="small"
          onClick={() => navigateToParticipant('prev')}
        >
          &larr; Anterior
        </Button>
        
        <RiderInfo>
          Jinete {participant.order} de {participants.length}
        </RiderInfo>
        
        <Button
          variant="outline"
          size="small"
          onClick={() => navigateToParticipant('next')}
        >
          Siguiente &rarr;
        </Button>
      </RiderNavigation>
      
      <ScoreCard
        rider={participant.rider}
        horse={participant.horse}
        parameters={parameters}
        initialScores={scores}
        onSave={handleSaveScores}
        isOffline={!isOnline}
        savedStatus={savedStatus}
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
          
          <p><strong>Fórmula de cálculo:</strong> Calificación Final = Calificación del Juez × Coeficiente</p>
          
          <p>El resultado final nunca debe exceder 10 puntos y debe ser un número entero.</p>
          
          {selectedParameterInfo && (
            <ParameterInfoContainer>
              <ParameterTitle>{selectedParameterInfo.name}</ParameterTitle>
              <ParameterDescription>{selectedParameterInfo.description}</ParameterDescription>
              <p><strong>Coeficiente:</strong> {selectedParameterInfo.coefficient}</p>
            </ParameterInfoContainer>
          )}
          
          <h3>Parámetros de esta Competencia</h3>
          <div>
            {parameters.map(param => (
              <Button 
                key={param.id} 
                variant="text" 
                onClick={() => showParameterInfo(param)}
                style={{ margin: '0.25rem' }}
              >
                {param.name}
              </Button>
            ))}
          </div>
        </div>
      </Modal>
      
      {/* Modal de sincronización pendiente */}
      <Modal
        isOpen={showPendingModal}
        onClose={() => setShowPendingModal(false)}
        title="Calificaciones Pendientes de Sincronización"
        size="medium"
      >
        <div>
          <p>Tiene {pendingActions.length} calificaciones pendientes de sincronizar con el servidor.</p>
          <p>Estos son datos que se guardaron mientras estaba sin conexión.</p>
          <p>¿Desea sincronizar estos datos ahora?</p>
          
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
            <Button variant="outline" onClick={() => setShowPendingModal(false)}>
              Más tarde
            </Button>
            <Button variant="primary" onClick={handleSyncPending}>
              Sincronizar ahora
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
  
  // Renderizar en pantalla normal o completa
  return isFullscreen ? (
    <FullscreenContainer>
      {content}
      <ExitFullscreenButton onClick={toggleFullscreen}>
        ✕
      </ExitFullscreenButton>
    </FullscreenContainer>
  ) : (
    <JudgingFormContainer>
      {content}
    </JudgingFormContainer>
  );
};

export default JudgingForm;