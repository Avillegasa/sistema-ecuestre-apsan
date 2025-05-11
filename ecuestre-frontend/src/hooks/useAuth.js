import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { login as apiLogin, getProfile } from '../services/api';

// Hook personalizado para gestionar la autenticación
const useAuth = () => {
  const { user, setUser, isAuthenticated, setIsAuthenticated } = useContext(AuthContext);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Verificar token al cargar
  useEffect(() => {
    const checkAuth = async () => {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      
      if (token) {
        try {
          // Verificar si el token es válido obteniendo el perfil del usuario
          const response = await getProfile();
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (err) {
          console.error('Error al verificar autenticación:', err);
          // Si hay error, limpiar el token
          localStorage.removeItem('authToken');
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
      
      setLoading(false);
    };
    
    checkAuth();
  }, [setUser, setIsAuthenticated]);

  // Función para iniciar sesión
  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiLogin(credentials);
      const { token, user } = response.data;
      
      // Guardar token en localStorage
      localStorage.setItem('authToken', token);
      
      // Actualizar el estado
      setUser(user);
      setIsAuthenticated(true);
      setLoading(false);
      
      return { success: true };
    } catch (err) {
      console.error('Error de login:', err);
      setError(err.response?.data?.message || 'Error al iniciar sesión');
      setLoading(false);
      
      return { success: false, error: err.response?.data?.message || 'Error al iniciar sesión' };
    }
  };

  // Función para cerrar sesión
  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    setIsAuthenticated(false);
  };

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    logout
  };
};

export default useAuth;