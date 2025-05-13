// src/pages/RankingBoard.jsx (versión mejorada)
import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';
import RealtimeRankingTable from '../components/rankings/RankingTable';
import { CompetitionContext } from '../context/CompetitionContext';
import { useRealtimeSync } from '../hooks/useRealtimeSync';
import { fetchRankings } from '../services/api';
import { formatPercentage } from '../utils/formatters';

// Contenedor principal
const RankingContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

// Cabecera
const Header = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
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
const ModesContainer = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
`;

const ModeButton = styled(Button)`
  opacity: ${props => props.isActive ? 1 : 0.6};
`;

/**
 * Página mejorada de Rankings en tiempo real
 */
const RankingBoard = () => {
  const { competition_id } = useParams();
  const { currentCompetition, loading: competitionLoading, error: competitionError, loadCompetition } = useContext(CompetitionContext);
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('table'); // 'table', 'fullscreen', 'projection'
  const { isOnline, syncMethod } = useRealtimeSync();
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(competition_id));
  }, [competition_id, loadCompetition]);
  
  // Cargar rankings
  useEffect(() => {
    const loadRankings = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetchRankings(competition_id);
        setRankings(response.data);
      } catch (err) {
        console.error('Error al cargar rankings:', err);
        setError('Error al cargar los rankings. ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    
    loadRankings();
  }, [competition_id]);
  
  // Cambiar modo de visualización
  const handleViewModeChange = (mode) => {
    setViewMode(mode);
  };
  
  // Si está cargando, mostrar mensaje
  if (competitionLoading || loading) {
    return (
      <Layout>
        <RankingContainer>
          <LoadingMessage>Cargando datos...</LoadingMessage>
        </RankingContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (competitionError || error) {
    return (
      <Layout>
        <RankingContainer>
          <ErrorMessage>{competitionError || error}</ErrorMessage>
          <Button as={Link} to="/competitions">Volver a Competencias</Button>
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
          <Button as={Link} to="/competitions">Volver a Competencias</Button>
        </RankingContainer>
      </Layout>
    );
  }
  
  // Renderizar según el modo de visualización
  const renderContent = () => {
    // Componentes comunes
    const table = (
      <RealtimeRankingTable
        competitionId={competition_id}
        title="Rankings de la Competencia"
        subtitle={currentCompetition.name}
        showAnimation={true}
      />
    );
    
    switch (viewMode) {
      case 'fullscreen':
        return (
          <FullscreenContainer>
            {table}
            <ExitButton onClick={() => handleViewModeChange('table')}>
              Salir del Modo Pantalla Completa
            </ExitButton>
          </FullscreenContainer>
        );
      
      case 'projection':
        return (
          <ProjectionContainer>
            <ProjectionHeader>
              <ProjectionTitle>{currentCompetition.name}</ProjectionTitle>
              <ProjectionSubtitle>Rankings en Tiempo Real</ProjectionSubtitle>
            </ProjectionHeader>
            {table}
            <ExitButton onClick={() => handleViewModeChange('table')}>
              Salir del Modo Proyección
            </ExitButton>
          </ProjectionContainer>
        );
      
      default: // 'table'
        return (
          <>
            <Header>
              <Title>Rankings de la Competencia</Title>
              <Subtitle>{currentCompetition.name}</Subtitle>
            </Header>
            
            <ModesContainer>
              <ModeButton 
                variant="outline" 
                isActive={viewMode === 'table'}
                onClick={() => handleViewModeChange('table')}
              >
                Vista Normal
              </ModeButton>
              <ModeButton 
                variant="outline" 
                isActive={viewMode === 'fullscreen'}
                onClick={() => handleViewModeChange('fullscreen')}
              >
                Pantalla Completa
              </ModeButton>
              <ModeButton 
                variant="outline" 
                isActive={viewMode === 'projection'}
                onClick={() => handleViewModeChange('projection')}
              >
                Modo Proyección
              </ModeButton>
            </ModesContainer>
            
            {table}
            
            <SyncInfo>
              <SyncMethod>
                Método de sincronización: <strong>{syncMethod}</strong>
              </SyncMethod>
              <ConnectionStatus isOnline={isOnline}>
                {isOnline ? 'Conectado' : 'Sin conexión'}
              </ConnectionStatus>
            </SyncInfo>
            
            <Button as={Link} to={`/competitions/${competition_id}`} variant="primary">
              Volver a la Competencia
            </Button>
          </>
        );
    }
  };
  
  // Wrapper según el modo
  const getWrapper = (content) => {
    if (viewMode === 'fullscreen' || viewMode === 'projection') {
      return content;
    }
    
    return (
      <Layout>
        <RankingContainer>
          {content}
        </RankingContainer>
      </Layout>
    );
  };
  
  return getWrapper(renderContent());
};

// Estilos adicionales para los modos especiales
const FullscreenContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${props => props.theme.colors.background};
  z-index: 9999;
  padding: 20px;
  overflow-y: auto;
`;

const ProjectionContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  z-index: 9999;
  padding: 20px;
  overflow-y: auto;
`;

const ProjectionHeader = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const ProjectionTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  font-size: 48px;
  margin: 0 0 16px;
`;

const ProjectionSubtitle = styled.div`
  font-size: 24px;
  opacity: 0.8;
`;

const ExitButton = styled(Button)`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 10000;
`;

const SyncInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
  padding: 12px;
  background-color: ${props => props.theme.colors.background};
  border-radius: 8px;
`;

const SyncMethod = styled.div`
  font-size: 14px;
  color: ${props => props.theme.colors.gray};
`;

const ConnectionStatus = styled.div`
  display: flex;
  align-items: center;
  font-size: 14px;
  color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
  
  &:before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
    margin-right: 8px;
  }
`;

export default RankingBoard;