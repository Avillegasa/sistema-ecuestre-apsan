// src/pages/ParticipantAdd.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import ParticipantForm from '../components/competitions/ParticipantForm';
import Button from '../components/common/Button';
import { CompetitionContext } from '../context/CompetitionContext';

// Contenedor principal
const AddContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

// Título de página
const PageTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Información de competencia
const CompetitionInfo = styled.div`
  background-color: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.medium};
  padding: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
  border-left: 4px solid ${props => props.theme.colors.primary};
`;

const CompetitionName = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  margin: 0 0 ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.fontSizes.large};
`;

const CompetitionDetails = styled.div`
  color: ${props => props.theme.colors.gray};
  font-size: ${props => props.theme.fontSizes.small};
`;

// Mensaje de error
const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.medium};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Estado de carga
const LoadingMessage = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.gray};
`;

// Formatear fecha
const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('es-BO', options);
};

/**
 * Pantalla para añadir un participante a una competencia
 */
const ParticipantAdd = () => {
  const { competitionId } = useParams();
  const navigate = useNavigate();
  const { currentCompetition, loading, error, loadCompetition } = useContext(CompetitionContext);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(competitionId));
  }, [competitionId, loadCompetition]);
  
  // Si está cargando, mostrar mensaje
  if (loading) {
    return (
      <Layout>
        <AddContainer>
          <LoadingMessage>Cargando datos de la competencia...</LoadingMessage>
        </AddContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (error) {
    return (
      <Layout>
        <AddContainer>
          <ErrorMessage>{error}</ErrorMessage>
          <Button 
            onClick={() => navigate('/competitions')} 
            variant="primary"
          >
            Volver a Competencias
          </Button>
        </AddContainer>
      </Layout>
    );
  }
  
  // Si no hay competencia, mostrar mensaje
  if (!currentCompetition) {
    return (
      <Layout>
        <AddContainer>
          <ErrorMessage>No se encontró la competencia</ErrorMessage>
          <Button 
            onClick={() => navigate('/competitions')} 
            variant="primary"
          >
            Volver a Competencias
          </Button>
        </AddContainer>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <AddContainer>
        <PageTitle>Añadir Participante</PageTitle>
        
        <CompetitionInfo>
          <CompetitionName>{currentCompetition.name}</CompetitionName>
          <CompetitionDetails>
            {currentCompetition.location} • {formatDate(currentCompetition.start_date)} 
            {currentCompetition.end_date !== currentCompetition.start_date && 
              ` - ${formatDate(currentCompetition.end_date)}`}
          </CompetitionDetails>
        </CompetitionInfo>
        
        <ParticipantForm competitionId={parseInt(competitionId)} />
      </AddContainer>
    </Layout>
  );
};

export default ParticipantAdd;