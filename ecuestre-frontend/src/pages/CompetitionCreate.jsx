// src/pages/CompetitionCreate.jsx
import React from 'react';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import CompetitionForm from '../components/competitions/CompetitionForm';

// Contenedor principal
const CreateContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`;

// Título de página
const PageTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

/**
 * Pantalla para crear una nueva competencia
 */
const CompetitionCreate = () => {
  return (
    <Layout>
      <CreateContainer>
        <PageTitle>Crear Nueva Competencia</PageTitle>
        <CompetitionForm />
      </CreateContainer>
    </Layout>
  );
};

export default CompetitionCreate;