// src/hooks/useOffline.js
import { useState, useEffect, useCallback } from 'react';
import { getPendingScores, removePendingScore, saveScoreOffline } from '../services/offline';
import { submitScore } from '../services/api';

/**
 * Hook personalizado para gestionar la funcionalidad offline
 * Proporciona funciones para guardar datos offline y sincronizar cuando vuelva la conexión
 */
const useOffline = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingActions, setPendingActions] = useState([]);
  const [syncInProgress, setSyncInProgress] = useState(false);
  
  // Verificar estado de conexión a internet
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  // Cargar acciones pendientes al iniciar
  useEffect(() => {
    const loadPendingActions = async () => {
      try {
        const scores = await getPendingScores();
        setPendingActions(scores);
      } catch (error) {
        console.error('Error al cargar acciones pendientes:', error);
      }
    };
    
    loadPendingActions();
  }, []);
  
  // Sincronizar cuando vuelve a estar online
  useEffect(() => {
    if (isOnline && pendingActions.length > 0 && !syncInProgress) {
      syncPendingActions();
    }
  }, [isOnline, pendingActions]);
  
  // Función para guardar una calificación (con soporte offline)
  const saveScore = async (competitionId, participantId, judgeId, scoreData) => {
    try {
      if (isOnline) {
         // Si está online, importar dinámicamente la API para evitar dependencia circular
        const apiModule = await import('../services/api');
        const submitScore = apiModule.submitScore;
        
        await submitScore(competitionId, participantId, {
          judge_id: judgeId,
          scores: scoreData
        });
        return { success: true, offline: false };
      } else {
        // Si está offline, guardar localmente
        await saveScoreOffline(competitionId, participantId, judgeId, scoreData);
        // Actualizar lista de acciones pendientes
        const scores = await getPendingScores();
        setPendingActions(scores);
        return { success: true, offline: true };
      }
    } catch (error) {
      console.error('Error al guardar calificación:', error);
      return { success: false, error };
    }
  };
  
  // Función para sincronizar acciones pendientes
  const syncPendingActions = useCallback(async () => {
    if (pendingActions.length === 0 || !isOnline) return;
    
    setSyncInProgress(true);
    
    try {
      // Procesar cada acción pendiente
      for (const action of pendingActions) {
        try {
          // Intentar enviar al servidor
          await submitScore(
            action.competitionId, 
            action.participantId, 
            {
              judge_id: action.judgeId,
              scores: action.scoreData
            }
          );
          
          // Si se envió correctamente, eliminar de pendientes
          await removePendingScore(action.id);
        } catch (error) {
          console.error('Error al sincronizar acción:', error);
          // Continuar con la siguiente acción
        }
      }
      
      // Actualizar lista de acciones pendientes
      const scores = await getPendingScores();
      setPendingActions(scores);
    } catch (error) {
      console.error('Error en sincronización:', error);
    } finally {
      setSyncInProgress(false);
    }
  }, [pendingActions, isOnline]);
  
  // Forzar sincronización manual
  const forceSyncPendingActions = () => {
    if (isOnline && !syncInProgress) {
      syncPendingActions();
    }
  };
  
  return {
    isOnline,
    pendingActions,
    syncInProgress,
    saveScore,
    forceSyncPendingActions
  };
};

export default useOffline;