// src/pages/Home.jsx
import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../context/AuthContext';
import Layout from '../components/layout/Layout';
import Button from '../components/common/Button';

// Contenedor principal
const HomeContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

// Sección hero
const HeroSection = styled.section`
  margin-bottom: ${props => props.theme.spacing.xl};
  text-align: center;
  padding: ${props => props.theme.spacing.xl} 0;
`;

const HeroTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  font-size: ${props => props.theme.fontSizes.xxl};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const HeroSubtitle = styled.p`
  font-size: ${props => props.theme.fontSizes.large};
  color: ${props => props.theme.colors.gray};
  margin-bottom: ${props => props.theme.spacing.lg};
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
`;

// Tarjetas de características
const FeaturesContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const FeatureCard = styled.div`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  padding: ${props => props.theme.spacing.lg};
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: ${props => props.theme.shadows.medium};
  }
`;

const FeatureTitle = styled.h3`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const FeatureIcon = styled.div`
  font-size: 2.5rem;
  margin-bottom: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.accent};
`;

// Sección de bienvenida para usuarios autenticados
const WelcomeSection = styled.section`
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.small};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const WelcomeTitle = styled.h2`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ActionButtonsContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
  flex-wrap: wrap;
`;

/**
 * Página de inicio
 */
const Home = () => {
  const { isAuthenticated, user } = useContext(AuthContext);
  
  return (
    <Layout>
      <HomeContainer>
        {isAuthenticated ? (
          // Contenido para usuarios autenticados
          <WelcomeSection>
            <WelcomeTitle>Bienvenido, {user?.firstName || 'Usuario'}</WelcomeTitle>
            <p>Bienvenido al Sistema Ecuestre APSAN. Utilice el panel lateral para navegar por las diferentes secciones del sistema.</p>
            
            <ActionButtonsContainer>
              <Button 
                as={Link} 
                to="/competitions" 
                variant="primary"
              >
                Ver Competencias
              </Button>
              
              {user?.role === 'judge' && (
                <Button 
                  as={Link} 
                  to="/judge" 
                  variant="secondary"
                >
                  Panel de Juez
                </Button>
              )}
              
              {user?.role === 'admin' && (
                <Button 
                  as={Link} 
                  to="/admin" 
                  variant="secondary"
                >
                  Panel de Administración
                </Button>
              )}
              
              <Button 
                as={Link} 
                to="/rankings" 
                variant="outline"
              >
                Ver Rankings
              </Button>
            </ActionButtonsContainer>
          </WelcomeSection>
        ) : (
          // Contenido para usuarios no autenticados
          <HeroSection>
            <HeroTitle>Sistema Ecuestre APSAN</HeroTitle>
            <HeroSubtitle>
              Sistema de gestión y calificación para competencias ecuestres de la Asociación Paceña de Salto y Adiestramiento
            </HeroSubtitle>
            
            <Button 
              as={Link}
              to="/login" 
              variant="primary" 
              size="large"
            >
              Iniciar Sesión
            </Button>
          </HeroSection>
        )}
        
        {/* Funcionalidades */}
        <FeaturesContainer>
          <FeatureCard>
            <FeatureIcon>🏆</FeatureIcon>
            <FeatureTitle>Competencias</FeatureTitle>
            <p>Gestión completa de competencias ecuestres, con calendario, participantes y resultados.</p>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>📋</FeatureIcon>
            <FeatureTitle>Calificación FEI</FeatureTitle>
            <p>Implementación del sistema FEI de 3 celdas para calificación profesional de jinetes.</p>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>📱</FeatureIcon>
            <FeatureTitle>Modo Offline</FeatureTitle>
            <p>Califique incluso sin conexión a internet. Sus datos se sincronizarán automáticamente.</p>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>📊</FeatureIcon>
            <FeatureTitle>Rankings en vivo</FeatureTitle>
            <p>Visualización de rankings en tiempo real con actualizaciones instantáneas.</p>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>🔒</FeatureIcon>
            <FeatureTitle>Acceso Seguro</FeatureTitle>
            <p>Sistema de autenticación seguro con roles específicos para administradores, jueces y visualizadores.</p>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>🔄</FeatureIcon>
            <FeatureTitle>Sincronización</FeatureTitle>
            <p>Todas las calificaciones se sincronizan automáticamente entre dispositivos.</p>
          </FeatureCard>
        </FeaturesContainer>
      </HomeContainer>
    </Layout>
  );
};

export default Home;