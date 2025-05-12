import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { calculateParameterScore } from '../../utils/calculations';
import Button from '../common/Button';

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
 * Componente ScoreCard para calificación FEI
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Object} props.rider - Información del jinete
 * @param {Object} props.horse - Información del caballo
 * @param {Array} props.parameters - Parámetros a evaluar
 * @param {Object} [props.initialScores={}] - Calificaciones iniciales
 * @param {Function} props.onSave - Función para guardar calificaciones
 * @param {boolean} [props.isOffline=false] - Si está en modo offline
 * @param {string} [props.savedStatus=''] - Estado de guardado (saved, offline, pending, error)
 */
const ScoreCard = ({
  rider,
  horse,
  parameters,
  initialScores = {},
  onSave,
  isOffline = false,
  savedStatus = ''
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
  
  // Inicializar calificaciones con valores iniciales
  useEffect(() => {
    setScores(initialScores);
    
    // Obtener comentarios de las calificaciones iniciales
    const initialComments = {};
    Object.keys(initialScores).forEach(paramId => {
      if (initialScores[paramId]?.comments) {
        initialComments[paramId] = initialScores[paramId].comments;
      }
    });
    setComments(initialComments);
    
    // Calcular resultados iniciales
    const initialResults = {};
    Object.keys(initialScores).forEach(paramId => {
      const parameter = parameters.find(p => p.id === paramId);
      if (parameter) {
        try {
          initialResults[paramId] = calculateParameterScore(
            initialScores[paramId],
            parameter.coefficient
          );
        } catch (error) {
          console.error('Error al calcular resultado:', error);
          initialResults[paramId] = 0;
        }
      }
    });
    
    setResults(initialResults);
    setHasChanges(false);
  }, [initialScores, parameters]);
  
  // Manejar cambio en calificación
  const handleScoreChange = (paramId, value) => {
    // Validar que sea un número entre 0 y 10
    const numValue = parseFloat(value);
    if (isNaN(numValue) || numValue < 0 || numValue > 10) {
      return;
    }
    
    // Actualizar calificaciones
    const newScores = {
      ...scores,
      [paramId]: numValue
    };
    setScores(newScores);
    
    // Calcular resultado
    const parameter = parameters.find(p => p.id === paramId);
    if (parameter) {
      try {
        const result = calculateParameterScore(numValue, parameter.coefficient);
        setResults({
          ...results,
          [paramId]: result
        });
      } catch (error) {
        console.error('Error al calcular resultado:', error);
      }
    }
    
    setHasChanges(true);
  };
  
  // Manejar cambio en comentarios
  const handleCommentChange = (paramId, value) => {
    setComments({
      ...comments,
      [paramId]: value
    });
    setHasChanges(true);
  };
  
  // Guardar calificaciones
  const handleSave = () => {
    // Preparar datos para guardar
    const scoreData = {};
    
    parameters.forEach(param => {
      if (scores[param.id] !== undefined) {
        scoreData[param.id] = {
          value: scores[param.id],
          comments: comments[param.id] || '',
        };
      }
    });
    
    // Añadir motivo de edición si existe
    if (editReason) {
      scoreData.editReason = editReason;
    }
    
    onSave(scoreData);
    setHasChanges(false);
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
  
  return (
    <ScoreCardContainer>
      <RiderHeader>
        <RiderName>{rider.firstName} {rider.lastName}</RiderName>
        <HorseInfo>
          Caballo: <strong>{horse.name}</strong> | Categoría: {horse.category}
        </HorseInfo>
      </RiderHeader>
      
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
      {Object.keys(initialScores).length > 0 && (
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
          {isOffline ? 'Guardar Localmente' : 'Guardar Calificación'}
        </Button>
      </ActionButtons>
    </ScoreCardContainer>
  );
};

export default ScoreCard;