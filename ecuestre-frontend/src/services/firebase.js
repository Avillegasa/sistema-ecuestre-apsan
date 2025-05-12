import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue, set, update, off } from 'firebase/database';

// Configuración de Firebase
// NOTA: Estas claves son públicas y están diseñadas para ser visibles en el cliente
// Las reglas de seguridad en Firebase controlan el acceso
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  databaseURL: process.env.REACT_APP_FIREBASE_DATABASE_URL,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// Función para suscribirse a actualizaciones de rankings
export const subscribeToRankings = (competitionId, callback) => {
  const rankingsRef = ref(database, `rankings/${competitionId}`);
  
  // Escuchar cambios en tiempo real
  onValue(rankingsRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  });
  
  // Devolver función para desuscribirse
  return () => off(rankingsRef);
};

// Función para suscribirse a actualizaciones de calificaciones
export const subscribeToScores = (competitionId, participantId, callback) => {
  const scoresRef = ref(database, `scores/${competitionId}/${participantId}`);
  
  onValue(scoresRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  });
  
  return () => off(scoresRef);
};

// Función para actualizar calificaciones
export const updateScore = (competitionId, participantId, judgeId, scoreData) => {
  const scoreRef = ref(database, `scores/${competitionId}/${participantId}/${judgeId}`);
  return update(scoreRef, scoreData);
};

// Verificar estado de conexión
export const checkOnlineStatus = (callback) => {
  const connectedRef = ref(database, '.info/connected');
  
  onValue(connectedRef, (snapshot) => {
    const connected = snapshot.val();
    callback(connected);
  });
  
  return () => off(connectedRef);
};

// Escuchar cambios en calificaciones específicas
export const listenToJudgeScores = (competitionId, participantId, judgeId, callback) => {
  const scoreRef = ref(database, `scores/${competitionId}/${participantId}/${judgeId}/parameters`);
  
  onValue(scoreRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  });
  
  return () => off(scoreRef);
};

// Escuchar cambios en el ranking de un participante específico
export const listenToParticipantRanking = (competitionId, participantId, callback) => {
  const rankingRef = ref(database, `rankings/${competitionId}/${participantId}`);
  
  onValue(rankingRef, (snapshot) => {
    const data = snapshot.val();
    callback(data);
  });
  
  return () => off(rankingRef);
};

export default {
  subscribeToRankings,
  subscribeToScores,
  updateScore,
  checkOnlineStatus,
  listenToJudgeScores,
  listenToParticipantRanking
};