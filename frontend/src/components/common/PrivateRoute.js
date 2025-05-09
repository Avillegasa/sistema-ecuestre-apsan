// frontend/src/components/common/PrivateRoute.js

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

/**
 * Componente para proteger rutas que requieren autenticación.
 * Redirige a login si no hay usuario autenticado o al dashboard correspondiente
 * si el tipo de usuario no tiene permiso para acceder.
 * 
 * @param {string} userType - Tipo de usuario requerido para acceder a la ruta (admin, juez, jinete, entrenador)
 * @param {React.ReactNode} children - Componentes hijos a renderizar si el usuario está autenticado
 */
const PrivateRoute = ({ userType, children }) => {
  const { isAuthenticated, user } = useSelector(state => state.auth);
  const location = useLocation();

  // Si no está autenticado, redirigir a login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Si se requiere un tipo específico de usuario y no coincide, redirigir a su dashboard
  if (userType && user.tipo_usuario !== userType) {
    // Redirigir al dashboard correspondiente según el tipo de usuario
    switch (user.tipo_usuario) {
      case 'admin':
        return <Navigate to="/admin" replace />;
      case 'juez':
        return <Navigate to="/juez" replace />;
      case 'jinete':
        return <Navigate to="/jinete" replace />;
      case 'entrenador':
        return <Navigate to="/entrenador" replace />;
      default:
        return <Navigate to="/login" replace />;
    }
  }

  // Si todo está bien, renderizar los hijos
  return children;
};

export default PrivateRoute;