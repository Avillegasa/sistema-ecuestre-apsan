import React from 'react';
import styled from 'styled-components';

// Contenedor principal
const FooterContainer = styled.footer`
  background-color: ${props => props.theme.colors.secondary};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
`;

// Contenido del footer
const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

// Logo y nombre
const FooterLogo = styled.div`
  font-family: ${props => props.theme.fonts.heading};
  font-size: ${props => props.theme.fontSizes.xl};
  font-weight: 700;
  margin-bottom: ${props => props.theme.spacing.md};
`;

// Links de navegación
const FooterNav = styled.nav`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const FooterNavList = styled.ul`
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    flex-direction: column;
    gap: ${props => props.theme.spacing.sm};
  }
`;

const FooterNavItem = styled.li`
  margin: 0 ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    margin: 0;
  }
`;

const FooterNavLink = styled.a`
  color: ${props => props.theme.colors.white};
  text-decoration: none;
  transition: color ${props => props.theme.transitions.fast};
  
  &:hover {
    color: ${props => props.theme.colors.lightGray};
    text-decoration: underline;
  }
`;

// Información de contacto
const ContactInfo = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Derechos de autor
const Copyright = styled.div`
  font-size: ${props => props.theme.fontSizes.small};
  opacity: 0.8;
`;

// Estado de conexión
const ConnectionStatus = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  background-color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.fontSizes.small};
  display: inline-flex;
  align-items: center;
`;

const StatusIndicator = styled.span`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: ${props => props.isOnline ? props.theme.colors.white : props.theme.colors.error};
  margin-right: ${props => props.theme.spacing.xs};
  display: inline-block;
`;

/**
 * Componente Footer para el pie de página
 * 
 * @param {Object} props - Propiedades del componente
 * @param {boolean} [props.isOnline=true] - Indica si la aplicación está online
 */
const Footer = ({ isOnline = true }) => {
  // Obtener el año actual
  const currentYear = new Date().getFullYear();
  
  return (
    <FooterContainer>
      <FooterContent>
        <FooterLogo>Sistema Ecuestre APSAN</FooterLogo>
        
        <FooterNav>
          <FooterNavList>
            <FooterNavItem>
              <FooterNavLink href="/">Inicio</FooterNavLink>
            </FooterNavItem>
            <FooterNavItem>
              <FooterNavLink href="/competitions">Competencias</FooterNavLink>
            </FooterNavItem>
            <FooterNavItem>
              <FooterNavLink href="/rankings">Rankings</FooterNavLink>
            </FooterNavItem>
            <FooterNavItem>
              <FooterNavLink href="https://apsan.org" target="_blank" rel="noopener noreferrer">
                Sitio Web APSAN
              </FooterNavLink>
            </FooterNavItem>
          </FooterNavList>
        </FooterNav>
        
        <ContactInfo>
          <p>APSAN - Asociación Paceña de Salto y Adiestramiento</p>
          <p>La Paz, Bolivia</p>
          <p>contacto@apsan.org</p>
        </ContactInfo>
        
        <Copyright>
          © {currentYear} APSAN. Todos los derechos reservados.
        </Copyright>
        
        <ConnectionStatus isOnline={isOnline}>
          <StatusIndicator isOnline={isOnline} />
          {isOnline ? 'Conectado' : 'Modo Offline'}
        </ConnectionStatus>
      </FooterContent>
    </FooterContainer>
  );
};

export default Footer;