// src/pages/Login.jsx
import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../context/AuthContext';
import useAuth from '../hooks/useAuth';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

// Contenedor principal
const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: ${props => props.theme.spacing.xl};
  background-color: ${props => props.theme.colors.background};
`;

// Tarjeta de login
const LoginCard = styled.div`
  width: 100%;
  max-width: 450px;
  background-color: ${props => props.theme.colors.white};
  border-radius: ${props => props.theme.borderRadius.medium};
  box-shadow: ${props => props.theme.shadows.medium};
  padding: ${props => props.theme.spacing.xl};
`;

// Logo y título
const LogoContainer = styled.div`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const LogoTitle = styled.h1`
  font-family: ${props => props.theme.fonts.heading};
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Subtitle = styled.p`
  color: ${props => props.theme.colors.gray};
  font-size: ${props => props.theme.fontSizes.medium};
`;

// Formulario
const LoginForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

// Mensaje de error
const ErrorMessage = styled.div`
  background-color: ${props => props.theme.colors.errorLight};
  color: ${props => props.theme.colors.error};
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.small};
  margin-bottom: ${props => props.theme.spacing.md};
  text-align: center;
`;

// Enlaces adicionales
const LinksContainer = styled.div`
  text-align: center;
  margin-top: ${props => props.theme.spacing.lg};
  font-size: ${props => props.theme.fontSizes.small};
  
  a {
    color: ${props => props.theme.colors.primary};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { isAuthenticated } = useContext(AuthContext);
  
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Redirigir si ya está autenticado
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials((prev) => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validaciones básicas
    if (!credentials.email || !credentials.password) {
      setError('Por favor complete todos los campos');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const result = await login(credentials);
      
      if (result.success) {
        navigate('/');
      } else {
        setError(result.error || 'Error al iniciar sesión');
      }
    } catch (err) {
      setError('Error al conectar con el servidor');
      console.error('Error de login:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <LoginContainer>
      <LoginCard>
        <LogoContainer>
          <LogoTitle>Sistema Ecuestre APSAN</LogoTitle>
          <Subtitle>Acceso al sistema de calificación</Subtitle>
        </LogoContainer>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <LoginForm onSubmit={handleSubmit}>
          <Input
            id="email"
            name="email"
            label="Correo Electrónico"
            type="email"
            value={credentials.email}
            onChange={handleChange}
            placeholder="Ingrese su correo electrónico"
            fullWidth
            required
          />
          
          <Input
            id="password"
            name="password"
            label="Contraseña"
            type="password"
            value={credentials.password}
            onChange={handleChange}
            placeholder="Ingrese su contraseña"
            fullWidth
            required
          />
          
          <Button
            type="submit"
            variant="primary"
            size="large"
            fullWidth
            disabled={isLoading}
          >
            {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </Button>
        </LoginForm>
        
        <LinksContainer>
          <p>
            ¿Problemas para acceder? Contacte a <Link to="/contact">soporte técnico</Link>
          </p>
        </LinksContainer>
      </LoginCard>
    </LoginContainer>
  );
};

export default Login;