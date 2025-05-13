// src/pages/JudgingPanel.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
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

// Tarjeta de información del participante
const ParticipantCard = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const ParticipantInfo = styled.div`
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
`;

const InfoColumn = styled.div`
  flex: 1;
  min-width: 250px;
`;

const InfoItem = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
`;

const InfoLabel = styled.div`
  font-weight: 500;
  color: ${props => props.theme.colors.gray};
  font-size: ${props => props.theme.fontSizes.small};
`;

const InfoValue = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
`;

// Navegación entre participantes
const Navigation = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Panel temporal
const TemporaryPanel = styled.div`
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.lg};
  
  h2 {
    color: ${props => props.theme.colors.primary};
    margin-bottom: ${props => props.theme.spacing.md};
  }
  
  p {
    margin-bottom: ${props => props.theme.spacing.lg};
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  justify-content: center;
  gap: ${props => props.theme.spacing.md};
`;

// Indicador de conexión
const ConnectionIndicator = styled.div`
  display: inline-flex;
  align-items: center;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  background-color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.warning};
  color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.fontSizes.small};
  margin-bottom: ${props => props.theme.spacing.md};
  
  &:before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: ${props => props.theme.colors.white};
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

// Tabla de calificaciones
const ScoreTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-bottom: ${props => props.theme.spacing.lg};
  
  th, td {
    border: 1px solid ${props => props.theme.colors.lightGray};
    padding: ${props => props.theme.spacing.md};
    text-align: center;
  }
  
  th {
    background-color: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.white};
    font-weight: 600;
  }
`;

// Celda de parámetro (primera columna)
const ParameterCell = styled.td`
  text-align: left;
  font-weight: 500;
  background-color: ${props => props.theme.colors.lightGray};
`;

// Entrada numérica para calificación
const ScoreInput = styled.input`
  width: 60px;
  height: 40px;
  text-align: center;
  font-size: ${props => props.theme.fontSizes.large};
  font-weight: 600;
  border: 2px solid ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.small};
  
  /* Mayor tamaño para uso móvil */
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
`;

// Celda de resultado calculado
const ResultCell = styled.td`
  font-weight: 600;
  font-size: ${props => props.theme.fontSizes.large};
  background-color: ${props => props.theme.colors.lightGray};
  color: ${props => props.theme.colors.text};
`;

// Área de comentarios
const CommentsContainer = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const CommentsTitle = styled.h3`
  font-size: ${props => props.theme.fontSizes.medium};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const CommentsTextarea = styled.textarea`
  width: 100%;
  min-height: 80px;
  padding: ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.lightGray};
  border-radius: ${props => props.theme.borderRadius.small};
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.medium};
  resize: vertical;
`;

// Botones de acción
const ActionButtons = styled.div`
  display: flex;
  justify-content: space-between;
  gap: ${props => props.theme.spacing.md};
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
 * Panel de calificación FEI para jueces
 */
const JudgingPanel = () => {
  const { competition_id, participant_id } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const { currentCompetition, participants, loading, error, loadCompetition } = useContext(CompetitionContext);
  const { isOnline } = useOffline();
  
  const [currentParticipant, setCurrentParticipant] = useState(null);
  const [parameters, setParameters] = useState([]);
  const [scores, setScores] = useState({});
  const [results, setResults] = useState({});
  const [comments, setComments] = useState({});
  const [hasChanges, setHasChanges] = useState(false);
  const [savedStatus, setSavedStatus] = useState('');
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
        const { parameters: params, scores: initialScores } = response.data;
        
        setParameters(params);
        setScores(initialScores[user.id] || {});
        
        // Calcular resultados iniciales
        const initialResults = {};
        Object.entries(initialScores[user.id] || {}).forEach(([paramId, scoreData]) => {
          if (scoreData && scoreData.calculated_result) {
            initialResults[paramId] = scoreData.calculated_result;
          }
        });
        
        setResults(initialResults);
        
        // Obtener comentarios
        const initialComments = {};
        Object.entries(initialScores[user.id] || {}).forEach(([paramId, scoreData]) => {
          if (scoreData && scoreData.comments) {
            initialComments[paramId] = scoreData.comments;
          }
        });
        
        setComments(initialComments);
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
  
  // Manejar cambio en calificación
  const handleScoreChange = (paramId, value) => {
    // Validar que sea un número entre 0 y 10
    const numValue = parseFloat(value);
    if (isNaN(numValue) || numValue < 0 || numValue > 10) {
      return;
    }
    
    // Actualizar calificaciones
    setScores(prev => ({
      ...prev,
      [paramId]: numValue
    }));
    
    // Calcular resultado
    const parameter = parameters.find(p => p.id === parseInt(paramId));
    if (parameter) {
      try {
        // Fórmula básica FEI: resultado = calificación * coeficiente (máximo 10)
        let result = numValue * parameter.coefficient;
        result = Math.min(result, 10);
        result = Math.round(result * 10) / 10; // Redondear a 1 decimal
        
        setResults(prev => ({
          ...prev,
          [paramId]: result
        }));
      } catch (error) {
        console.error('Error al calcular resultado:', error);
      }
    }
    
    setHasChanges(true);
  };
  
  // Manejar cambio en comentarios
  const handleCommentChange = (paramId, value) => {
    setComments(prev => ({
      ...prev,
      [paramId]: value
    }));
    setHasChanges(true);
  };
  
  // Guardar calificaciones
  const handleSave = async () => {
  setSavedStatus('pending');
  
  try {
    // Preparar datos para enviar
    const scoreData = {};
    
    parameters.forEach(param => {
      if (scores[param.id] !== undefined) {
        scoreData[param.id] = {
          value: scores[param.id],
          comments: comments[param.id] || '',
        };
      }
    });
    
    // Importar dinámicamente para evitar ciclos de dependencia
    const apiModule = await import('../services/api');
    
    // Enviar al servidor
    await apiModule.submitScore(
      competition_id,
      participant_id,
      {
        judge_id: user.id,
        scores: Object.entries(scoreData).map(([paramId, data]) => ({
          parameter_id: parseInt(paramId),
          value: data.value,
          comments: data.comments
        }))
      }
    );
    
    setSavedStatus(isOnline ? 'saved' : 'offline');
    setHasChanges(false);
  } catch (error) {
    console.error('Error al guardar calificaciones:', error);
    setSavedStatus('error');
  }
};
  
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
  
  // Generar estado de guardado
  const getSaveStatus = () => {
    if (hasChanges) {
      return 'pending';
    }
    return savedStatus;
  };
  
  // Texto de estado
  const getStatusText = () => {
    if (hasChanges) {
      return 'Cambios sin guardar';
    }
    
    switch (savedStatus) {
      case 'saved': return 'Guardado correctamente';
      case 'offline': return 'Guardado localmente (sin conexión)';
      case 'pending': return 'Guardando...';
      case 'error': return 'Error al guardar';
      default: return '';
    }
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
  
  return (
    <Layout>
      <JudgingContainer>
        <Header>
          <Title>Panel de Calificación FEI (3 Celdas)</Title>
          <Subtitle>{currentCompetition.name}</Subtitle>
        </Header>
        
        <ConnectionIndicator isOnline={isOnline}>
          {isOnline ? 'Conectado' : 'Modo Offline - Los cambios se sincronizarán cuando vuelva la conexión'}
        </ConnectionIndicator>
        
        <ButtonGroup style={{ marginBottom: '16px' }}>
          <Button
            variant="outline"
            onClick={() => setShowHelpModal(true)}
          >
            Ayuda Sistema FEI
          </Button>
          
          <Button
            as={Link}
            to={`/competitions/${competition_id}`}
            variant="outline"
          >
            Volver a la Competencia
          </Button>
        </ButtonGroup>
        
        <Navigation>
          <Button
            variant="outline"
            onClick={() => navigateToParticipant('prev')}
            disabled={participants.length <= 1}
          >
            ← Anterior
          </Button>
          
          <div>
            Participante {participants.findIndex(p => p.id === parseInt(participant_id)) + 1} de {participants.length}
          </div>
          
          <Button
            variant="outline"
            onClick={() => navigateToParticipant('next')}
            disabled={participants.length <= 1}
          >
            Siguiente →
          </Button>
        </Navigation>
        
        <ParticipantCard>
          <h2>Información del Participante</h2>
          <ParticipantInfo>
            <InfoColumn>
              <InfoItem>
                <InfoLabel>Jinete</InfoLabel>
                <InfoValue>
                  {currentParticipant.rider_details 
                    ? `${currentParticipant.rider_details.first_name} ${currentParticipant.rider_details.last_name}` 
                    : 'Desconocido'}
                </InfoValue>
              </InfoItem>
              
              <InfoItem>
                <InfoLabel>Número de Participante</InfoLabel>
                <InfoValue>{currentParticipant.number}</InfoValue>
              </InfoItem>
              
              <InfoItem>
                <InfoLabel>Orden de Salida</InfoLabel>
                <InfoValue>{currentParticipant.order}</InfoValue>
              </InfoItem>
            </InfoColumn>
            
            <InfoColumn>
              <InfoItem>
                <InfoLabel>Caballo</InfoLabel>
                <InfoValue>
                  {currentParticipant.horse_details 
                    ? currentParticipant.horse_details.name 
                    : 'Desconocido'}
                </InfoValue>
              </InfoItem>
              
              <InfoItem>
                <InfoLabel>Raza</InfoLabel>
                <InfoValue>
                  {currentParticipant.horse_details && currentParticipant.horse_details.breed 
                    ? currentParticipant.horse_details.breed 
                    : 'No especificada'}
                </InfoValue>
              </InfoItem>
              
              <InfoItem>
                <InfoLabel>Categoría</InfoLabel>
                <InfoValue>
                  {currentParticipant.category_details 
                    ? currentParticipant.category_details.name 
                    : 'Desconocida'}
                </InfoValue>
              </InfoItem>
            </InfoColumn>
          </ParticipantInfo>
        </ParticipantCard>
        
        {/* Indicador de estado */}
        {savedStatus && (
          <div style={{ marginBottom: '16px' }}>
            <ConnectionIndicator isOnline={savedStatus === 'saved'}>
              {getStatusText()}
            </ConnectionIndicator>
          </div>
        )}
        
        {/* Tabla de calificaciones */}
        <ScoreTable>
          <thead>
            <tr>
              <th>Parámetro</th>
              <th>Máximo</th>
              <th>Coeficiente</th>
              <th>Calificación</th>
              <th>Resultado</th>
            </tr>
          </thead>
          <tbody>
            {parameters.map(param => (
              <tr key={param.id}>
                <ParameterCell>{param.name}</ParameterCell>
                <td>10</td>
                <td>{param.coefficient}</td>
                <td>
                  <ScoreInput
                    type="number"
                    min="0"
                    max="10"
                    step="0.5"
                    value={scores[param.id] || ''}
                    onChange={(e) => handleScoreChange(param.id, e.target.value)}
                    aria-label={`Calificación para ${param.name}`}
                  />
                </td>
                <ResultCell>{results[param.id] || 0}</ResultCell>
              </tr>
            ))}
          </tbody>
        </ScoreTable>
        
        {/* Área de comentarios por parámetro */}
        <CommentsContainer>
          <CommentsTitle>Comentarios</CommentsTitle>
          {parameters.map(param => (
            <div key={`comment-${param.id}`} style={{ marginBottom: '1rem' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>{param.name}</div>
              <CommentsTextarea
                placeholder={`Comentarios para ${param.name}`}
                value={comments[param.id] || ''}
                onChange={(e) => handleCommentChange(param.id, e.target.value)}
              />
            </div>
          ))}
        </CommentsContainer>
        
        {/* Botones de acción */}
        <ActionButtons>
          <Button
            variant="primary"
            size="large"
            onClick={handleSave}
            disabled={!hasChanges}
          >
            {isOnline ? 'Guardar Calificación' : 'Guardar Localmente'}
          </Button>
        </ActionButtons>
        
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