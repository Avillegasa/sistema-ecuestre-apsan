import React, { useContext } from 'react';
import styled from 'styled-components';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

// Contenedor principal
const SidebarContainer = styled.aside`
  background-color: ${props => props.theme.colors.white};
  box-shadow: ${props => props.theme.shadows.small};
  width: ${props => props.isCollapsed ? '80px' : '250px'};
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 50;
  transition: width ${props => props.theme.transitions.medium};
  display: flex;
  flex-direction: column;
  
  @media (max-width: ${props => props.theme.breakpoints.tablet}) {
    transform: translateX(${props => props.isOpen ? '0' : '-100%'});
    width: 250px;
    box-shadow: ${props => props.isOpen ? props.theme.shadows.large : 'none'};
  }
`;

// Cabecera del sidebar
const SidebarHeader = styled.div`
  padding: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  justify-content: ${props => props.isCollapsed ? 'center' : 'space-between'};
  border-bottom: 1px solid ${props => props.theme.colors.lightGray};
`;

// Logo de la aplicación
const Logo = styled(Link)`
  font-family: ${props => props.theme.fonts.heading};
  font-size: ${props => props.theme.fontSizes.large};
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  text-decoration: none;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`;

// Botón para colapsar el sidebar
const CollapseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: ${props => props.theme.fontSizes.large};
  color: ${props => props.theme.colors.gray};
  transition: color ${props => props.theme.transitions.fast};
  
  &:hover {
    color: ${props => props.theme.colors.text};
  }
`;

// Contenedor de la navegación
const NavContainer = styled.nav`
  flex: 1;
  padding: ${props => props.theme.spacing.md} 0;
  overflow-y: auto;
`;

// Lista de enlaces
const NavList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

// Elemento de la lista
const NavItem = styled.li`
  margin: ${props => props.theme.spacing.xs} 0;
`;

// Enlace de navegación
const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  font-family: ${props => props.theme.fonts.main};
  font-size: ${props => props.theme.fontSizes.medium};
  color: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.text};
  text-decoration: none;
  background-color: ${props => props.isActive ? 'rgba(41, 98, 255, 0.1)' : 'transparent'};
  border-left: 3px solid ${props => props.isActive ? props.theme.colors.primary : 'transparent'};
  transition: all ${props => props.theme.transitions.fast};
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
    color: ${props => props.theme.colors.primary};
  }
`;

// Icono en el enlace
const NavIcon = styled.span`
  font-size: ${props => props.theme.fontSizes.large};
  margin-right: ${props => props.isCollapsed ? '0' : props.theme.spacing.md};
  display: flex;
  align-items: center;
  justify-content: center;
  width: ${props => props.isCollapsed ? '100%' : 'auto'};
`;

// Texto del enlace
const NavText = styled.span`
  display: ${props => props.isCollapsed ? 'none' : 'block'};
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`;

// Información del usuario
const UserInfo = styled.div`
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.lightGray};
  display: flex;
  align-items: center;
  overflow: hidden;
`;

// Avatar del usuario
const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: ${props => props.theme.colors.primary};
  color: ${props => props.theme.colors.white};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
`;

// Detalles del usuario
const UserDetails = styled.div`
  margin-left: ${props => props.theme.spacing.md};
  overflow: hidden;
  display: ${props => props.isCollapsed ? 'none' : 'block'};
`;

// Nombre del usuario
const UserName = styled.div`
  font-weight: 600;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`;

// Rol del usuario
const UserRole = styled.div`
  font-size: ${props => props.theme.fontSizes.small};
  color: ${props => props.theme.colors.gray};
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`;

/**
 * Componente Sidebar para navegación lateral
 * 
 * @param {Object} props - Propiedades del componente
 * @param {boolean} [props.isOpen=false] - Si el sidebar está abierto (móvil)
 * @param {Function} props.toggleSidebar - Función para alternar el estado del sidebar
 * @param {boolean} [props.isCollapsed=false] - Si el sidebar está colapsado (escritorio)
 * @param {Function} props.toggleCollapse - Función para alternar el colapso del sidebar
 */
const Sidebar = ({ 
  isOpen = false, 
  toggleSidebar, 
  isCollapsed = false, 
  toggleCollapse 
}) => {
  const { isAuthenticated, user } = useContext(AuthContext);
  const location = useLocation();
  
  // Determinar si un enlace está activo
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  // Obtener iniciales del usuario
  const getUserInitials = () => {
    if (!user || !user.firstName) return '?';
    
    const initials = `${user.firstName.charAt(0)}${user.lastName ? user.lastName.charAt(0) : ''}`;
    return initials.toUpperCase();
  };
  
  // Obtener rol en español
  const getUserRole = () => {
    if (!user || !user.role) return '';
    
    const roles = {
      'admin': 'Administrador',
      'judge': 'Juez',
      'viewer': 'Visualizador'
    };
    
    return roles[user.role] || user.role;
  };
  
  return (
    <SidebarContainer isOpen={isOpen} isCollapsed={isCollapsed}>
      <SidebarHeader isCollapsed={isCollapsed}>
        {!isCollapsed && <Logo to="/">APSAN</Logo>}
        <CollapseButton onClick={toggleCollapse} aria-label="Colapsar sidebar">
          {isCollapsed ? '⟩' : '⟨'}
        </CollapseButton>
      </SidebarHeader>
      
      <NavContainer>
        <NavList>
          <NavItem>
            <NavLink to="/" isActive={isActive('/')}>
              <NavIcon isCollapsed={isCollapsed}>🏠</NavIcon>
              <NavText isCollapsed={isCollapsed}>Inicio</NavText>
            </NavLink>
          </NavItem>
          
          {isAuthenticated && (
            <>
              <NavItem>
                <NavLink to="/competitions" isActive={isActive('/competitions')}>
                  <NavIcon isCollapsed={isCollapsed}>🏆</NavIcon>
                  <NavText isCollapsed={isCollapsed}>Competencias</NavText>
                </NavLink>
              </NavItem>
              
              {user?.role === 'judge' && (
                <NavItem>
                  <NavLink to="/judge" isActive={isActive('/judge')}>
                    <NavIcon isCollapsed={isCollapsed}>📋</NavIcon>
                    <NavText isCollapsed={isCollapsed}>Panel de Juez</NavText>
                  </NavLink>
                </NavItem>
              )}
              
              <NavItem>
                <NavLink to="/rankings" isActive={isActive('/rankings')}>
                  <NavIcon isCollapsed={isCollapsed}>📊</NavIcon>
                  <NavText isCollapsed={isCollapsed}>Rankings</NavText>
                </NavLink>
              </NavItem>
              
              {user?.role === 'admin' && (
                <NavItem>
                  <NavLink to="/admin" isActive={isActive('/admin')}>
                    <NavIcon isCollapsed={isCollapsed}>⚙️</NavIcon>
                    <NavText isCollapsed={isCollapsed}>Administración</NavText>
                  </NavLink>
                </NavItem>
              )}
            </>
          )}
          
          {!isAuthenticated && (
            <NavItem>
              <NavLink to="/login" isActive={isActive('/login')}>
                <NavIcon isCollapsed={isCollapsed}>🔑</NavIcon>
                <NavText isCollapsed={isCollapsed}>Iniciar Sesión</NavText>
              </NavLink>
            </NavItem>
          )}
        </NavList>
      </NavContainer>
      
      {isAuthenticated && user && (
        <UserInfo>
          <UserAvatar>{getUserInitials()}</UserAvatar>
          <UserDetails isCollapsed={isCollapsed}>
            <UserName>{user.firstName} {user.lastName}</UserName>
            <UserRole>{getUserRole()}</UserRole>
          </UserDetails>
        </UserInfo>
      )}
    </SidebarContainer>
  );
};

export default Sidebar;