// src/App.js (con rutas actualizadas)
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import GlobalStyles from './styles/GlobalStyles';
import theme from './styles/theme';
import { AuthProvider } from './context/AuthContext';
import { CompetitionProvider } from './context/CompetitionContext';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Páginas
import Home from './pages/Home';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';
import FEIHelpPage from './pages/FEIHelpPage';

// Páginas de Competencias
import CompetitionList from './pages/CompetitionList';
import CompetitionDetail from './pages/CompetitionDetail';
import CompetitionCreate from './pages/CompetitionCreate';
import CompetitionEdit from './pages/CompetitionEdit';
import ParticipantAdd from './pages/ParticipantAdd';
import ParticipantEdit from './pages/ParticipantEdit';

// Páginas de Calificación y Rankings
import JudgingPanel from './pages/JudgingPanel';
import RankingBoard from './pages/RankingBoard';

// Otras páginas (temporales)
const AdminPanel = () => <div>Panel de Administración (en desarrollo)</div>;

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      <AuthProvider>
        <CompetitionProvider>
          <Router>
            <Routes>
              {/* Rutas públicas */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/unauthorized" element={<Unauthorized />} />
              <Route path="/help/fei" element={<FEIHelpPage />} />
              
              {/* Rutas de competencias */}
              <Route 
                path="/competitions" 
                element={
                  <ProtectedRoute>
                    <CompetitionList />
                  </ProtectedRoute>
                } 
              />

              <Route 
                path="/competitions/:competitionId/participants/:participantId/edit" 
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <ParticipantEdit />
                  </ProtectedRoute>
                } 
              />

              <Route 
                path="/competitions/new" 
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <CompetitionCreate />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/competitions/:id" 
                element={
                  <ProtectedRoute>
                    <CompetitionDetail />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/competitions/:id/edit" 
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <CompetitionEdit />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/competitions/:competitionId/participants/add" 
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <ParticipantAdd />
                  </ProtectedRoute>
                } 
              />
              
              {/* Rutas para jueces */}
              <Route 
                path="/judging/:competition_id/:participant_id" 
                element={
                  <ProtectedRoute allowedRoles={['admin', 'judge']}>
                    <JudgingPanel />
                  </ProtectedRoute>
                } 
              />
              
              {/* Rutas para rankings */}
              <Route 
                path="/rankings/:competition_id" 
                element={
                  <ProtectedRoute>
                    <RankingBoard />
                  </ProtectedRoute>
                } 
              />
              
              {/* Rutas para administradores */}
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <AdminPanel />
                  </ProtectedRoute>
                } 
              />
              
              {/* Ruta 404 */}
              <Route path="*" element={<div>Página no encontrada</div>} />
            </Routes>
          </Router>
        </CompetitionProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;