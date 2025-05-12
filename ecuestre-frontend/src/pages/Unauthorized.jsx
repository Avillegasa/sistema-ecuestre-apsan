// src/pages/Unauthorized.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';

// Contenedor principal
const UnauthorizedContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  min-height: 60vh;
`;

// Icono
const ErrorIcon = styled.div`
  font-size: 5rem;
  color: ${props => props.theme.colors.error};
  margin-bottom: ${props => props.theme.spacing.md};
`;

// Título
const Title = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.error};
  margin-bottom: ${props => props.theme.spacing.md};
`;

// Mensaje
const Message = styled.p`
  font-size: ${props => props.theme.fontSizes.large};
  color: ${props => props.theme.colors.gray};
  margin-bottom: ${props => props.theme.spacing.xl};
  max-width: 600px;
`;

/**
 * Página de Acceso No Autorizado
 */
const Unauthorized = () => {
  return (
    <Layout showSidebar={false}>
      <UnauthorizedContainer>
        <ErrorIcon>🔒</ErrorIcon>
        <Title>Acceso No Autorizado</Title>
        <Message>
          Lo sentimos, no tiene permisos para acceder a esta sección. Si cree que esto es un error, contacte al administrador del sistema.
        </Message>
        
        <Button as={Link} to="/" variant="primary" size="large">
          Volver al Inicio
        </Button>
      </UnauthorizedContainer>
    </Layout>
  );
};

export default Unauthorized;