
// frontend/src/services/authService.js

import api from './api';
import { jwtDecode } from 'jwt-decode';

const authService = {
  // Iniciar sesión
  login: async (credentials) => {
    const response = await api.post('/token/', credentials);
    
    // Decodificar el token para obtener información del usuario
    const decodedToken = jwtDecode(response.data.access);
    
    // Obtener información completa del usuario
    const userResponse = await api.get('/usuarios/usuarios/me/', {
      headers: {
        Authorization: `Bearer ${response.data.access}`
      }
    });
    
    return {
      token: response.data.access,
      refreshToken: response.data.refresh,
      user: userResponse.data
    };
  },
  
  // Cerrar sesión (limpieza en el cliente)
  logout: async () => {
    // En JWT no hay endpoint de logout, solo se eliminan los tokens
    return Promise.resolve();
  },
  
  // Refrescar token
  refreshToken: async (refreshToken) => {
    const response = await api.post('/token/refresh/', { refresh: refreshToken });
    return {
      token: response.data.access
    };
  },
  
  // Registrar nuevo usuario
  register: async (userData) => {
    const response = await api.post('/usuarios/usuarios/', userData);
    return response.data;
  },
  
  // Verificar si el usuario está autenticado
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    try {
      const decoded = jwtDecode(token);
      // Verificar si el token ha expirado
      const currentTime = Date.now() / 1000;
      return decoded.exp > currentTime;
    } catch (error) {
      return false;
    }
  }
};

export default authService;