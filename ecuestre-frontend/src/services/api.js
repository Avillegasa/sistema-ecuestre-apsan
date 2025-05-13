// src/services/api.js
import axios from 'axios';

// Determinar la URL base según el entorno
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
  
  // Añadir CSRF token para peticiones no GET
  if (config.method !== 'get') {
    // Obtener token CSRF de la cookie (asumiendo Django)
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
  }
  
  return config;
});

// Función para obtener el valor de una cookie por su nombre
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Interceptor para manejar errores
// Mejorar el interceptor de respuesta
api.interceptors.response.use(
  response => response,
  error => {
    // Manejar errores específicos
    if (error.response) {
      const { status } = error.response;
      
      switch (status) {
        case 401:
          // No autorizado, redirigir a login
          localStorage.removeItem('authToken');
          window.location.href = '/login';
          break;
        case 403:
          // Prohibido, redirigir a página de no autorizado
          window.location.href = '/unauthorized';
          break;
        case 404:
          // Recurso no encontrado
          console.error('Recurso no encontrado');
          break;
        case 500:
          // Error del servidor
          console.error('Error del servidor');
          break;
        default:
          // Otros errores
          console.error('Error en la solicitud:', status);
      }
    } else if (error.request) {
      // La solicitud se realizó pero no se recibió respuesta (probablemente offline)
      console.error('No se recibió respuesta del servidor. Posiblemente offline.');
    } else {
      // Error al configurar la solicitud
      console.error('Error en la configuración de la solicitud:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Exportar métodos comunes
export const fetchRankings = (competitionId) => api.get(`/judging/rankings/${competitionId}/`);
export const fetchScorecard = (competitionId, participantId) => {
  return api.get(`/judging/scorecard/${competitionId}/${participantId}/`);
};
export const submitScore = (competitionId, participantId, scoreData) => {
  return api.post(`/judging/scorecard/${competitionId}/${participantId}/`, scoreData);
};

// Servicios de autenticación
export const login = (credentials) => api.post('/users/login/', credentials);
export const register = (userData) => api.post('/users/register/', userData);
export const getProfile = () => api.get('/users/me/');

// Exportar la instancia de api para uso personalizado
export default api;

// Competencias
export const fetchCompetitions = (params) => api.get('/competitions/', { params });
export const fetchCompetition = (id) => api.get(`/competitions/${id}/`);
export const createCompetition = (data) => api.post('/competitions/', data);
export const updateCompetition = (id, data) => api.put(`/competitions/${id}/`, data);
export const deleteCompetition = (id) => api.delete(`/competitions/${id}/`);

// Participantes
export const fetchParticipants = (competitionId) => api.get(`/competitions/${competitionId}/participants/`);
export const assignParticipant = (competitionId, data) => api.post(`/competitions/${competitionId}/assign_participant/`, data);
export const updateParticipant = (id, data) => api.put(`/participants/${id}/`, data);
export const deleteParticipant = (id) => api.delete(`/participants/${id}/`);
export const fetchParticipant = (id) => api.get(`/participants/${id}/`);

// Jinetes y Caballos
export const fetchRiders = (params) => api.get('/competitions/riders/', { params });
export const fetchHorses = (params) => api.get('/competitions/horses/', { params });
export const fetchCategories = () => api.get('/competitions/categories/');

// Jueces
export const fetchJudges = () => api.get('/users/judges/');
export const assignJudges = (competitionId, judgesData) => api.post(`/competitions/${competitionId}/assign_judges/`, judgesData);
export const removeJudge = (competitionId, judgeId) => api.delete(`/competitions/${competitionId}/judges/${judgeId}/`);

// Asignación de categorías
export const assignCategories = (competitionId, categoriesData) => api.post(`/competitions/${competitionId}/categories/`, categoriesData);


