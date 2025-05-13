// src/services/offline.js
// Servicio para gestionar la funcionalidad offline

// Abrir IndexedDB
const openDatabase = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('EcuestreOfflineDB', 1);
    
    request.onerror = (event) => {
      console.error('Error al abrir la base de datos:', event.target.error);
      reject(event.target.error);
    };
    
    request.onsuccess = (event) => {
      const db = event.target.result;
      resolve(db);
    };
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // Crear almacén para calificaciones pendientes
      if (!db.objectStoreNames.contains('pendingScores')) {
        const store = db.createObjectStore('pendingScores', { keyPath: 'id', autoIncrement: true });
        store.createIndex('competition', 'competitionId', { unique: false });
        store.createIndex('participant', 'participantId', { unique: false });
      }
      
      // Crear almacén para datos de competencia
      if (!db.objectStoreNames.contains('competitions')) {
        db.createObjectStore('competitions', { keyPath: 'id' });
      }
      
      // Crear almacén para datos de participantes
      if (!db.objectStoreNames.contains('participants')) {
        const store = db.createObjectStore('participants', { keyPath: 'id' });
        store.createIndex('competition', 'competitionId', { unique: false });
      }
    };
  });
};

// Guardar calificación offline
export const saveScoreOffline = async (competitionId, participantId, judgeId, scoreData) => {
  try {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['pendingScores'], 'readwrite');
      const store = transaction.objectStore('pendingScores');
      
      const pendingScore = {
        competitionId,
        participantId,
        judgeId,
        scoreData,
        timestamp: new Date().toISOString(),
      };
      
      const request = store.add(pendingScore);
      
      request.onsuccess = () => {
        resolve(pendingScore);
      };
      
      request.onerror = (event) => {
        console.error('Error al guardar calificación offline:', event.target.error);
        reject(event.target.error);
      };
    });
  } catch (error) {
    console.error('Error en saveScoreOffline:', error);
    throw error;
  }
};

// Obtener calificaciones pendientes
export const getPendingScores = async () => {
  try {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['pendingScores'], 'readonly');
      const store = transaction.objectStore('pendingScores');
      const request = store.getAll();
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = (event) => {
        console.error('Error al obtener calificaciones pendientes:', event.target.error);
        reject(event.target.error);
      };
    });
  } catch (error) {
    console.error('Error en getPendingScores:', error);
    throw error;
  }
};

// Eliminar calificación pendiente
export const removePendingScore = async (id) => {
  try {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['pendingScores'], 'readwrite');
      const store = transaction.objectStore('pendingScores');
      const request = store.delete(id);
      
      request.onsuccess = () => {
        resolve(true);
      };
      
      request.onerror = (event) => {
        console.error('Error al eliminar calificación pendiente:', event.target.error);
        reject(event.target.error);
      };
    });
  } catch (error) {
    console.error('Error en removePendingScore:', error);
    throw error;
  }
};

// Guardar datos de competencia para uso offline
export const saveCompetitionData = async (competition) => {
  try {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['competitions'], 'readwrite');
      const store = transaction.objectStore('competitions');
      const request = store.put(competition);
      
      request.onsuccess = () => {
        resolve(competition);
      };
      
      request.onerror = (event) => {
        console.error('Error al guardar datos de competencia:', event.target.error);
        reject(event.target.error);
      };
    });
  } catch (error) {
    console.error('Error en saveCompetitionData:', error);
    throw error;
  }
};

// Obtener datos de competencia guardados offline
export const getOfflineCompetition = async (competitionId) => {
  try {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['competitions'], 'readonly');
      const store = transaction.objectStore('competitions');
      const request = store.get(competitionId);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = (event) => {
        console.error('Error al obtener datos de competencia offline:', event.target.error);
        reject(event.target.error);
      };
    });
  } catch (error) {
    console.error('Error en getOfflineCompetition:', error);
    throw error;
  }
};

// Obtener todas las competencias guardadas offline
export const getOfflineCompetitions = async () => {
  try {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['competitions'], 'readonly');
      const store = transaction.objectStore('competitions');
      const request = store.getAll();
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = (event) => {
        console.error('Error al obtener competencias offline:', event.target.error);
        reject(event.target.error);
      };
    });
  } catch (error) {
    console.error('Error en getOfflineCompetitions:', error);
    throw error;
  }
};



// Guardar datos de participantes para uso offline
export const saveParticipantsData = async (participants) => {
  try {
    const db = await openDatabase();
    const transaction = db.transaction(['participants'], 'readwrite');
    const store = transaction.objectStore('participants');
    
    // Procesar cada participante
    for (const participant of participants) {
      await new Promise((resolve, reject) => {
        const request = store.put(participant);
        
        request.onsuccess = () => {
          resolve();
        };
        
        request.onerror = (event) => {
          console.error('Error al guardar participante:', event.target.error);
          reject(event.target.error);
        };
      });
    }
    
    return true;
  } catch (error) {
    console.error('Error en saveParticipantsData:', error);
    throw error;
  }
};

// Obtener participantes de una competencia guardados offline
export const getOfflineParticipants = async (competitionId) => {
  try {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['participants'], 'readonly');
      const store = transaction.objectStore('participants');
      const index = store.index('competition');
      const request = index.getAll(competitionId);
      
      request.onsuccess = () => {
        resolve(request.result);
      };
      
      request.onerror = (event) => {
        console.error('Error al obtener participantes offline:', event.target.error);
        reject(event.target.error);
      };
    });
  } catch (error) {
    console.error('Error en getOfflineParticipants:', error);
    throw error;
  }
};


export default {
  saveScoreOffline,
  getPendingScores,
  removePendingScore,
  saveCompetitionData,
  getOfflineCompetition,
  saveParticipantsData,
  getOfflineParticipants,
  getOfflineCompetitions
};