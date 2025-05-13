// src/components/judging/RealtimeScoreCard.jsx
import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { calculateParameterScore } from '../../utils/calculations';
import Button from '../common/Button';
import { useRealtimeSync } from '../../hooks/useRealtimeSync';
import useSaveScore from '../../hooks/useSaveScore';
import ScoreCard from './ScoreCard';

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
 * @param {Function} props.onScoreUpdated - Callback para notificar actualizaciones
 */
const RealtimeScoreCard = ({
  rider,
  horse,
  parameters,
  competitionId,
  participantId,
  judgeId,
  onScoreUpdated
}) => {
  // Estado para almacenar las calificaciones
  const [scores, setScores] = useState({});
  
  // Usar el hook de sincronización en tiempo real
  const { 
    isOnline, 
    syncMethod,
    subscribeToRealtimeScores
  } = useRealtimeSync();
  
  // Usar el hook para guardar calificaciones
  const {
    saveScore,
    syncPendingScores,
    isSaving,
    lastSaveStatus
  } = useSaveScore(competitionId, participantId, judgeId);
  
  // Suscribirse a actualizaciones de calificaciones
  useEffect(() => {
    if (!competitionId || !participantId || !judgeId) return () => {};
    
    const handleScoresUpdate = (data) => {
      if (!data) {
        console.warn('Datos de calificaciones inválidos');
        return;
      }
      
      // Procesar las calificaciones del juez actual
      const judgeData = data[judgeId];
      if (!judgeData || !judgeData.parameters) return;
      
      const paramScores = {};
      
      // Procesar cada parámetro
      Object.entries(judgeData.parameters).forEach(([paramId, scoreData]) => {
        paramScores[paramId] = scoreData.value;
      });
      
      setScores(paramScores);
      
      // Notificar actualización
      if (onScoreUpdated) {
        onScoreUpdated(paramScores);
      }
    };
    
    // Suscribirse a sincronización en tiempo real
    const unsubscribe = subscribeToRealtimeScores(
      competitionId, 
      participantId, 
      handleScoresUpdate
    );
    
    return unsubscribe;
  }, [competitionId, participantId, judgeId, subscribeToRealtimeScores, onScoreUpdated]);
  
  // Manejar guardado de calificaciones
  const handleSaveScores = useCallback(async (scoreData) => {
    try {
      await saveScore(scoreData);
      
      // Notificar actualización
      if (onScoreUpdated) {
        const paramScores = {};
        Object.entries(scoreData).forEach(([paramId, data]) => {
          if (paramId !== 'editReason') {
            paramScores[paramId] = data.value;
          }
        });
        
        onScoreUpdated(paramScores);
      }
    } catch (error) {
      console.error('Error al guardar calificaciones:', error);
    }
  }, [saveScore, onScoreUpdated]);
  
  return (
    <div>
      <ScoreCard
        rider={rider}
        horse={horse}
        parameters={parameters}
        initialScores={scores}
        onSave={handleSaveScores}
        isOffline={!isOnline}
        savedStatus={isSaving ? 'pending' : lastSaveStatus}
        syncMethod={syncMethod}
        onScoreUpdated={onScoreUpdated}
      />
      
      {!isOnline && (
        <OfflineIndicator>
          Modo Offline - Los cambios se sincronizarán cuando vuelva la conexión
        </OfflineIndicator>
      )}
      
      {isOnline && (
        <SyncButton
          variant="outline"
          onClick={syncPendingScores}
        >
          Sincronizar Datos Pendientes
        </SyncButton>
      )}
    </div>
  );
};

// Estilos
const OfflineIndicator = styled.div`
  background-color: ${props => props.theme.colors.warning};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.small};
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const SyncButton = styled(Button)`
  width: 100%;
  margin-top: ${props => props.theme.spacing.md};
`;

export default RealtimeScoreCard;