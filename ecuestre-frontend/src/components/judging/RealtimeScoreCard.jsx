import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { calculateParameterScore } from '../../utils/calculations';
import Button from '../common/Button';
import { useRealtimeSync } from '../../hooks/useRealtimeSync';

// Contenedor principal
const ScoreCardContainer = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.medium};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Encabezado con información del jinete
const RiderHeader = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
  padding-bottom: ${props => props.theme.spacing.md};
`;

const RiderName = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const HorseInfo = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
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
  
  /* Mejorar visibilidad para uso en campo */
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    th, td {
      padding: ${props => props.theme.spacing.sm};
      font-size: 14px;
    }
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

// Botones de acción
const ActionButtons = styled.div`
  display: flex;
  justify-content: space-between;
  gap: ${props => props.theme.spacing.md};
`;

// Indicador de estado
const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
  
  span {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: ${props => props.theme.spacing.xs};
    background-color: ${props => {
      switch(props.status) {
        case 'saved': return props.theme.colors.success;
        case 'offline': return props.theme.colors.warning;
        case 'pending': return props.theme.colors.accent;
        case 'error': return props.theme.colors.error;
        default: return props.theme.colors.gray;
      }
    }};
  }
`;

// Indicador de sincronización
const SyncIndicator = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  background-color: ${props => {
    switch (props.syncMethod) {
      case 'firebase': return props.theme.colors.accent;
      case 'websocket': return props.theme.colors.success;
      case 'both': return props.theme.colors.primary;
      default: return props.theme.colors.error;
    }
  }};
  color: ${props => props.theme.colors.white};
  margin-bottom: 10px;
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.fontSizes.small};
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

/**
 * Componente RealtimeScoreCard para calificación FEI en tiempo real
 * Utiliza WebSockets y Firebase para sincronización
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Object} props.rider - Información del jinete
 * @param {Object} props.horse - Información del caballo
 * @param {Array} props.parameters - Parámetros a evaluar
 * @param {number} props.competitionId - ID de la competencia
 * @param {number} props.participantId - ID del participante
 * @param {number} props.judgeId - ID del juez actual
 */
const RealtimeScoreCard = ({
  rider,
  horse,
  parameters,
  competitionId,
  participantId,
  judgeId
}) => {
  // Estado para almacenar las calificaciones
  const [scores, setScores] = useState({});
  // Estado para almacenar los resultados calculados
  const [results, setResults] = useState({});
  // Estado para almacenar comentarios
  const [comments, setComments] = useState({});
  // Estado para indicar si hay cambios sin guardar
  const [hasChanges, setHasChanges] = useState(false);
  // Estado para almacenar el motivo de edición
  const [editReason, setEditReason] = useState('');
  // Estado para el estado de guardado
  const [savedStatus, setSavedStatus] = useState('');
  
  // Usar el hook de sincronización en tiempo real
  const { 
    isOnline, 
    syncMethod,
    subscribeToRealtimeScores,
    sendScoreUpdate
  } = useRealtimeSync();
  
  // Suscribirse a actualizaciones de calificaciones
  useEffect(() => {
    if (!competitionId || !participantId) return () => {};
    
    const handleScoresUpdate = (data) => {
      if (!data) {
        console.warn('Datos de calificaciones inválidos');
        return;
      }
      
      // Procesar las calificaciones del juez actual
      const judgeData = data[judgeId];
      if (!judgeData || !judgeData.parameters) return;
      
      const paramScores = {};
      const paramComments = {};
      const paramResults = {};
      
      // Procesar cada parámetro
      Object.entries(judgeData.parameters).forEach(([paramId, scoreData]) => {
        paramScores[paramId] = scoreData.value;
        paramComments[paramId] = scoreData.comments || '';
        paramResults[paramId] = scoreData.calculatedResult;
      });
      
      setScores(paramScores);
      setComments(paramComments);
      setResults(paramResults);
      setHasChanges(false);
    };
    
    // Suscribirse a ambos métodos de sincronización
    const unsubscribe = subscribeToRealtimeScores(
      competitionId, 
      participantId, 
      handleScoresUpdate
    );
    
    return unsubscribe;
  }, [competitionId, participantId, judgeId, subscribeToRealtimeScores]);
  
  // Manejar cambio en calificación
  const handleScoreChange = useCallback((paramId, value) => {
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
        const result = calculateParameterScore(numValue, parameter.coefficient);
        setResults(prev => ({
          ...prev,
          [paramId]: result
        }));
      } catch (error) {
        console.error('Error al calcular resultado:', error);
      }
    }
    
    setHasChanges(true);
  }, [parameters]);
  
  // Manejar cambio en comentarios
  const handleCommentChange = useCallback((paramId, value) => {
    setComments(prev => ({
      ...prev,
      [paramId]: value
    }));
    setHasChanges(true);
  }, []);
  
  // Guardar calificaciones
  const handleSave = useCallback(() => {
    setSavedStatus('pending');
    
    try {
      // Preparar datos para guardar
      const scoreData = {};
      
      parameters.forEach(param => {
        const paramId = param.id.toString();
        if (scores[paramId] !== undefined) {
          scoreData[paramId] = {
            parameter_id: param.id,
            value: scores[paramId],
            comments: comments[paramId] || '',
          };
        }
      });
      
      // Enviar datos
      sendScoreUpdate(
        competitionId,
        participantId,
        judgeId,
        scoreData
      );
      
      setSavedStatus(isOnline ? 'saved' : 'offline');
      setHasChanges(false);
    } catch (error) {
      console.error('Error al guardar calificaciones:', error);
      setSavedStatus('error');
    }
  }, [
    competitionId, 
    participantId, 
    judgeId, 
    scores, 
    comments, 
    parameters, 
    sendScoreUpdate, 
    isOnline
  ]);
  
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
  
  // Obtener texto según el método de sincronización
  const getSyncMethodText = () => {
    switch (syncMethod) {
      case 'firebase': return 'Sincronización vía Firebase';
      case 'websocket': return 'Sincronización vía WebSocket';
      case 'both': return 'Sincronización redundante (Firebase + WebSocket)';
      default: return 'Sin conexión';
    }
  };
  
  return (
    <ScoreCardContainer>
      <RiderHeader>
        <RiderName>{rider.firstName} {rider.lastName}</RiderName>
        <HorseInfo>
          Caballo: <strong>{horse.name}</strong> | Categoría: {horse.category}
        </HorseInfo>
      </RiderHeader>
      
      <SyncIndicator syncMethod={syncMethod}>
        {getSyncMethodText()}
      </SyncIndicator>
      
      {/* Indicador de estado */}
      {savedStatus && (
        <StatusIndicator status={getSaveStatus()}>
          <span />
          {getStatusText()}
        </StatusIndicator>
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
      
      {/* Motivo de edición (solo si hay calificaciones previas) */}
      {Object.keys(scores).length > 0 && (
        <CommentsContainer>
          <CommentsTitle>Motivo de edición</CommentsTitle>
          <CommentsTextarea
            placeholder="Ingrese el motivo por el que está modificando las calificaciones"
            value={editReason}
            onChange={(e) => setEditReason(e.target.value)}
          />
        </CommentsContainer>
      )}
      
      {/* Botones de acción */}
      <ActionButtons>
        <Button
          variant="primary"
          size="large"
          onClick={handleSave}
          disabled={!hasChanges}
          fullWidth
        >
          {isOnline ? 'Guardar Calificación' : 'Guardar Localmente'}
        </Button>
      </ActionButtons>
    </ScoreCardContainer>
  );
};

export default RealtimeScoreCard;