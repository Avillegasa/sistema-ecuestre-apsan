import axios from 'axios';

// Determinar el baseURL según el entorno
const baseURL = process.env.NODE_ENV === 'production'
  ? 'https://sistema-ecuestre.apsan.org/api'
  : 'http://localhost:8000/api';

// Crear instancia de axios con configuración por defecto
const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor para añadir token de autenticación
api.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores
api.interceptors.response.use(
  response => response,
  error => {
    // Manejar errores comunes (401, 403, etc.)
    if (error.response) {
      if (error.response.status === 401) {
        // Redireccionar a login si hay problemas de autenticación
        localStorage.removeItem('authToken');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Exportar métodos comunes
export const fetchCompetitions = () => api.get('/competitions/');
export const fetchCompetition = (id) => api.get(`/competitions/${id}/`);
export const fetchRankings = (competitionId) => api.get(`/judging/rankings/${competitionId}/`);
export const fetchScorecard = (competitionId, participantId) => {
  return api.get(`/judging/score/${competitionId}/${participantId}/`);
};
export const submitScore = (competitionId, participantId, scoreData) => {
  return api.post(`/judging/score/${competitionId}/${participantId}/`, scoreData);
};

// Servicios de autenticación
export const login = (credentials) => api.post('/users/login/', credentials);
export const register = (userData) => api.post('/users/register/', userData);
export const getProfile = () => api.get('/users/profile/');

// Exportar la instancia de api para uso personalizado
export default api;