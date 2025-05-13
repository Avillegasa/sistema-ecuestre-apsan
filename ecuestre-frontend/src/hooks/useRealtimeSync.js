// src/hooks/useRealtimeSync.js
import { useState, useEffect, useCallback } from 'react';
import { 
  subscribeToRankings, 
  subscribeToScores,
  updateScore as updateFirebaseScore,
  checkOnlineStatus 
} from '../services/firebase';
import { scoreWebSocket, rankingWebSocket } from '../services/websockets';

/**
 * Hook personalizado para sincronización en tiempo real
 * Combina Firebase y WebSockets para máxima robustez
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
    
    // Verificar conexión WebSocket
    const handleWebSocketOpen = () => {
      setIsWebSocketConnected(true);
      updateSyncMethod(isFirebaseConnected, true);
    };
    
    const handleWebSocketClose = () => {
      setIsWebSocketConnected(false);
      updateSyncMethod(isFirebaseConnected, false);
    };
    
    scoreWebSocket.onOpen(handleWebSocketOpen);
    scoreWebSocket.onClose(handleWebSocketClose);
    rankingWebSocket.onOpen(handleWebSocketOpen);
    rankingWebSocket.onClose(handleWebSocketClose);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      unsubscribeFirebase();
      
      // No necesitamos desuscribirnos de eventos WebSocket ya que
      // estos controladores son locales al scoreWebSocket/rankingWebSocket
    };
  }, [isFirebaseConnected, isWebSocketConnected]);
  
  // Función auxiliar para actualizar el método de sincronización
  const updateSyncMethod = (firebase, websocket) => {
    if (firebase && websocket) {
      setSyncMethod('both');
    } else if (firebase) {
      setSyncMethod('firebase');
    } else if (websocket) {
      setSyncMethod('websocket');
    } else {
      setSyncMethod('unavailable');
    }
  };

  // Función para suscribirse a rankings
  const subscribeToRealtimeRankings = useCallback((competitionId, callback) => {
    // Intentar WebSocket primero
    try {
      rankingWebSocket.connectToRankings(competitionId);
      rankingWebSocket.requestRankings();
      
      const wsCallback = rankingWebSocket.onRankingsUpdate(callback);
      
      // También suscribirse a Firebase como respaldo
      const firebaseCallback = subscribeToRankings(competitionId, callback);
      
      // Devolver función para desuscribirse de ambos
      return () => {
        if (wsCallback && typeof wsCallback === 'function') {
          wsCallback();
        }
        rankingWebSocket.disconnect();
        
        if (firebaseCallback && typeof firebaseCallback === 'function') {
          firebaseCallback();
        }
      };
    } catch (wsError) {
      console.warn('Error al conectar WebSocket para rankings:', wsError);
      // Si falla WebSocket, usar solo Firebase
      return subscribeToRankings(competitionId, callback);
    }
  }, []);

  // Función para suscribirse a calificaciones
  const subscribeToRealtimeScores = useCallback((competitionId, participantId, callback) => {
    // Intentar WebSocket primero
    try {
      scoreWebSocket.connectToScores(competitionId, participantId);
      scoreWebSocket.requestScores();
      
      const wsCallback = scoreWebSocket.onScoreUpdate(callback);
      
      // También suscribirse a Firebase como respaldo
      const firebaseCallback = subscribeToScores(competitionId, participantId, callback);
      
      // Devolver función para desuscribirse de ambos
      return () => {
        if (wsCallback && typeof wsCallback === 'function') {
          wsCallback();
        }
        scoreWebSocket.disconnect();
        
        if (firebaseCallback && typeof firebaseCallback === 'function') {
          firebaseCallback();
        }
      };
    } catch (wsError) {
      console.warn('Error al conectar WebSocket para scores:', wsError);
      // Si falla WebSocket, usar solo Firebase
      return subscribeToScores(competitionId, participantId, callback);
    }
  }, []);

  // Función para enviar actualizaciones de calificaciones
  const sendScoreUpdate = useCallback((competitionId, participantId, judgeId, scoreData) => {
    // Intentar enviar a través de la API REST
    import('../services/api').then(({ submitScore }) => {
      submitScore(competitionId, participantId, {
        judge_id: judgeId,
        scores: Object.entries(scoreData).map(([paramId, data]) => ({
          parameter_id: parseInt(paramId),
          value: data.value,
          comments: data.comments || ''
        }))
      })
      .then(() => {
        // Si la API REST tiene éxito, también actualizar Firebase y WebSocket
        // para asegurar que todos los clientes estén sincronizados
        
        // Actualizar Firebase
        const firebaseData = {};
        Object.entries(scoreData).forEach(([paramId, data]) => {
          firebaseData[paramId] = {
            value: data.value,
            comments: data.comments || ''
          };
        });
        
        updateFirebaseScore(competitionId, participantId, judgeId, firebaseData);
        
        // Actualizar WebSocket
        if (isWebSocketConnected) {
          scoreWebSocket.updateScore({
            type: 'score_update',
            judge_id: judgeId,
            ...scoreData
          });
        }
      })
      .catch(error => {
        console.error('Error al enviar calificación:', error);
        // Si falla la API REST, intentar guardar offline
        import('./useOffline').then(module => {
          const saveScoreOffline = module.saveScoreOffline;
          saveScoreOffline(competitionId, participantId, judgeId, scoreData);
        });
      });
    });
  }, [isWebSocketConnected]);
  
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

export default useRealtimeSync;