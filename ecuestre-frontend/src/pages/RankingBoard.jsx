// src/pages/RankingBoard.jsx (mejorado)
import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import styled, { css } from 'styled-components';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';
import RealtimeRankingTable from '../components/rankings/RealtimeRankingTable';
import { CompetitionContext } from '../context/CompetitionContext';
import { useRealtimeSync } from '../hooks/useRealtimeSync';
import DynamicLogo from '../components/logos/DynamicLogo';
import Timer from '../components/common/Timer';

// Contenedor principal
const RankingContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.lg};
`;

// Cabecera
const Header = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
`;

const Title = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Subtitle = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
`;

// Sección de información de la competencia
const CompetitionInfo = styled.div`
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
    align-items: flex-start;
    gap: ${props => props.theme.spacing.md};
  }
`;

const CompetitionDetail = styled.div`
  flex: 1;
`;

const CompetitionName = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes.large};
`;

const CompetitionLocation = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
  display: flex;
  align-items: center;
  
  &:before {
    content: "📍";
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

const CompetitionDate = styled.div`
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.gray};
  display: flex;
  align-items: center;
  
  &:before {
    content: "📅";
    margin-right: ${props => props.theme.spacing.xs};
  }
`;

// Estado de carga
const LoadingMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.gray};
`;

// Mensaje de error
const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Modos de visualización de rankings
const ViewModesContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const ViewModeButton = styled(Button)`
  flex: 1;
  min-width: 150px;
  opacity: ${props => props.isActive ? 1 : 0.6};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex: 0 0 100%;
  }
`;

// Contenedor para modos especiales (fullscreen/projection)
const SpecialModeContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  padding: ${props => props.theme.spacing.md};
  overflow-y: auto;
  
  ${props => props.mode === 'fullscreen' && css`
    background-color: ${props => props.theme.colors.background};
  `}
  
  ${props => props.mode === 'projection' && css`
    background-color: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.white};
    padding: ${props => props.theme.spacing.xl};
  `}
`;

// Cabecera para el modo de proyección
const ProjectionHeader = styled.div`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xxl};
  animation: fadeIn 1s ease;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const ProjectionTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  font-size: 3rem;
  margin-bottom: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.white};
`;

const ProjectionSubtitle = styled.div`
  font-size: 1.5rem;
  margin-bottom: ${props => props.theme.spacing.lg};
  opacity: 0.9;
`;

const LogoContainer = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  justify-content: center;
`;

// Botón para salir del modo especial
const ExitButton = styled(Button)`
  position: fixed;
  bottom: ${props => props.theme.spacing.lg};
  right: ${props => props.theme.spacing.lg};
  z-index: 10000;
  box-shadow: ${props => props.theme.shadows.large};
`;

// Información de sincronización
const SyncInfoContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const SyncMethod = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  
  span {
    font-weight: 500;
  }
`;

const SyncStatus = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
  
  &:before {
    content: "";
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
  }
`;

// Botones de acción
const ActionButtonsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: ${props => props.theme.spacing.xl};
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
  }
`;

/**
 * Componente RankingBoard mejorado con múltiples modos de visualización
 */
const RankingBoard = () => {
  const { competition_id } = useParams();
  const navigate = useNavigate();
  const { currentCompetition, loading: competitionLoading, error: competitionError, loadCompetition } = useContext(CompetitionContext);
  const { isOnline, syncMethod } = useRealtimeSync();
  
  // Estados
  const [viewMode, setViewMode] = useState('normal');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [refreshInterval, setRefreshInterval] = useState(0); // 0 = realtime, positive = interval in seconds
  
  // Cargar datos de la competencia
  useEffect(() => {
    if (competition_id) {
      loadCompetition(parseInt(competition_id));
    }
  }, [competition_id, loadCompetition]);
  
  // Formatear fecha para mostrar
  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-BO', options);
  };
  
  // Cambiar modo de visualización
  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    
    // Si entramos en modo proyección o pantalla completa, intentar activar modo pantalla completa del navegador
    if (mode === 'projection' || mode === 'fullscreen') {
      try {
        const docEl = document.documentElement;
        
        if (docEl.requestFullscreen) {
          docEl.requestFullscreen();
        } else if (docEl.mozRequestFullScreen) { // Firefox
          docEl.mozRequestFullScreen();
        } else if (docEl.webkitRequestFullscreen) { // Chrome, Safari
          docEl.webkitRequestFullscreen();
        } else if (docEl.msRequestFullscreen) { // IE/Edge
          docEl.msRequestFullscreen();
        }
      } catch (error) {
        console.warn('No se pudo activar el modo pantalla completa:', error);
      }
    } else {
      // Si salimos de esos modos, salir del modo pantalla completa
      try {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen();
        }
      } catch (error) {
        console.warn('No se pudo salir del modo pantalla completa:', error);
      }
    }
  };

  // Si está cargando, mostrar indicador
  if (competitionLoading) {
    return (
      <Layout>
        <RankingContainer>
          <LoadingMessage>Cargando datos de la competencia...</LoadingMessage>
        </RankingContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (competitionError) {
    return (
      <Layout>
        <RankingContainer>
          <ErrorMessage>{competitionError}</ErrorMessage>
          <Button as={Link} to="/competitions" variant="primary">
            Volver a Competencias
          </Button>
        </RankingContainer>
      </Layout>
    );
  }
  
  // Si no hay competencia, mostrar mensaje
  if (!currentCompetition) {
    return (
      <Layout>
        <RankingContainer>
          <ErrorMessage>No se encontró la competencia</ErrorMessage>
          <Button as={Link} to="/competitions" variant="primary">
            Volver a Competencias
          </Button>
        </RankingContainer>
      </Layout>
    );
  }

  // Renderizar contenido según el modo de visualización
  const renderContent = () => {
    // Componente base de tabla de rankings que usaremos en todos los modos
    const rankingTable = (
      <RealtimeRankingTable
        competitionId={competition_id}
        title="Rankings de la Competencia"
        subtitle={currentCompetition.name}
        showAnimation={true}
        isProjection={viewMode === 'projection'}
        initialCategory={categoryFilter}
      />
    );
    
    // Renderizar según el modo seleccionado
    switch (viewMode) {
      case 'fullscreen':
        return (
          <SpecialModeContainer mode="fullscreen">
            <Header>
              <Title>Rankings en Tiempo Real</Title>
            </Header>
            
            {rankingTable}
            
            <ExitButton
              variant="primary"
              size="large"
              onClick={() => handleViewModeChange('normal')}
            >
              Salir de Pantalla Completa
            </ExitButton>
          </SpecialModeContainer>
        );
      
      case 'projection':
        return (
          <SpecialModeContainer mode="projection">
            <ProjectionHeader>
              <ProjectionTitle>{currentCompetition.name}</ProjectionTitle>
              <ProjectionSubtitle>Rankings en Tiempo Real</ProjectionSubtitle>
              
              <LogoContainer>
                <DynamicLogo 
                  src="/logo-apsan-large.png" 
                  fallbackText="APSAN"
                  size="120px"
                  textColor="white"
                  icon="🏇"
                  iconColor="white"
                />
              </LogoContainer>
              
              <div style={{ position: 'absolute', top: '20px', right: '20px' }}>
                <Timer large={true} showSeconds={true} />
              </div>
            </ProjectionHeader>
            
            {rankingTable}
            
            <ExitButton
              variant="light"
              size="large"
              onClick={() => handleViewModeChange('normal')}
            >
              Salir de Modo Proyección
            </ExitButton>
          </SpecialModeContainer>
        );
      
      default: // 'normal'
        return (
          <Layout>
            <RankingContainer>
              <Header>
                <div>
                  <Title>Rankings de la Competencia</Title>
                  <Subtitle>Resultados en tiempo real</Subtitle>
                </div>
                
                <Button 
                  as={Link} 
                  to={`/competitions/${competition_id}`}
                  variant="outline"
                >
                  Volver a la Competencia
                </Button>
              </Header>
              
              <CompetitionInfo>
                <CompetitionDetail>
                  <CompetitionName>{currentCompetition.name}</CompetitionName>
                  <CompetitionLocation>{currentCompetition.location}</CompetitionLocation>
                </CompetitionDetail>
                
                <CompetitionDate>
                  {formatDate(currentCompetition.start_date)}
                  {currentCompetition.end_date !== currentCompetition.start_date && 
                    ` - ${formatDate(currentCompetition.end_date)}`}
                </CompetitionDate>
              </CompetitionInfo>
              
              <ViewModesContainer>
                <ViewModeButton
                  variant="outline"
                  isActive={viewMode === 'normal'}
                  onClick={() => handleViewModeChange('normal')}
                >
                  <span>📊</span> Vista Normal
                </ViewModeButton>
                
                <ViewModeButton
                  variant="outline"
                  isActive={viewMode === 'fullscreen'}
                  onClick={() => handleViewModeChange('fullscreen')}
                >
                  <span>🖥️</span> Pantalla Completa
                </ViewModeButton>
                
                <ViewModeButton
                  variant="outline"
                  isActive={viewMode === 'projection'}
                  onClick={() => handleViewModeChange('projection')}
                >
                  <span>📽️</span> Modo Proyección
                </ViewModeButton>
              </ViewModesContainer>
              
              <SyncInfoContainer>
                <SyncMethod>
                  Método de sincronización: <span>{syncMethod}</span>
                </SyncMethod>
                
                <SyncStatus isOnline={isOnline}>
                  {isOnline ? 'Conectado - Actualizando en tiempo real' : 'Sin conexión - Mostrando datos locales'}
                </SyncStatus>
              </SyncInfoContainer>
              
              {rankingTable}
              
              <ActionButtonsContainer>
                <Button
                  as={Link}
                  to={`/competitions/${competition_id}`}
                  variant="primary"
                >
                  Volver a la Competencia
                </Button>
                
                <Button
                  as={Link}
                  to="/help/fei"
                  variant="outline"
                  target="_blank"
                >
                  Información Sistema FEI
                </Button>
              </ActionButtonsContainer>
            </RankingContainer>
          </Layout>
        );
    }
  };
  
  return renderContent();
};

export default RankingBoard;