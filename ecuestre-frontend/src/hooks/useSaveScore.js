// src/hooks/useSaveScore.js

import { useState, useCallback } from 'react';
import useOffline from './useOffline';
import { updateScore as updateFirebaseScore } from '../services/firebase';
import { scoreWebSocket } from '../services/websockets';

/**
 * Hook para gestionar el guardado de calificaciones (online u offline)
 * con soporte para múltiples métodos de sincronización
 */
const useSaveScore = (competitionId, participantId, judgeId) => {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [lastSaveStatus, setLastSaveStatus] = useState('');
  const { isOnline, saveScore: saveOffline, forceSyncPendingActions } = useOffline();

  /**
   * Guarda la calificación usando el mejor método disponible
   * @param {Object} scoreData - Datos de la calificación
   * @returns {Promise<Object>} - Resultado de la operación
   */
  const saveScore = useCallback(async (scoreData) => {
    setIsSaving(true);
    setSaveError(null);
    
    try {
      // Preparar datos para la API
      const apiScoreData = {
        judge_id: judgeId,
        scores: Object.entries(scoreData).map(([paramId, data]) => {
          if (paramId === 'editReason') return null;
          return {
            parameter_id: parseInt(paramId),
            value: data.value,
            comments: data.comments || ''
          };
        }).filter(Boolean)
      };
      
      // Guardar usando la API REST
      if (isOnline) {
        // Importar dinámicamente para evitar ciclos de dependencia
        const { submitScore } = await import('../services/api');
        await submitScore(competitionId, participantId, apiScoreData);
        
        // Si tiene éxito, actualizar también Firebase
        const firebaseData = {};
        Object.entries(scoreData).forEach(([paramId, data]) => {
          if (paramId !== 'editReason') {
            firebaseData[paramId] = {
              value: data.value,
              comments: data.comments || ''
            };
          }
        });
        
        try {
          // Actualizar en Firebase
          updateFirebaseScore(competitionId, participantId, judgeId, firebaseData);
          
          // Enviar por WebSocket si está disponible
          try {
            scoreWebSocket.updateScore({
              type: 'score_update',
              judge_id: judgeId,
              parameters: firebaseData
            });
          } catch (wsError) {
            console.warn('Error al enviar por WebSocket:', wsError);
          }
        } catch (syncError) {
          console.warn('Error al sincronizar con servicios en tiempo real:', syncError);
        }
        
        setLastSaveStatus('saved');
        return { success: true, status: 'saved' };
      } else {
        // Guardar offline
        const result = await saveOffline(
          parseInt(competitionId),
          parseInt(participantId),
          judgeId,
          scoreData
        );
        
        setLastSaveStatus('offline');
        return { success: true, status: 'offline' };
      }
    } catch (error) {
      console.error('Error al guardar calificación:', error);
      setSaveError(error.message || 'Error al guardar');
      setLastSaveStatus('error');
      return { success: false, error };
    } finally {
      setIsSaving(false);
    }
  }, [competitionId, participantId, judgeId, isOnline, saveOffline]);

  /**
   * Fuerza la sincronización de datos pendientes
   */
  const syncPendingScores = useCallback(() => {
    if (!isOnline) {
      return { success: false, error: 'No hay conexión a Internet' };
    }
    
    return forceSyncPendingActions();
  }, [isOnline, forceSyncPendingActions]);

  return {
    saveScore,
    syncPendingScores,
    isSaving,
    saveError,
    lastSaveStatus
  };
};

export default useSaveScore;