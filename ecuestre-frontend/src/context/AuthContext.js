// src/context/AuthContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import { getProfile } from '../services/api';

// Crear el contexto de autenticación
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Estado para almacenar información del usuario y estado de autenticación
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Verificar autenticación al cargar la app
  useEffect(() => {
    const verifyAuth = async () => {
      const token = localStorage.getItem('authToken');
      
      if (token) {
        try {
          // Verificar si el token es válido
          const response = await getProfile();
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          // Si hay error, limpiar token
          console.error('Error al verificar autenticación:', error);
          localStorage.removeItem('authToken');
          setUser(null);
          setIsAuthenticated(false);
        }
      }
      
      setIsLoading(false);
    };
    
    verifyAuth();
  }, []);
  
  // Función para cerrar sesión
  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    setIsAuthenticated(false);
  };
  
  // Proporcionar contexto a los componentes hijos
  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        setUser, 
        isAuthenticated, 
        setIsAuthenticated,
        isLoading,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;