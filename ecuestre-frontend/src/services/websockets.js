/**
 * Servicio de WebSocket para comunicación en tiempo real
 */

// Determinar el host de WebSocket según el entorno
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHost = process.env.NODE_ENV === 'production'
  ? `${wsProtocol}//${window.location.host}`
  : 'ws://localhost:8000';

/**
 * Clase para gestionar conexiones WebSocket
 */
class WebSocketService {
  constructor() {
    this.socket = null;
    this.callbacks = {
      onOpen: [],
      onClose: [],
      onError: [],
      onMessage: [],
      onSpecificMessage: {}  // Organizados por tipo de mensaje
    };
    this.reconnectTimer = null;
    this.reconnectInterval = 3000;  // 3 segundos entre intentos
    this.maxReconnectAttempts = 5;
    this.reconnectAttempts = 0;
    this.url = '';
  }

  /**
   * Conecta a un WebSocket
   * @param {string} url - URL del WebSocket
   */
  connect(url) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket ya está conectado');
      return;
    }
    
    this.url = url;
    const fullUrl = `${wsHost}${url}`;
    
    try {
      this.socket = new WebSocket(fullUrl);
      
      this.socket.onopen = (event) => {
        console.log('WebSocket conectado:', fullUrl);
        this.reconnectAttempts = 0;
        this.callbacks.onOpen.forEach(callback => callback(event));
      };
      
      this.socket.onclose = (event) => {
        console.log('WebSocket desconectado, código:', event.code);
        this.callbacks.onClose.forEach(callback => callback(event));
        
        // Intentar reconectar automáticamente
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectTimer = setTimeout(() => {
            this.reconnectAttempts++;
            console.log(`Intentando reconectar (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            this.connect(this.url);
          }, this.reconnectInterval);
        }
      };
      
      this.socket.onerror = (error) => {
        console.error('Error en WebSocket:', error);
        this.callbacks.onError.forEach(callback => callback(error));
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Notificar a todos los callbacks generales
          this.callbacks.onMessage.forEach(callback => callback(data));
          
          // Notificar a callbacks específicos por tipo de mensaje
          const messageType = data.type;
          if (messageType && this.callbacks.onSpecificMessage[messageType]) {
            this.callbacks.onSpecificMessage[messageType].forEach(
              callback => callback(data)
            );
          }
        } catch (error) {
          console.error('Error al procesar mensaje WebSocket:', error);
        }
      };
    } catch (error) {
      console.error('Error al crear WebSocket:', error);
    }
  }

  /**
   * Desconecta el WebSocket
   */
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  /**
   * Envía un mensaje al servidor
   * @param {Object} data - Datos a enviar
   */
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
    } else {
      console.warn('No se puede enviar mensaje: WebSocket no está conectado');
    }
  }

  /**
   * Registra un callback para eventos de apertura de conexión
   * @param {Function} callback - Función a llamar
   */
  onOpen(callback) {
    this.callbacks.onOpen.push(callback);
  }

  /**
   * Registra un callback para eventos de cierre de conexión
   * @param {Function} callback - Función a llamar
   */
  onClose(callback) {
    this.callbacks.onClose.push(callback);
  }

  /**
   * Registra un callback para eventos de error
   * @param {Function} callback - Función a llamar
   */
  onError(callback) {
    this.callbacks.onError.push(callback);
  }

  /**
   * Registra un callback para todos los mensajes
   * @param {Function} callback - Función a llamar con los datos
   */
  onMessage(callback) {
    this.callbacks.onMessage.push(callback);
  }

  /**
   * Registra un callback para un tipo específico de mensaje
   * @param {string} messageType - Tipo de mensaje a escuchar
   * @param {Function} callback - Función a llamar con los datos
   */
  onMessageType(messageType, callback) {
    if (!this.callbacks.onSpecificMessage[messageType]) {
      this.callbacks.onSpecificMessage[messageType] = [];
    }
    
    this.callbacks.onSpecificMessage[messageType].push(callback);
    
    // Devolver función para cancelar la suscripción
    return () => {
      this.callbacks.onSpecificMessage[messageType] = 
        this.callbacks.onSpecificMessage[messageType].filter(cb => cb !== callback);
    };
  }
}

// Servicios específicos para los diferentes tipos de WebSockets

/**
 * Servicio para WebSocket de calificaciones
 */
export class ScoreWebSocketService extends WebSocketService {
  /**
   * Conecta al WebSocket de calificaciones
   * @param {number} competitionId - ID de la competencia
   * @param {number} participantId - ID del participante
   */
  connectToScores(competitionId, participantId) {
    this.connect(`/ws/scores/${competitionId}/${participantId}/`);
  }
  
  /**
   * Solicita las calificaciones actuales
   */
  requestScores() {
    this.send({
      type: 'request_scores'
    });
  }
  
  /**
   * Envía una actualización de calificación
   * @param {Object} scoreData - Datos de la calificación
   */
  updateScore(scoreData) {
    this.send({
      type: 'score_update',
      ...scoreData
    });
  }
  
  /**
   * Registra un callback para actualizaciones de calificaciones
   * @param {Function} callback - Función a llamar con los datos
   */
  onScoreUpdate(callback) {
    return this.onMessageType('score_update', callback);
  }
  
  /**
   * Registra un callback para recibir todas las calificaciones actuales
   * @param {Function} callback - Función a llamar con los datos
   */
  onCurrentScores(callback) {
    return this.onMessageType('current_scores', callback);
  }
}

/**
 * Servicio para WebSocket de rankings
 */
export class RankingWebSocketService extends WebSocketService {
  /**
   * Conecta al WebSocket de rankings
   * @param {number} competitionId - ID de la competencia
   */
  connectToRankings(competitionId) {
    this.connect(`/ws/rankings/${competitionId}/`);
  }
  
  /**
   * Solicita los rankings actuales
   */
  requestRankings() {
    this.send({
      type: 'request_rankings'
    });
  }
  
  /**
   * Registra un callback para actualizaciones de rankings
   * @param {Function} callback - Función a llamar con los datos
   */
  onRankingsUpdate(callback) {
    return this.onMessageType('rankings_update', callback);
  }
  
  /**
   * Registra un callback para recibir todos los rankings actuales
   * @param {Function} callback - Función a llamar con los datos
   */
  onCurrentRankings(callback) {
    return this.onMessageType('current_rankings', callback);
  }
}

// Instancias singleton para uso en toda la aplicación
export const scoreWebSocket = new ScoreWebSocketService();
export const rankingWebSocket = new RankingWebSocketService();

export default {
  scoreWebSocket,
  rankingWebSocket
};