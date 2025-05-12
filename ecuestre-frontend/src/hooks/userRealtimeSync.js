import { useState, useEffect, useCallback } from 'react';
import { 
  subscribeToRankings, 
  subscribeToScores,
  checkOnlineStatus 
} from '../services/firebase';
import { 
  scoreWebSocket, 
  rankingWebSocket 
} from '../services/websocket';

/**
 * Hook para gestionar la sincronización en tiempo real de datos
 * Combina Firebase y WebSockets para mayor robustez
 */
export const useRealtimeSync = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isFirebaseConnected, setIsFirebaseConnected] = useState(false);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const [syncMethod, setSyncMethod] = useState('unavailable');

  // Verificar estado de conexión general
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Verificar conexión con Firebase
    const unsubscribeFirebase = checkOnlineStatus((connected) => {
      setIsFirebaseConnected(connected);
      updateSyncMethod(connected, isWebSocketConnected);
    });
    
    // Manejar eventos WebSocket
    scoreWebSocket.onOpen(() => {
      setIsWebSocketConnected(true);
      updateSyncMethod(isFirebaseConnected, true);
    });
    
    scoreWebSocket.onClose(() => {
      setIsWebSocketConnected(false);
      updateSyncMethod(isFirebaseConnected, false);
    });
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      unsubscribeFirebase();
    };
  }, [isFirebaseConnected, isWebSocketConnected]);
  
  // Función auxiliar para determinar el método de sincronización
  const updateSyncMethod = useCallback((firebaseConnected, websocketConnected) => {
    if (firebaseConnected && websocketConnected) {
      setSyncMethod('both'); // Ambos disponibles, preferible
    } else if (firebaseConnected) {
      setSyncMethod('firebase');
    } else if (websocketConnected) {
      setSyncMethod('websocket');
    } else {
      setSyncMethod('unavailable');
    }
  }, []);

  // Función para suscribirse a rankings
  const subscribeToRealtimeRankings = useCallback((competitionId, callback) => {
    // Preparar callbacks
    const processRankingsData = (data) => {
      if (!data) return;
      
      // Convertir a formato común
      const rankings = Object.entries(data).map(([participantId, rankingData]) => ({
        participantId: parseInt(participantId),
        ...rankingData
      }));
      
      // Ordenar por posición
      rankings.sort((a, b) => a.position - b.position);
      
      callback(rankings);
    };
    
    // Suscribirse a ambos métodos para redundancia
    const firebaseUnsubscribe = subscribeToRankings(competitionId, processRankingsData);
    
    // Conectar WebSocket
    rankingWebSocket.connectToRankings(competitionId);
    const websocketUnsubscribe = rankingWebSocket.onCurrentRankings(
      (data) => callback(data.rankings)
    );
    
    // Solicitar rankings actuales vía WebSocket
    rankingWebSocket.requestRankings();
    
    // Devolver función de limpieza
    return () => {
      firebaseUnsubscribe();
      websocketUnsubscribe();
      rankingWebSocket.disconnect();
    };
  }, []);

  // Función para suscribirse a calificaciones
  const subscribeToRealtimeScores = useCallback((competitionId, participantId, callback) => {
    // Suscribirse a Firebase
    const firebaseUnsubscribe = subscribeToScores(competitionId, participantId, callback);
    
    // Conectar WebSocket
    scoreWebSocket.connectToScores(competitionId, participantId);
    const websocketUnsubscribe = scoreWebSocket.onCurrentScores(
      (data) => callback(data.scores)
    );
    
    // Solicitar calificaciones actuales vía WebSocket
    scoreWebSocket.requestScores();
    
    // Devolver función de limpieza
    return () => {
      firebaseUnsubscribe();
      websocketUnsubscribe();
      scoreWebSocket.disconnect();
    };
  }, []);

  // Función para enviar actualizaciones de calificaciones
  const sendScoreUpdate = useCallback((competitionId, participantId, judgeId, scoreData) => {
    // Intentar enviar por WebSocket
    if (isWebSocketConnected) {
      scoreWebSocket.updateScore({
        competition_id: competitionId,
        participant_id: participantId,
        judge_id: judgeId,
        ...scoreData
      });
    }
    
    // Respaldar con API REST si WebSocket no está disponible
    if (!isWebSocketConnected || syncMethod === 'both') {
      import('../services/api').then(({ submitScore }) => {
        submitScore(competitionId, participantId, {
          judge_id: judgeId,
          scores: scoreData
        });
      });
    }
  }, [isWebSocketConnected, syncMethod]);
  
  return {
    isOnline,
    isFirebaseConnected,
    isWebSocketConnected,
    syncMethod,
    subscribeToRealtimeRankings,
    subscribeToRealtimeScores,
    sendScoreUpdate
  };
};