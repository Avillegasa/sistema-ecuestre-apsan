// frontend/src/App.js

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';

// Importación de componentes
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import AdminDashboard from './pages/admin/Dashboard';
import UserManagement from './pages/admin/UserManagement';
import CompetitionManagement from './pages/admin/CompetitionManagement';

import JudgeDashboard from './pages/jueces/Dashboard';
import JudgeEvaluation from './pages/jueces/Evaluation';

import RiderDashboard from './pages/jinetes/Dashboard';
import RiderProfile from './pages/jinetes/Profile';
import HorseManagement from './pages/jinetes/HorseManagement';

import TrainerDashboard from './pages/entrenadores/Dashboard';
import RidersManagement from './pages/entrenadores/RidersManagement';

import PrivateRoute from './components/common/PrivateRoute';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Rutas Admin */}
          <Route 
            path="/admin" 
            element={
              <PrivateRoute userType="admin">
                <AdminDashboard />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/admin/users" 
            element={
              <PrivateRoute userType="admin">
                <UserManagement />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/admin/competitions" 
            element={
              <PrivateRoute userType="admin">
                <CompetitionManagement />
              </PrivateRoute>
            } 
          />
          
          {/* Rutas Jueces */}
          <Route 
            path="/juez" 
            element={
              <PrivateRoute userType="juez">
                <JudgeDashboard />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/juez/evaluacion/:id" 
            element={
              <PrivateRoute userType="juez">
                <JudgeEvaluation />
              </PrivateRoute>
            } 
          />
          
          {/* Rutas Jinetes */}
          <Route 
            path="/jinete" 
            element={
              <PrivateRoute userType="jinete">
                <RiderDashboard />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/jinete/perfil" 
            element={
              <PrivateRoute userType="jinete">
                <RiderProfile />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/jinete/caballos" 
            element={
              <PrivateRoute userType="jinete">
                <HorseManagement />
              </PrivateRoute>
            } 
          />
          
          {/* Rutas Entrenadores */}
          <Route 
            path="/entrenador" 
            element={
              <PrivateRoute userType="entrenador">
                <TrainerDashboard />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/entrenador/jinetes" 
            element={
              <PrivateRoute userType="entrenador">
                <RidersManagement />
              </PrivateRoute>
            } 
          />
          
          {/* Ruta por defecto */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* Ruta 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </Provider>
  );
}

export default App;