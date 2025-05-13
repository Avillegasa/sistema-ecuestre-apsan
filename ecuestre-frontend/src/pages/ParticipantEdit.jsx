// Crear un nuevo archivo: src/pages/ParticipantEdit.jsx

import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import ParticipantForm from '../components/competitions/ParticipantForm';
import Button from '../components/common/Button';
import { CompetitionContext } from '../context/CompetitionContext';
import { fetchParticipant } from '../services/api';

// Contenedor principal
const EditContainer = styled.div`
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
 * Pantalla para editar un participante
 */
const ParticipantEdit = () => {
  const { competitionId, participantId } = useParams();
  const navigate = useNavigate();
  const { currentCompetition, loading, error, loadCompetition } = useContext(CompetitionContext);
  const [participant, setParticipant] = useState(null);
  const [participantLoading, setParticipantLoading] = useState(true);
  const [participantError, setParticipantError] = useState(null);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(competitionId));
  }, [competitionId, loadCompetition]);
  
  // Cargar datos del participante
  useEffect(() => {
    const loadParticipant = async () => {
      setParticipantLoading(true);
      setParticipantError(null);
      
      try {
        const response = await fetchParticipant(participantId);
        setParticipant(response.data);
      } catch (err) {
        console.error('Error al cargar participante:', err);
        setParticipantError('Error al cargar datos del participante');
      } finally {
        setParticipantLoading(false);
      }
    };
    
    loadParticipant();
  }, [participantId]);
  
  // Si está cargando, mostrar mensaje
  if (loading || participantLoading) {
    return (
      <Layout>
        <EditContainer>
          <LoadingMessage>Cargando datos...</LoadingMessage>
        </EditContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (error || participantError) {
    return (
      <Layout>
        <EditContainer>
          <ErrorMessage>{error || participantError}</ErrorMessage>
          <Button 
            onClick={() => navigate(`/competitions/${competitionId}`)} 
            variant="primary"
          >
            Volver a la Competencia
          </Button>
        </EditContainer>
      </Layout>
    );
  }
  
  // Si no hay competencia o participante, mostrar mensaje
  if (!currentCompetition || !participant) {
    return (
      <Layout>
        <EditContainer>
          <ErrorMessage>No se encontraron los datos necesarios</ErrorMessage>
          <Button 
            onClick={() => navigate(`/competitions/${competitionId}`)} 
            variant="primary"
          >
            Volver a la Competencia
          </Button>
        </EditContainer>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <EditContainer>
        <PageTitle>Editar Participante</PageTitle>
        
        <CompetitionInfo>
          <CompetitionName>{currentCompetition.name}</CompetitionName>
          <CompetitionDetails>
            {currentCompetition.location} • {formatDate(currentCompetition.start_date)} 
            {currentCompetition.end_date !== currentCompetition.start_date && 
              ` - ${formatDate(currentCompetition.end_date)}`}
          </CompetitionDetails>
        </CompetitionInfo>
        
        <ParticipantForm 
          competitionId={parseInt(competitionId)} 
          initialData={participant}
          isEditing={true}
        />
      </EditContainer>
    </Layout>
  );
};

export default ParticipantEdit;