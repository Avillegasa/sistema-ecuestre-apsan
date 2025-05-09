// frontend/src/services/api.js

import axios from 'axios';
import { store } from '../store';
import { refreshAccessToken, logout } from '../store/slices/authSlice';

// Crear instancia de axios
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = store.getState().auth.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Si el error es 401 (Unauthorized) y no se ha intentado refresh
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Intentar refrescar el token
        await store.dispatch(refreshAccessToken()).unwrap();
        
        // Actualizar el token en la solicitud original
        const newToken = store.getState().auth.token;
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        
        // Reintentar la solicitud original
        return api(originalRequest);
      } catch (refreshError) {
        // Si el refresh falla, cerrar sesión
        store.dispatch(logout());
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

