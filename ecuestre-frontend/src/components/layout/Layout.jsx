// src/components/layout/Layout.jsx
import React, { useState, useContext } from 'react';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { AuthContext } from '../../context/AuthContext';
import useOffline from '../../hooks/useOffline';

// Contenedor principal de la aplicación
const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${props => props.theme.colors.background};
`;

// Contenedor principal con sidebar
const MainContainer = styled.div`
  display: flex;
  flex: 1;
`;

// Sidebar
const SidebarContainer = styled.div`
  width: ${props => props.isCollapsed ? '80px' : '250px'};
  transition: width ${props => props.theme.transitions.medium};
`;

// Contenido principal
const ContentContainer = styled.main`
  flex: 1;
  margin-left: ${props => props.hasSidebar ? (props.isCollapsed ? '80px' : '250px') : '0'};
  padding: ${props => props.theme.spacing.lg};
  transition: margin-left ${props => props.theme.transitions.medium};
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    margin-left: 0;
    padding: ${props => props.theme.spacing.md};
  }
`;

// Barra de estado offline
const OfflineBar = styled.div`
  background-color: ${props => props.theme.colors.warning};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.sm};
  text-align: center;
  font-weight: 500;
`;

/**
 * Componente Layout principal de la aplicación
 * 
 * @param {Object} props - Propiedades del componente
 * @param {React.ReactNode} props.children - Contenido a mostrar
 * @param {boolean} [props.showSidebar=true] - Si mostrar el sidebar
 */
const Layout = ({ children, showSidebar = true }) => {
  const { isAuthenticated, isLoading } = useContext(AuthContext);
  const { isOnline } = useOffline();
  const location = useLocation();
  
  // Estado del sidebar
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  
  // Alternar estado del sidebar para móviles
  const toggleSidebar = () => {
    setIsMobileOpen(!isMobileOpen);
  };
  
  // Alternar colapso del sidebar para escritorio
  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };
  
  // No mostrar sidebar en login/register
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';
  
  // Si aún está verificando autenticación, mostrar carga
  if (isLoading) {
    return (
      <AppContainer>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <p>Cargando...</p>
        </div>
      </AppContainer>
    );
  }
  
  return (
    <AppContainer>
      {/* Barra de estado offline */}
      {!isOnline && (
        <OfflineBar>
          Modo Offline - Los cambios se sincronizarán cuando vuelva la conexión
        </OfflineBar>
      )}
      
      {/* Header */}
      {!isAuthPage && (
        <Header 
          toggleSidebar={toggleSidebar}
          isOffline={!isOnline}
        />
      )}
      
      <MainContainer>
        {/* Sidebar - solo mostrar si está autenticado y no es página de auth */}
        {showSidebar && isAuthenticated && !isAuthPage && (
          <SidebarContainer>
            <Sidebar 
              isOpen={isMobileOpen}
              toggleSidebar={toggleSidebar}
              isCollapsed={isCollapsed}
              toggleCollapse={toggleCollapse}
            />
          </SidebarContainer>
        )}
        
        {/* Contenido principal */}
        <ContentContainer 
          hasSidebar={showSidebar && isAuthenticated && !isAuthPage}
          isCollapsed={isCollapsed}
        >
          {children}
        </ContentContainer>
      </MainContainer>
      
      {/* Footer */}
      {!isAuthPage && (
        <Footer isOnline={isOnline} />
      )}
    </AppContainer>
  );
};

export default Layout;