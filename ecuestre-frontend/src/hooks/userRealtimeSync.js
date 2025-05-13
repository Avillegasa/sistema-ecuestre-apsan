// Simplificar src/hooks/useRealtimeSync.js a una versión básica que solo use Firebase
import { useState, useEffect, useCallback } from 'react';
import { 
  subscribeToRankings, 
  subscribeToScores,
  checkOnlineStatus 
} from '../services/firebase';

export const useRealtimeSync = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isFirebaseConnected, setIsFirebaseConnected] = useState(false);
  const [syncMethod, setSyncMethod] = useState('firebase');

  // Verificar estado de conexión general
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Verificar conexión con Firebase
    const unsubscribeFirebase = checkOnlineStatus((connected) => {
      setIsFirebaseConnected(connected);
      setSyncMethod(connected ? 'firebase' : 'unavailable');
    });
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      unsubscribeFirebase();
    };
  }, []);

  // Función para suscribirse a rankings
  const subscribeToRealtimeRankings = useCallback((competitionId, callback) => {
    return subscribeToRankings(competitionId, callback);
  }, []);

  // Función para suscribirse a calificaciones
  const subscribeToRealtimeScores = useCallback((competitionId, participantId, callback) => {
    return subscribeToScores(competitionId, participantId, callback);
  }, []);

  // Función para enviar actualizaciones de calificaciones
  const sendScoreUpdate = useCallback((competitionId, participantId, judgeId, scoreData) => {
    // Importar dinámicamente para evitar ciclos de dependencia
    import('../services/api').then(({ submitScore }) => {
      submitScore(competitionId, participantId, {
        judge_id: judgeId,
        scores: scoreData
      });
    });
  }, []);
  
  return {
    isOnline,
    isFirebaseConnected,
    isWebSocketConnected: false,
    syncMethod,
    subscribeToRealtimeRankings,
    subscribeToRealtimeScores,
    sendScoreUpdate
  };
};