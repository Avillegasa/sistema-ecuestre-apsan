// src/components/layout/Header.jsx
import React, { useState, useContext } from 'react';
import styled from 'styled-components';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import Button from '../common/Button';

// Contenedor principal
const HeaderContainer = styled.header`
  background-color: ${props => props.theme.colors.white};
  box-shadow: ${props => props.theme.shadows.small};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
`;

// Logo y título
const LogoContainer = styled.div`
  display: flex;
  align-items: center;
`;

const LogoTitle = styled(Link)`
  font-family: ${props => props.theme.fonts.heading};
  font-size: ${props => props.theme.fontSizes.xl};
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  text-decoration: none;
  margin-left: ${props => props.theme.spacing.sm};
  
  &:hover {
    color: ${props => props.theme.colors.accent};
  }
`;

// Navegación principal
const Nav = styled.nav`
  display: flex;
  align-items: center;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: ${props => props.isOpen ? 'flex' : 'none'};
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: ${props => props.theme.colors.white};
    box-shadow: ${props => props.theme.shadows.medium};
    flex-direction: column;
    padding: ${props => props.theme.spacing.md};
    z-index: 99;
  }
`;

const NavList = styled.ul`
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    flex-direction: column;
    width: 100%;
  }
`;

const NavItem = styled.li`
  margin: 0 ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    margin: ${props => props.theme.spacing.sm} 0;
    width: 100%;
  }
`;

const NavLink = styled(Link)`
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.theme.colors.text};
  text-decoration: none;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.small};
  transition: background-color ${props => props.theme.transitions.fast};
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
    color: ${props => props.theme.colors.primary};
  }
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: block;
    padding: ${props => props.theme.spacing.md};
    text-align: center;
  }
`;

// Contenedor para botones de usuario
const UserActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    margin-top: ${props => props.theme.spacing.md};
    width: 100%;
    justify-content: center;
  }
`;

// Botón para el menú móvil
const MenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  font-size: ${props => props.theme.fontSizes.xl};
  cursor: pointer;
  color: ${props => props.theme.colors.primary};
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    display: block;
  }
`;

// Indicador de estado offline
const OfflineIndicator = styled.div`
  background-color: ${props => props.theme.colors.error};
  color: ${props => props.theme.colors.white};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.fontSizes.small};
  margin-right: ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    margin: ${props => props.theme.spacing.sm} 0;
    text-align: center;
  }
`;

/**
 * Componente Header para la navegación principal
 * 
 * @param {Object} props - Propiedades del componente
 * @param {Function} props.toggleSidebar - Función para mostrar/ocultar el sidebar en móviles
 * @param {boolean} [props.isOffline=false] - Indica si la aplicación está en modo offline
 */
const Header = ({ toggleSidebar, isOffline = false }) => {
  const { isAuthenticated, user, logout } = useContext(AuthContext);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  
  // Alternar menú móvil
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };
  
  // Cerrar sesión
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <HeaderContainer>
      <LogoContainer>
        <LogoTitle to="/">Sistema Ecuestre APSAN</LogoTitle>
      </LogoContainer>
      
      <MenuButton onClick={toggleMenu} aria-label="Menú">
        {isMenuOpen ? '✕' : '☰'}
      </MenuButton>
      
      <Nav isOpen={isMenuOpen}>
        <NavList>
          <NavItem>
            <NavLink to="/" onClick={() => setIsMenuOpen(false)}>Inicio</NavLink>
          </NavItem>
          {isAuthenticated && (
            <>
              <NavItem>
                <NavLink to="/competitions" onClick={() => setIsMenuOpen(false)}>Competencias</NavLink>
              </NavItem>
              {user?.role === 'admin' && (
                <NavItem>
                  <NavLink to="/admin" onClick={() => setIsMenuOpen(false)}>Administración</NavLink>
                </NavItem>
              )}
            </>
          )}
        </NavList>
        
        {isOffline && (
          <OfflineIndicator>
            Modo Offline
          </OfflineIndicator>
        )}
        
        <UserActions>
          {isAuthenticated ? (
            <>
              <Button 
                variant="outline" 
                size="small" 
                onClick={handleLogout}
              >
                Cerrar Sesión
              </Button>
            </>
          ) : (
            <Button 
              variant="primary" 
              size="small" 
              onClick={() => {
                navigate('/login');
                setIsMenuOpen(false);
              }}
            >
              Iniciar Sesión
            </Button>
          )}
        </UserActions>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;