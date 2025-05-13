// src/pages/CompetitionEdit.jsx
import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import CompetitionForm from '../components/competitions/CompetitionForm';
import Button from '../components/common/Button';
import { fetchCompetition } from '../services/api';
import { CompetitionContext } from '../context/CompetitionContext';

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

/**
 * Pantalla para editar una competencia existente
 */
const CompetitionEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentCompetition, loading, error, loadCompetition } = useContext(CompetitionContext);
  
  // Cargar datos de la competencia
  useEffect(() => {
    loadCompetition(parseInt(id));
  }, [id, loadCompetition]);
  
  // Si está cargando, mostrar mensaje
  if (loading) {
    return (
      <Layout>
        <EditContainer>
          <LoadingMessage>Cargando datos de la competencia...</LoadingMessage>
        </EditContainer>
      </Layout>
    );
  }
  
  // Si hay error, mostrar mensaje
  if (error) {
    return (
      <Layout>
        <EditContainer>
          <ErrorMessage>{error}</ErrorMessage>
          <Button 
            onClick={() => navigate('/competitions')} 
            variant="primary"
          >
            Volver a Competencias
          </Button>
        </EditContainer>
      </Layout>
    );
  }
  
  // Si no hay competencia, mostrar mensaje
  if (!currentCompetition) {
    return (
      <Layout>
        <EditContainer>
          <ErrorMessage>No se encontró la competencia</ErrorMessage>
          <Button 
            onClick={() => navigate('/competitions')} 
            variant="primary"
          >
            Volver a Competencias
          </Button>
        </EditContainer>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <EditContainer>
        <PageTitle>Editar Competencia</PageTitle>
        <CompetitionForm initialData={currentCompetition} isEditing={true} />
      </EditContainer>
    </Layout>
  );
};

export default CompetitionEdit;