// src/hooks/useOffline.js - versión mejorada

import { useState, useEffect, useCallback } from 'react';
import { getPendingScores, removePendingScore, saveScoreOffline } from '../services/offline';
import { submitScore } from '../services/api';

/**
 * Hook personalizado mejorado para gestionar la funcionalidad offline
 * Proporciona funciones para guardar datos offline y sincronizar cuando vuelva la conexión
 */
const useOffline = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingActions, setPendingActions] = useState([]);
  const [syncInProgress, setSyncInProgress] = useState(false);
  const [lastConnectionTime, setLastConnectionTime] = useState(
    isOnline ? new Date() : null
  );
  
  // Verificar estado de conexión a internet
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setLastConnectionTime(new Date());
    };
    
    const handleOffline = () => {
      setIsOnline(false);
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // También verificar conexión mediante ping periódico
    const checkConnectionInterval = setInterval(() => {
      fetch('/ping.json', { method: 'GET', cache: 'no-store' })
        .then(() => {
          if (!isOnline) {
            setIsOnline(true);
            setLastConnectionTime(new Date());
          }
        })
        .catch(() => {
          if (isOnline) {
            setIsOnline(false);
          }
        });
    }, 30000); // Verificar cada 30 segundos
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(checkConnectionInterval);
    };
  }, [isOnline]);
  
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
        // Si está online, enviar directamente
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
      // Importar dinámicamente para evitar ciclos
      const apiModule = await import('../services/api');
      const submitScore = apiModule.submitScore;
      
      // Procesar cada acción pendiente
      const results = [];
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
          results.push({ id: action.id, success: true });
        } catch (error) {
          console.error('Error al sincronizar acción:', error);
          results.push({ id: action.id, success: false, error });
          // Continuar con la siguiente acción
        }
      }
      
      // Actualizar lista de acciones pendientes
      const scores = await getPendingScores();
      setPendingActions(scores);
      
      return results;
    } catch (error) {
      console.error('Error en sincronización:', error);
      return { success: false, error };
    } finally {
      setSyncInProgress(false);
    }
  }, [pendingActions, isOnline]);
  
  // Forzar sincronización manual
  const forceSyncPendingActions = () => {
    if (isOnline && !syncInProgress) {
      return syncPendingActions();
    }
    return Promise.resolve({ success: false, error: 'No hay conexión o ya hay una sincronización en progreso' });
  };
  
  // Obtener tiempo desde la última conexión
  const getTimeSinceLastConnection = () => {
    if (!lastConnectionTime) return null;
    
    const now = new Date();
    const diffMs = now - lastConnectionTime;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins} minuto${diffMins !== 1 ? 's' : ''}`;
    } else {
      const diffHours = Math.floor(diffMins / 60);
      return `${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
    }
  };
  
  return {
    isOnline,
    pendingActions,
    syncInProgress,
    saveScore,
    forceSyncPendingActions,
    getTimeSinceLastConnection,
    lastConnectionTime
  };
};

export default useOffline;