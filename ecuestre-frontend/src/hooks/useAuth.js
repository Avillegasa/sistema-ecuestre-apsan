// src/hooks/useAuth.js
import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { login as apiLogin } from '../services/api';

/**
 * Hook personalizado para gestionar la autenticación
 * Proporciona funciones para iniciar sesión y verificar el estado de autenticación
 */
const useAuth = () => {
  const { setUser, setIsAuthenticated } = useContext(AuthContext);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  /**
   * Función para iniciar sesión
   * @param {Object} credentials - Credenciales (email, password)
   * @returns {Object} - Resultado de la operación
   */
  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiLogin(credentials);
      const { token, user } = response.data;
      
      // Guardar token en localStorage
      localStorage.setItem('authToken', token);
      
      // Actualizar contexto
      setUser(user);
      setIsAuthenticated(true);
      
      setLoading(false);
      return { success: true };
    } catch (err) {
      console.error('Error de login:', err);
      
      const errorMessage = err.response?.data?.message || 
                          'No se pudo iniciar sesión. Verifique sus credenciales.';
      
      setError(errorMessage);
      setLoading(false);
      
      return { 
        success: false, 
        error: errorMessage 
      };
    }
  };
  
  return {
    login,
    loading,
    error
  };
};

export default useAuth;