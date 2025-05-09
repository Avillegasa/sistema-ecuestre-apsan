
// frontend/src/services/userService.js

import api from './api';

const userService = {
  // Obtener el perfil del usuario actual
  getProfile: async () => {
    const response = await api.get('/usuarios/usuarios/me/');
    return response.data;
  },
  
  // Actualizar el perfil del usuario
  updateProfile: async (userData) => {
    const response = await api.patch(`/usuarios/usuarios/${userData.id}/`, userData);
    return response.data;
  },
  
  // Obtener todos los usuarios (para admin)
  getAllUsers: async (params = {}) => {
    const response = await api.get('/usuarios/usuarios/', { params });
    return response.data;
  },
  
  // Obtener un usuario específico
  getUser: async (id) => {
    const response = await api.get(`/usuarios/usuarios/${id}/`);
    return response.data;
  },
  
  // Crear un nuevo usuario (para admin)
  createUser: async (userData) => {
    const response = await api.post('/usuarios/usuarios/', userData);
    return response.data;
  },
  
  // Actualizar un usuario (para admin)
  updateUser: async (id, userData) => {
    const response = await api.patch(`/usuarios/usuarios/${id}/`, userData);
    return response.data;
  },
  
  // Eliminar un usuario (para admin)
  deleteUser: async (id) => {
    const response = await api.delete(`/usuarios/usuarios/${id}/`);
    return response.data;
  }
};

export default userService;