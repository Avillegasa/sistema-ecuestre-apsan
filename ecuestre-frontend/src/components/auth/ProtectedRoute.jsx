// src/components/auth/ProtectedRoute.jsx
import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

/**
 * Componente para proteger rutas que requieren autenticación
 * 
 * @param {Object} props - Propiedades del componente
 * @param {React.ReactNode} props.children - Componente hijo a renderizar si está autenticado
 * @param {Array} [props.allowedRoles] - Roles permitidos para acceder a la ruta
 */
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user, isLoading } = useContext(AuthContext);
  
  // Mientras verifica autenticación, no renderizar nada
  if (isLoading) {
    return null;
  }
  
  // Si no está autenticado, redirigir al login
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  // Si hay roles permitidos definidos, verificar si el usuario tiene alguno de ellos
  if (allowedRoles.length > 0) {
    if (!user || !allowedRoles.includes(user.role)) {
      // Usuario no tiene el rol requerido, redirigir a página no autorizada
      return <Navigate to="/unauthorized" />;
    }
  }
  
  // Si está autenticado y tiene el rol adecuado, renderizar el componente hijo
  return children;
};

export default ProtectedRoute;